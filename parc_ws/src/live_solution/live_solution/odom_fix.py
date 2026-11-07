"""Corrected wheel odometry for SLAM: turning scaled by `yaw_scale`.

    ros2 run live_solution odom_fix --ros-args -p yaw_scale:=1.096

Measured in the simulator (3 spins in place): odometry reported 1080 deg, the robot
really turned 1184 deg, so odometry under-reports rotation by ~9.6 %. Every scan spin
then put SLAM ~35 deg off, the live map twisted and the planner found no routes.

This node re-integrates /botwheel_explorer/odom with rotation x yaw_scale and publishes
the result as a NEW frame, `odom_fixed`, without touching the existing tree:

    map -> odom_fixed -> odom -> base_footprint
          (SLAM)      (this node: corrected * raw^-1)   (robot/Gazebo)

so map -> base_footprint follows the corrected odometry. SLAM uses odom_frame:=odom_fixed.
On the real robot, measure the factor the same way (or keep 1.0).
"""

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


class OdomFix(Node):

    def __init__(self):
        super().__init__('odom_fix')
        self.declare_parameter('yaw_scale', 1.0)
        self.declare_parameter('odom_topic', '/botwheel_explorer/odom')
        self.declare_parameter('raw_frame', 'odom')
        self.declare_parameter('fixed_frame', 'odom_fixed')
        g = lambda n: self.get_parameter(n).value  # noqa: E731
        self.scale = float(g('yaw_scale'))
        self.raw_frame, self.fixed_frame = g('raw_frame'), g('fixed_frame')
        self.prev = None                     # previous raw pose (x, y, yaw)
        self.fx = self.fy = self.fyaw = 0.0  # corrected pose
        self.br = TransformBroadcaster(self)
        self.create_subscription(Odometry, g('odom_topic'), self.on_odom, 50)
        self.get_logger().info(f'Odometry rotation x {self.scale:.3f} -> frame {self.fixed_frame}')

    def on_odom(self, m):
        q = m.pose.pose.orientation
        rx, ry = m.pose.pose.position.x, m.pose.pose.position.y
        ryaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        if self.prev is None:
            self.prev = (rx, ry, ryaw)
            self.fx, self.fy, self.fyaw = rx, ry, ryaw
        px, py, pyaw = self.prev
        # raw step expressed in the robot frame at the previous raw pose
        c, s = math.cos(pyaw), math.sin(pyaw)
        lx = c * (rx - px) + s * (ry - py)
        ly = -s * (rx - px) + c * (ry - py)
        dyaw = wrap(ryaw - pyaw) * self.scale
        mid = self.fyaw + dyaw / 2
        self.fx += math.cos(mid) * lx - math.sin(mid) * ly
        self.fy += math.sin(mid) * lx + math.cos(mid) * ly
        self.fyaw = wrap(self.fyaw + dyaw)
        self.prev = (rx, ry, ryaw)
        # odom_fixed -> odom = corrected * raw^-1
        d = wrap(self.fyaw - ryaw)
        cd, sd = math.cos(d), math.sin(d)
        tx = self.fx - (cd * rx - sd * ry)
        ty = self.fy - (sd * rx + cd * ry)
        t = TransformStamped()
        t.header.stamp = m.header.stamp
        t.header.frame_id = self.fixed_frame
        t.child_frame_id = self.raw_frame
        t.transform.translation.x, t.transform.translation.y = tx, ty
        t.transform.rotation.z, t.transform.rotation.w = math.sin(d / 2), math.cos(d / 2)
        self.br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = OdomFix()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
