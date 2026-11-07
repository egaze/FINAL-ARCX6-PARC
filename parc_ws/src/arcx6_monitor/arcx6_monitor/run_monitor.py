"""ARCX6 run monitor: logs what the solution sees, knows and does. Read-only.

    ros2 run arcx6_monitor run_monitor                     # robot (or the laptop, same ROS_DOMAIN_ID)
    ros2 run arcx6_monitor run_monitor --ros-args -p use_sim_time:=true    # simulation

It subscribes only (publishes nothing, never drives) and prints:
  * events as they happen: a camera starts/stops seeing a tag (id, distance, decode
    quality), the solution found / reported / forgot a tag or changed target, referee state
    changes, Nav2 goals starting and ending, collision-monitor interventions, and every
    warning/error of the solution node;
  * a status block every `period` s: run state and clock, order, reported, tags known to
    the solution, tags in view now, robot pose, wheel command, collision monitor, Nav2.
Everything is also written to ~/arcx6_logs/monitor_<date>_<time>.log (`log_dir`).

Sources: /cameraN/cameraN/color/detections (both cameras; whichever sees tags is the one
in use), the tag_N TF frames from apriltag_ros, /rosout of the solution node (`watch_nodes`),
/parc/run_status, TF map -> robot, the wheel command topics, /collision_monitor_state and
/navigate_to_pose/_action/status.
"""

import math
import os
import re
import time

import rclpy
import tf2_ros
from action_msgs.msg import GoalStatus, GoalStatusArray
from apriltag_msgs.msg import AprilTagDetectionArray
from geometry_msgs.msg import Twist, TwistStamped
from nav2_msgs.msg import CollisionMonitorState
from parc_msgs.msg import RunStatus
from rcl_interfaces.msg import Log
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from rclpy.time import Time

RUN_STATES = {0: 'IDLE', 1: 'ARMED', 2: 'RUNNING', 3: 'FINISHED', 4: 'TIMED_OUT', 5: 'TERMINATED'}
CM_ACTIONS = {0: 'free', 1: 'STOP', 2: 'SLOWDOWN', 3: 'APPROACH', 4: 'LIMIT'}
GOAL_STATES = {GoalStatus.STATUS_ACCEPTED: 'accepted', GoalStatus.STATUS_EXECUTING: 'executing',
               GoalStatus.STATUS_CANCELING: 'canceling', GoalStatus.STATUS_SUCCEEDED: 'succeeded',
               GoalStatus.STATUS_CANCELED: 'canceled', GoalStatus.STATUS_ABORTED: 'aborted'}
LOG_LEVELS = {10: 'DEBUG', 20: 'INFO', 30: 'WARN', 40: 'ERROR', 50: 'FATAL'}
LATCHED = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                     durability=DurabilityPolicy.TRANSIENT_LOCAL)

# INFO lines of the solution worth showing as events (warnings/errors are always shown)
INTERESTING = re.compile(
    r'Run started|Run done|Opening|Found tag|Reported tag|seen at|in view|aligning|'
    r'within the rules|camera-to-tag|Looking for tag|driving to the approach|sweep point|'
    r'heading there|spotted|forgetting|Pose:|Own velocity|Waiting for')


