#!/usr/bin/env python3
"""
Subscribes to parc_msgs/TagVisit, decodes the JPEG with OpenCV and shows it.
Optionally saves each visit image to `save_dir` as tag_<id>.jpg.
"""
import os

import cv2
import numpy as np
import rclpy
from rclpy.node import Node

from parc_msgs.msg import TagVisit


class TagVisitViewer(Node):
    def __init__(self):
        super().__init__('tag_visit_viewer')

        self.declare_parameter('visit_topic', '/parc/tag_visit')
        self.declare_parameter('save_dir', '')  # empty = don't save

        self.save_dir = os.path.expanduser(self.get_parameter('save_dir').value)
        if self.save_dir:
            os.makedirs(self.save_dir, exist_ok=True)

        self.create_subscription(
            TagVisit, self.get_parameter('visit_topic').value, self.visit_cb, 10)

        # cv2.imshow needs waitKey() called regularly to refresh the windows
        self.create_timer(0.03, lambda: cv2.waitKey(1))

        self.get_logger().info("Waiting for tag visits...")

    def visit_cb(self, msg):
        buf = np.frombuffer(bytes(msg.image.data), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if img is None:
            self.get_logger().error(f"Could not decode image for tag {msg.tag_id}")
            return

        # --- Process the image with OpenCV here ---
        cv2.putText(img, f"Tag {msg.tag_id}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        cv2.imshow(f"Tag {msg.tag_id}", img)
        self.get_logger().info(f"Received visit image for tag {msg.tag_id} ({img.shape[1]}x{img.shape[0]})")

        if self.save_dir:
            path = os.path.join(self.save_dir, f"tag_{msg.tag_id}.jpg")
            cv2.imwrite(path, img)
            self.get_logger().info(f"Saved {path}")


def main(args=None):
    rclpy.init(args=args)
    node = TagVisitViewer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
