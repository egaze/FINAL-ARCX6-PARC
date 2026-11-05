#!/usr/bin/env python3
"""
Tag manager: one node that, for every AprilTag detection,
  1. logs the tag's pose in the world frame (map) to a YAML file, and
  2. when the tag is within `visit_distance` of the camera, takes a picture
     and publishes a parc_msgs/TagVisit on `visit_topic` (once per tag).

Replaces tag_logger.py + tag_visit_reporter.py.

Every detection is cross-checked before it is used:
  * family must be AprilTag 36h11 (the competition family),
  * hamming (corrected bits) <= max_hamming (0 = exact code only),
  * decision_margin >= min_decision_margin (rejects weak / blurred decodes),
  * id must be one of the competition tags,
  * the same id must pass in min_consecutive frames in a row.

TagVisit publishing is OFF by default (publish_visits): during a scored run
task_solution/tag_visitor reports visits through RefereeClient, which also checks
that the run is RUNNING and that the robot is stopped in the visit pose.
"""
import math
import os

import cv2
import rclpy
import yaml
from apriltag_msgs.msg import AprilTagDetectionArray
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import CompressedImage, Image
from tf2_ros import Buffer, TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

from parc_msgs.msg import TagVisit

TF_ERRORS = (LookupException, ConnectivityException, ExtrapolationException)