class RunMonitor(Node):

    def __init__(self):
        super().__init__('arcx6_monitor')
        self.declare_parameter('cameras', ['camera1', 'camera2'])
        self.declare_parameter('watch_nodes', ['tag_visitor', 'tag_tracker'])
        self.declare_parameter('period', 2.0)
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_frames', ['base_link', 'base_footprint'])
        self.declare_parameter('log_dir', os.path.expanduser('~/arcx6_logs'))
        self.declare_parameter('lost_after_s', 2.0)       # tag counts as out of view after this
        g = lambda n: self.get_parameter(n).value  # noqa: E731

        d = g('log_dir')
        os.makedirs(d, exist_ok=True)
        self.path = os.path.join(d, time.strftime('monitor_%Y%m%d_%H%M%S.log'))
        self.file = open(self.path, 'a', buffering=1)

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.watch = set(g('watch_nodes'))
        self.lost_after = float(g('lost_after_s'))

        self.in_view = {}          # (camera, tag) -> dict(t, dist, margin, hamming)
        self.det_rate = {}         # camera -> detection messages since last status
        self.known = {}            # tag -> 'x, y' text, from the solution's log
        self.known_list = None     # last 'Known: [...]' list the solution printed
        self.reported_sol = []     # 'Reported tag N' lines
        self.target = None
        self.run = None            # last RunStatus
        self.cmd = {}              # topic -> (t, vx, wz)
        self.cm = None
        self.nav = {}              # goal id -> status
        self.sol_seen = 0.0
        self.last_line = ''

        for cam in g('cameras'):
            self.create_subscription(
                AprilTagDetectionArray, f'/{cam}/{cam}/color/detections',
                lambda m, cam=cam: self.on_detections(cam, m), qos_profile_sensor_data)
        self.create_subscription(Log, '/rosout', self.on_rosout, 200)
        self.create_subscription(RunStatus, '/parc/run_status', self.on_run_status, LATCHED)
        self.create_subscription(TwistStamped, '/botwheel_explorer/cmd_vel',
                                 lambda m: self.on_cmd('/botwheel_explorer/cmd_vel', m.twist), 20)
        self.create_subscription(Twist, '/cmd_vel', lambda m: self.on_cmd('/cmd_vel', m), 20)
        self.create_subscription(CollisionMonitorState, '/collision_monitor_state', self.on_cm, 10)
        self.create_subscription(GoalStatusArray, '/navigate_to_pose/_action/status', self.on_nav, 10)
        self.create_timer(float(g('period')), self.status)
        self.create_timer(0.5, self.check_lost)
        self.out(f'ARCX6 run monitor started (read-only). Log file: {self.path}')

    # ------------------------------------------------------------------ output
    def out(self, text, level='INFO'):
        line = f'{time.strftime("%H:%M:%S")} {text}'
        self.file.write(line + '\n')
        if level == 'WARN':
            self.get_logger().warn(text)
        elif level == 'ERROR':
            self.get_logger().error(text)
        else:
            self.get_logger().info(text)

    # ------------------------------------------------------------------ inputs
    def tag_distance(self, frame, tag):
        try:
            tf = self.tf_buffer.lookup_transform(frame, f'tag_{tag}', Time())
        except tf2_ros.TransformException:
            return None
        t = tf.transform.translation
        return math.sqrt(t.x * t.x + t.y * t.y + t.z * t.z)

    def on_detections(self, cam, msg):
        self.det_rate[cam] = self.det_rate.get(cam, 0) + 1
        now = time.monotonic()
        for d in msg.detections:
            key = (cam, int(d.id))
            dist = self.tag_distance(msg.header.frame_id, int(d.id))
            new = key not in self.in_view
            self.in_view[key] = dict(t=now, dist=dist, margin=float(d.decision_margin),
                                     hamming=int(d.hamming))
            if new:
                ds = f'{dist:.2f} m' if dist is not None else 'distance ?'
                self.out(f'[CAMERA] {cam} now sees tag {d.id} ({ds}, decode margin '
                         f'{d.decision_margin:.0f}, hamming {d.hamming})')

    def check_lost(self):
        now = time.monotonic()
        for key in [k for k, v in self.in_view.items() if now - v['t'] > self.lost_after]:
            del self.in_view[key]
            self.out(f'[CAMERA] {key[0]} lost tag {key[1]}')

    def on_rosout(self, m):
        if m.name not in self.watch:
            return
        self.sol_seen = time.monotonic()
        text = m.msg
        f = re.search(r'Found tag (\d+) at \(([-\d.]+), ([-\d.]+)\)', text)
        if f:
            self.known[int(f.group(1))] = f'({f.group(2)}, {f.group(3)})'
        f = re.search(r'Tag (\d+) seen at [\d.]+ m -> stored at \(([-\d.]+), ([-\d.]+)\)', text)
        if f:                                          # tag_tracker
            self.known[int(f.group(1))] = f'({f.group(2)}, {f.group(3)})'
        f = re.search(r'[Kk]nown: \[([\d, ]*)\]', text)
        if f:
            self.known_list = [int(x) for x in f.group(1).replace(',', ' ').split()]
        f = re.search(r'Reported tag (\d+)', text)
        if f:
            self.reported_sol.append(int(f.group(1)))
        f = re.search(r'Tag (\d+): .*(forgetting|not at its remembered spot)', text)
        if f:
            self.known.pop(int(f.group(1)), None)
        f = re.search(r'(?:Looking for tag|Tag) (\d+)[: ]', text)
        if f and re.search(r'Looking for|driving to|navigating|approaching|aligning|going to', text):
            t = int(f.group(1))
            if t != self.target:
                self.target = t
                self.out(f'[TARGET] solution is now working on tag {t}')
        level = LOG_LEVELS.get(m.level, str(m.level))
        if level in ('WARN', 'ERROR', 'FATAL') or INTERESTING.search(text):
            if text != self.last_line:
                self.last_line = text
                self.out(f'[{m.name}] {text}', 'WARN' if level == 'WARN' else
                         'ERROR' if level in ('ERROR', 'FATAL') else 'INFO')

    def on_run_status(self, m):
        old = self.run
        self.run = m
        if old is None or old.state != m.state:
            self.out(f'[REFEREE] {RUN_STATES.get(m.state, m.state)}  order {list(m.tag_order)}'
                     f'{"  FALSE START" if m.false_start else ""}')
        if old is not None and list(old.tags_reported) != list(m.tags_reported):
            self.out(f'[REFEREE] tags reported so far: {list(m.tags_reported)}  '
                     f'(at {m.elapsed_s:.0f} s)')

    def on_cmd(self, topic, tw):
        self.cmd[topic] = (time.monotonic(), tw.linear.x, tw.angular.z)

    def on_cm(self, m):
        a = CM_ACTIONS.get(m.action_type, str(m.action_type))
        if self.cm != a:
            self.out(f'[SAFETY] collision monitor: {a}{" (" + m.polygon_name + ")" if m.polygon_name else ""}')
        self.cm = a

    def on_nav(self, m):
        for s in m.status_list:
            gid = bytes(s.goal_info.goal_id.uuid).hex()[:6]
            st = GOAL_STATES.get(s.status, str(s.status))
            if self.nav.get(gid) != st:
                self.nav[gid] = st
                if st in ('executing', 'succeeded', 'aborted', 'canceled'):
                    self.out(f'[NAV2] goal {gid}: {st}')
        if len(self.nav) > 30:
            self.nav = dict(list(self.nav.items())[-10:])

    # ------------------------------------------------------------------ status
    def pose(self):
        for base in self.get_parameter('base_frames').value:
            for frame in (self.get_parameter('map_frame').value, 'odom'):
                try:
                    tf = self.tf_buffer.lookup_transform(frame, base, Time())
                except tf2_ros.TransformException:
                    continue
                t, q = tf.transform.translation, tf.transform.rotation
                yaw = math.degrees(math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)))
                return f'({t.x:.2f}, {t.y:.2f}) {yaw:.0f} deg in {frame}'
        return 'unknown (no TF)'

    def status(self):
        now = time.monotonic()
        r = self.run
        if r is not None:
            run = (f'{RUN_STATES.get(r.state, r.state)} {r.elapsed_s:.0f}/{r.time_limit_s:.0f} s, '
                   f'order {list(r.tag_order)}, reported {list(r.tags_reported)}')
        else:
            run = 'no referee status yet'
        view = ', '.join(f'{t}@{c}' + (f' {v["dist"]:.1f}m' if v['dist'] is not None else '')
                         for (c, t), v in sorted(self.in_view.items(), key=lambda kv: kv[0][1])) or 'none'
        cams = ', '.join(f'{c} {n / float(self.get_parameter("period").value):.0f} Hz'
                         for c, n in sorted(self.det_rate.items())) or 'no detector output'
        self.det_rate = {}
        known = (', '.join(f'{t} {xy}' for t, xy in sorted(self.known.items()))
                 if self.known else (str(self.known_list) if self.known_list else 'none'))
        cmds = []
        for topic, (t, vx, wz) in self.cmd.items():
            if now - t < 1.0:
                cmds.append(f'{topic} v={vx:.2f} w={wz:.2f}')
        nav_active = [g for g, s in self.nav.items() if s in ('accepted', 'executing', 'canceling')]
        sol = 'alive' if now - self.sol_seen < 15.0 else 'NO LOG from solution in 15 s'
        self.out('[STATUS] ' + ' | '.join([
            f'run: {run}',
            f'target: {self.target if self.target is not None else "-"}',
            f'known: {known}',
            f'in view: {view} ({cams})',
            f'robot: {self.pose()}',
            f'wheels: {"; ".join(cmds) if cmds else "no command"}',
            f'safety: {self.cm or "-"}',
            f'nav2: {"goal " + nav_active[-1] if nav_active else "idle"}',
            f'solution: {sol}']))

    def destroy_node(self):
        try:
            self.file.close()
        finally:
            super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = RunMonitor()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
