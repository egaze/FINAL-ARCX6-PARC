#!/usr/bin/env python3
"""
Waits for AprilTag detections. When a visible tag is within `visit_distance`
of the camera, grabs the latest camera frame, JPEG-encodes it and publishes
a parc_msgs/TagVisit on `visit_topic` (once per tag).
"""
import math

import cv2
import rclpy
from apriltag_msgs.msg import AprilTagDetectionArray
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import CompressedImage, Image
from tf2_ros import Buffer, TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

from parc_msgs.msg import TagVisit

TF_ERRORS = (LookupException, ConnectivityException, ExtrapolationException)


class TagVisitReporter(Node):
    def __init__(self):
        super().__init__('tag_visit_reporter')

        self.declare_parameter('image_topic', '/camera1/camera1/color/image_raw')
        self.declare_parameter('detections_topic', '/camera1/camera1/color/detections')
        self.declare_parameter('visit_topic', '/parc/tag_visit')
        self.declare_parameter('visit_tag_ids', [1, 4, 7, 9])
        self.declare_parameter('visit_distance', 0.5)   # metres, camera -> tag
        self.declare_parameter('tag_frame_prefix', 'tag_')
        self.declare_parameter('jpeg_quality', 90)

        self.visit_tag_ids = set(self.get_parameter('visit_tag_ids').value)
        self.visit_distance = float(self.get_parameter('visit_distance').value)
        self.tag_frame_prefix = self.get_parameter('tag_frame_prefix').value
        self.jpeg_quality = int(self.get_parameter('jpeg_quality').value)
        self.visit_topic = self.get_parameter('visit_topic').value

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.bridge = CvBridge()

        self.latest_image = None
        self.visited = set()

        self.create_subscription(Image, self.get_parameter('image_topic').value, self.image_cb, 10)
        self.create_subscription(
            AprilTagDetectionArray, self.get_parameter('detections_topic').value, self.detections_cb, 10)
        self.visit_pub = self.create_publisher(TagVisit, self.visit_topic, 10)

        self.get_logger().info(
            f"Waiting for tags {sorted(self.visit_tag_ids)} within {self.visit_distance} m "
            f"-> publishing to {self.visit_topic}"
        )

    def image_cb(self, msg):
        self.latest_image = msg

    def detections_cb(self, msg):
        # Camera frame comes from the detection header (same frame as the image)
        camera_frame = msg.header.frame_id

        for det in msg.detections:
            tag_id = det.id
            if tag_id not in self.visit_tag_ids or tag_id in self.visited:
                continue

            tag_frame = f'{self.tag_frame_prefix}{tag_id}'
            try:
                tf = self.tf_buffer.lookup_transform(camera_frame, tag_frame, Time())
            except TF_ERRORS:
                continue

            t = tf.transform.translation
            distance = math.sqrt(t.x ** 2 + t.y ** 2 + t.z ** 2)
            self.get_logger().info(
                f"Tag {tag_id} seen at {distance:.2f} m", throttle_duration_sec=1.0)

            if distance <= self.visit_distance:
                self.get_logger().info(
                    f"[WITHIN {self.visit_distance:.2f} m] Tag {tag_id} at {distance:.3f} m - taking picture")
                self.report_visit(tag_id)

    def report_visit(self, tag_id):
        if self.latest_image is None:
            self.get_logger().warn("No camera image received yet; cannot report visit.")
            return

        img = self.latest_image
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
        self.get_logger().info(f"[VISIT PUBLISHED] Tag {tag_id} -> {self.visit_topic}")


def main(args=None):
    rclpy.init(args=args)
    node = TagVisitReporter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