class TagManager(Node):
    def __init__(self):
        super().__init__('tag_manager')

        # ---------------- Parameters ----------------
        self.declare_parameter('detections_topic', '/camera1/camera1/color/detections')
        self.declare_parameter('image_topic', '/camera1/camera1/color/image_raw')
        self.declare_parameter('visit_topic', '/parc/tag_visit')
        self.declare_parameter('reference_frame', 'map')      # world frame for logged coordinates
        self.declare_parameter('tag_frame_prefix', 'tag_')
        self.declare_parameter('map_tag_ids', [1, 4, 7, 9])  # tags whose world pose is logged
        self.declare_parameter('visit_tag_ids', [1, 4, 7, 9])   # tags that get a TagVisit
        self.declare_parameter('visit_distance', 0.5)           # metres, camera -> tag
        self.declare_parameter('jpeg_quality', 90)
        self.declare_parameter('tag_family', '36h11')
        self.declare_parameter('max_hamming', 0)
        self.declare_parameter('min_decision_margin', 25.0)
        self.declare_parameter('min_consecutive', 3)
        self.declare_parameter('publish_visits', False)
        self.declare_parameter(
            'output_file',
            '~/ARCX6FINALREPO/FINAL-ARCX6-PARC/parc_ws/src/parcbot_docking/src/mapped_tag_world_coordinates.yaml')

        p = lambda name: self.get_parameter(name).value
        self.reference_frame = p('reference_frame')
        self.tag_frame_prefix = p('tag_frame_prefix')
        self.map_tag_ids = set(p('map_tag_ids'))
        self.visit_tag_ids = set(p('visit_tag_ids'))
        self.visit_distance = float(p('visit_distance'))
        self.jpeg_quality = int(p('jpeg_quality'))
        self.visit_topic = p('visit_topic')
        self.output_file = os.path.expanduser(p('output_file'))
        self.tag_family = p('tag_family')
        self.max_hamming = int(p('max_hamming'))
        self.min_margin = float(p('min_decision_margin'))
        self.min_consecutive = int(p('min_consecutive'))
        self.publish_visits = bool(p('publish_visits'))
        self.streak = {}
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        # ---------------- State ----------------
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.bridge = CvBridge()
        self.latest_image = None
        self.mapped_tags = {}
        self.visited = set()
        self.dirty = False  # file needs saving

        # ---------------- ROS interfaces ----------------
        self.create_subscription(Image, p('image_topic'), self.image_cb, 10)
        self.create_subscription(AprilTagDetectionArray, p('detections_topic'), self.detections_cb, 10)
        self.visit_pub = self.create_publisher(TagVisit, self.visit_topic, 10)
        self.create_timer(1.0, self.save_if_dirty)

        self.get_logger().info(
            f"Tag manager ready | mapping {sorted(self.map_tag_ids)} in '{self.reference_frame}' "
            f"-> {self.output_file} | visits for {sorted(self.visit_tag_ids)} within "
            f"{self.visit_distance} m -> {self.visit_topic}")

    # ---------------------------------------------------------------
    def image_cb(self, msg):
        self.latest_image = msg

    def valid(self, det):
        """True if the detection is a clean decode of one of our 36h11 tags."""
        family = det.family.replace('tag', '')          # apriltag_ros reports "36h11" or "tag36h11"
        reasons = []
        if family != self.tag_family:
            reasons.append(f"family {det.family}")
        if det.hamming > self.max_hamming:
            reasons.append(f"hamming {det.hamming}")
        if det.decision_margin < self.min_margin:
            reasons.append(f"margin {det.decision_margin:.0f}")
        if det.id not in self.map_tag_ids | self.visit_tag_ids:
            reasons.append("not a competition tag")
        if reasons:
            self.get_logger().warn(f"Rejected detection id {det.id}: {', '.join(reasons)}",
                                   throttle_duration_sec=2.0)
            return False
        return True

    def detections_cb(self, msg):
        camera_frame = msg.header.frame_id
        good = [d for d in msg.detections if self.valid(d)]
        seen = {d.id for d in good}
        for tag_id in list(self.streak):
            if tag_id not in seen:
                self.streak[tag_id] = 0
        for det in good:
            tag_id = det.id
            self.streak[tag_id] = self.streak.get(tag_id, 0) + 1
            if self.streak[tag_id] < self.min_consecutive:
                continue
            tag_frame = f'{self.tag_frame_prefix}{tag_id}'

            if tag_id in self.map_tag_ids:
                self.log_world_pose(tag_id, tag_frame)

            if (self.publish_visits and tag_id in self.visit_tag_ids
                    and tag_id not in self.visited):
                self.check_visit(tag_id, tag_frame, camera_frame)

    # ---------------- 1. World pose logging ----------------
    def log_world_pose(self, tag_id, tag_frame):
        try:
            tf = self.tf_buffer.lookup_transform(self.reference_frame, tag_frame, Time())
        except TF_ERRORS as e:
            self.get_logger().warn(
                f"No '{self.reference_frame}' -> {tag_frame} transform yet: {e}", throttle_duration_sec=5.0)
            return

        t, q = tf.transform.translation, tf.transform.rotation
        self.mapped_tags[str(tag_id)] = {
            "id": tag_id,
            "reference_frame": self.reference_frame,
            "position": {"x": t.x, "y": t.y, "z": t.z},
            "orientation": {"x": q.x, "y": q.y, "z": q.z, "w": q.w},
            "visited": tag_id in self.visited,
        }
        self.dirty = True
        self.get_logger().info(
            f"[MAPPED] Tag {tag_id} -> X: {t.x:.3f}, Y: {t.y:.3f}, Z: {t.z:.3f}", throttle_duration_sec=2.0)

    def save_if_dirty(self):
        if not self.dirty:
            return
        try:
            with open(self.output_file, 'w') as f:
                yaml.safe_dump(self.mapped_tags, f, default_flow_style=False, sort_keys=False)
            self.dirty = False
        except Exception as e:
            self.get_logger().error(f"Failed to save {self.output_file}: {e}")

    # ---------------- 2. Visit reporting ----------------
    def check_visit(self, tag_id, tag_frame, camera_frame):
        try:
            tf = self.tf_buffer.lookup_transform(camera_frame, tag_frame, Time())
        except TF_ERRORS:
            return

        t = tf.transform.translation
        distance = math.sqrt(t.x ** 2 + t.y ** 2 + t.z ** 2)
        self.get_logger().info(f"Tag {tag_id} seen at {distance:.2f} m", throttle_duration_sec=1.0)

        if distance <= self.visit_distance:
            self.get_logger().info(
                f"[WITHIN {self.visit_distance:.2f} m] Tag {tag_id} at {distance:.3f} m - taking picture")
            self.publish_visit(tag_id)

    def publish_visit(self, tag_id):
        img = self.latest_image
        if img is None:
            self.get_logger().warn("No camera image received yet; cannot report visit.")
            return
        try:
            cv_image = self.bridge.imgmsg_to_cv2(img, desired_encoding='bgr8')
            ok, jpeg = cv2.imencode('.jpg', cv_image, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        except Exception as e:
            self.get_logger().error(f"Image encoding failed: {e}")
            return
        if not ok:
            self.get_logger().error("JPEG encoding failed")
            return

        visit = TagVisit()
        visit.header.stamp = self.get_clock().now().to_msg()
        visit.header.frame_id = img.header.frame_id
        visit.tag_id = tag_id
        visit.image = CompressedImage(header=img.header, format='jpeg', data=jpeg.tobytes())
        self.visit_pub.publish(visit)

        self.visited.add(tag_id)
        if str(tag_id) in self.mapped_tags:
            self.mapped_tags[str(tag_id)]["visited"] = True
            self.dirty = True
        self.get_logger().info(f"[VISIT PUBLISHED] Tag {tag_id} -> {self.visit_topic}")


def main(args=None):
    rclpy.init(args=args)
    node = TagManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.save_if_dirty()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
