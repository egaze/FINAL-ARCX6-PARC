"""Turn the depth cameras into an obstacle point cloud for Nav2.

    ros2 run task_solution depth_obstacles --ros-args -p use_sim_time:=true

Why: the lidar is 4 cm above the floor, so it only sees the base plate of a cafe
table (0.56 m square). The 0.91 m tabletop at 0.75 m overhangs it by ~0.18 m and
hits the robot body. This node projects each depth image into 3D, keeps points
between min_height and max_height above the floor (drops the floor itself),
removes points inside the robot's own outline, and publishes
/depth_obstacles/<camera> as PointCloud2 in base_footprint for the costmaps and
the collision monitor.
"""

import numpy as np
import rclpy
import tf2_ros
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo, Image, PointCloud2, PointField
from std_msgs.msg import Header

from task_solution.tag_mapper import quat_to_matrix


class DepthObstacles(Node):

    def __init__(self):
        super().__init__('depth_obstacles')
        self.declare_parameter('cameras', ['camera1', 'camera2'])
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('rate_hz', 5.0)
        self.declare_parameter('stride', 4)               # use every Nth pixel
        self.declare_parameter('min_range', 0.3)          # m (camera returns 0 below this)
        self.declare_parameter('max_range', 3.0)          # m (noise grows with distance^2)
        self.declare_parameter('min_height', 0.10)        # m above the floor: drops the floor
        self.declare_parameter('max_height', 1.25)        # m: robot is ~1.05 m tall
        # Robot outline in base_footprint (x forward, y left) plus a margin; points
        # inside are the robot itself.
        self.declare_parameter('self_box', [-0.35, 0.26, -0.28, 0.28])   # xmin, xmax, ymin, ymax

        g = lambda n: self.get_parameter(n).value  # noqa: E731
        self.base = g('base_frame')
        self.period = 1.0 / float(g('rate_hz'))
        self.stride = int(g('stride'))
        self.rmin, self.rmax = float(g('min_range')), float(g('max_range'))
        self.hmin, self.hmax = float(g('min_height')), float(g('max_height'))
        self.box = [float(v) for v in g('self_box')]

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.cams = {}
        for cam in g('cameras'):
            st = {'K': None, 'tf': None, 'last': None, 'rays': None,
                  'pub': self.create_publisher(PointCloud2, f'depth_obstacles/{cam}', 5)}
            self.cams[cam] = st
            self.create_subscription(
                CameraInfo, f'/{cam}/{cam}/depth/camera_info',
                lambda m, s=st: s.__setitem__('K', np.array(m.k).reshape(3, 3)) if s['K'] is None else None,
                qos_profile_sensor_data)
            self.create_subscription(
                Image, f'/{cam}/{cam}/depth/image_rect_raw',
                lambda m, s=st: self.on_depth(m, s), qos_profile_sensor_data)
        self.get_logger().info(
            f'Depth obstacles from {list(self.cams)}: {self.hmin:.2f}-{self.hmax:.2f} m high, '
            f'up to {self.rmax:.1f} m away.')

    def on_depth(self, msg, st):
        now = self.get_clock().now()
        if st['K'] is None or (st['last'] is not None
                               and (now - st['last']).nanoseconds * 1e-9 < self.period):
            return
        st['last'] = now
        if st['tf'] is None:      # camera is fixed to the robot: look the transform up once
            try:
                tf = self.tf_buffer.lookup_transform(self.base, msg.header.frame_id, Time(),
                                                     timeout=Duration(seconds=0.1))
            except tf2_ros.TransformException:
                return
            t = tf.transform.translation
            st['tf'] = (quat_to_matrix(tf.transform.rotation), np.array([t.x, t.y, t.z]))

        s = self.stride
        depth = np.frombuffer(msg.data, dtype=np.uint16).reshape(msg.height, msg.width)[::s, ::s]
        if st['rays'] is None or st['rays'][0].shape != depth.shape:
            K = st['K']
            v, u = np.mgrid[0:msg.height:s, 0:msg.width:s]
            st['rays'] = ((u - K[0, 2]) / K[0, 0], (v - K[1, 2]) / K[1, 1])
        z = depth.astype(np.float32) * 0.001                      # mm -> m (optical frame)
        ok = (z >= self.rmin) & (z <= self.rmax)
        z = z[ok]
        pts = np.stack([st['rays'][0][ok] * z, st['rays'][1][ok] * z, z], axis=1)
        R, t = st['tf']
        p = pts @ R.T + t                                          # -> base_footprint
        keep = (p[:, 2] >= self.hmin) & (p[:, 2] <= self.hmax)
        x0, x1, y0, y1 = self.box
        keep &= ~((p[:, 0] > x0) & (p[:, 0] < x1) & (p[:, 1] > y0) & (p[:, 1] < y1))
        p = p[keep].astype(np.float32)

        cloud = PointCloud2()
        cloud.header = Header(stamp=msg.header.stamp, frame_id=self.base)
        cloud.height, cloud.width = 1, len(p)
        cloud.fields = [PointField(name=n, offset=4 * i, datatype=PointField.FLOAT32, count=1)
                        for i, n in enumerate('xyz')]
        cloud.is_bigendian, cloud.point_step = False, 12
        cloud.row_step, cloud.is_dense = 12 * len(p), True
        cloud.data = p.tobytes()
        st['pub'].publish(cloud)


def main(args=None):
    rclpy.init(args=args)
    node = DepthObstacles()
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
