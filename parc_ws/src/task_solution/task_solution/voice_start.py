"""Voice start: say the start word ("go") and this node sends the StartSignal.

    ros2 run task_solution voice_start
    ros2 run task_solution voice_start --ros-args \
        -p model_path:=$HOME/ARCX6FINALREPO/models/vosk-model-small-en-us-0.15

How it meets the voice-start rules (PARC 2026 Real World brief):
  * Offline, on the robot, ReSpeaker mic: Vosk speech recognition on the /audio
    topic from respeaker_node. Nothing is sent over the network.
  * The robot must wait for the start word: this node never moves the robot. It
    only publishes /parc/start (through RefereeClient), and only while the referee
    is ARMED. tag_visitor only moves once the referee says RUNNING.
  * Crowd noise must not start it: the recogniser may only output the start word,
    a few sound-alike decoys ("no", "so", ...) or [unk]. An utterance counts only if
    it is the start word on its own ("go" or "go go"), recognised with at least
    min_conf confidence and, if min_rms is set, spoken loudly enough. Anything said
    before the run is ARMED is thrown away.
  * One start word is enough for the bonus; heard='go' marks it as a voice start.

If the voice start fails, start by typing:  ros2 run task_solution start_run

Second source (optional): source:=transcript listens to /speech/transcript from
stt_node instead. stt_node must then run OFFLINE (-p local_model:=base.en) and
with -p prompt:='' (its prompt-echo filter would otherwise drop a lone "Go.").

Needs (install during practice, so nothing downloads at run time), in the repo root
(the folder that contains parc_ws/):
    pip install --target <repo>/pydeps vosk
    model: vosk-model-small-en-us-0.15 (~40 MB), unzipped in <repo>/models/
Both are found automatically (no PYTHONPATH needed); model_path overrides the model.
"""

import json
import os
import queue
import re
import threading
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from parc_msgs.msg import RunStatus

from task_solution.referee import START_WORDS, STATE_NAMES, RefereeClient

try:
    from audio_common_msgs.msg import AudioData
except ImportError:                     # reported with a clear message in the node
    AudioData = None

# Repo root = the folder holding parc_ws/ (this file is parc_ws/src/task_solution/task_solution/).
# realpath follows the colcon --symlink-install links back to the source tree.
REPO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))))
_PYDEPS = [os.path.join(REPO_DIR, 'pydeps'), os.path.expanduser('~/ARCX6FINALREPO/pydeps')]
_MODELS = [os.path.join(REPO_DIR, 'models', 'vosk-model-small-en-us-0.15'),
           os.path.expanduser('~/ARCX6FINALREPO/models/vosk-model-small-en-us-0.15')]

try:
    import vosk
except ImportError:                     # not on PYTHONPATH: look in the team's pydeps folder
    import sys
    for _d in _PYDEPS:
        if os.path.isdir(os.path.join(_d, 'vosk')) and _d not in sys.path:
            sys.path.insert(0, _d)
    try:
        import vosk
    except ImportError:                 # only needed for source:=vosk
        vosk = None

SAMPLE_RATE = 16000                     # what the Vosk model is fed
# audio_format -> (numpy dtype, divisor that maps it to -1.0 .. 1.0)
SAMPLE_FORMATS = {
    'int16': ('<i2', 32768.0),
    'int32': ('<i4', 2147483648.0),
    'float32': ('<f4', 1.0),
}
# Words that sound like "go". Giving Vosk these as alternatives means a "no" or
# "so" from the crowd is recognised as itself instead of being forced into "go".
DEFAULT_DECOYS = ['no', 'so', 'oh', 'show', 'low', 'slow', 'stop', 'okay']


def clean(text):
    """Lowercase, strip punctuation, collapse spaces (for matching only)."""
    return re.sub(r'\s+', ' ', re.sub(r"[^a-z0-9' ]+", ' ', text.lower())).strip()


def only_start_word(text, word, max_repeats=2):
    """True if the text is the start word on its own ("go", "Go!", "go go")."""
    tokens = clean(text).split()
    return 0 < len(tokens) <= max_repeats and all(t == word for t in tokens)


def judge_vosk_result(result, word, min_conf):
    """Decide from one final Vosk result (a dict) whether it is a start.

    -> (accepted, reason). [unk] cleans to "unk", so any unknown speech in the
    utterance rejects it: "let's go" or crowd chatter around a "go" never counts."""
    text = result.get('text', '')
    if not clean(text):
        return False, 'empty'
    if not only_start_word(text, word):
        return False, f'not the start word on its own: "{text}"'
    confs = [float(w.get('conf', 0.0)) for w in result.get('result') or []
             if clean(w.get('word', '')) == word]
    if confs and min(confs) < min_conf:
        return False, f'confidence {min(confs):.2f} below {min_conf:.2f}'
    return True, 'ok'


class VoiceStart(Node):

    def __init__(self):
        super().__init__('voice_start')
        for name, default in [
                ('start_word', 'go'),               # go | allez | vai (one is enough)
                ('source', 'vosk'),                 # vosk | transcript
                ('model_path', next((m for m in _MODELS if os.path.isdir(m)), _MODELS[0])),
                ('decoy_words', DEFAULT_DECOYS),
                ('min_conf', 0.75),                 # Vosk word confidence, 0..1
                ('min_rms', 0.0),                   # 0 = off; else utterance must be this loud
                ('transcript_topic', '/speech/transcript'),
                # --- audio format of /audio (same parameters as stt_node) ---
                ('audio_topic', '/audio'),
                ('audio_sample_rate', 16000),
                ('audio_channels', 1),
                ('audio_channel', 0),
                ('audio_format', 'int16'),
                ('confirm_timeout_s', 3.0)]:        # RUNNING expected this soon after sending
            self.declare_parameter(name, default)
        p = lambda n: self.get_parameter(n).value   # noqa: E731

        self.word = clean(p('start_word'))
        if self.word not in START_WORDS:
            raise RuntimeError(f'start_word must be one of {START_WORDS}, not "{self.word}"')
        self.source = p('source')
        self.min_conf = float(p('min_conf'))
        self.min_rms = float(p('min_rms'))
        self.confirm_timeout = float(p('confirm_timeout_s'))

        self.referee = RefereeClient(self, on_status=self.on_status)
        self.fired = False
        self.fire_lock = threading.Lock()
        self.msg_count = 0

        if self.source == 'vosk':
            self.setup_vosk(p)
        elif self.source == 'transcript':
            self.create_subscription(String, p('transcript_topic'), self.on_transcript, 10)
            self.get_logger().info(
                f'Listening for "{self.word}" on {p("transcript_topic")} (stt_node must run '
                'with local_model set: the voice start must be offline).')
        else:
            raise RuntimeError('source must be "vosk" or "transcript"')
        self.get_logger().info(
            'Waiting for the referee to ARM the run; speech before that is ignored.')

    # ------------------------------------------------------------ vosk set-up
    def setup_vosk(self, p):
        if vosk is None:
            raise RuntimeError(
                'vosk is not installed: pip install --target <team folder>/pydeps vosk, '
                'then add that folder to PYTHONPATH')
        if AudioData is None:
            raise RuntimeError(
                'audio_common_msgs not found: sudo apt install ros-jazzy-audio-common-msgs')
        path = os.path.expanduser(p('model_path'))
        if not os.path.isdir(path):
            raise RuntimeError(
                f'Vosk model not found at {path}. Download vosk-model-small-en-us-0.15 '
                'during practice, unzip it there, or set -p model_path:=...')
        fmt = p('audio_format')
        if fmt not in SAMPLE_FORMATS:
            raise RuntimeError(f'audio_format must be one of {sorted(SAMPLE_FORMATS)}')
        self.np_dtype, self.scale = SAMPLE_FORMATS[fmt]
        self.in_rate = int(p('audio_sample_rate'))
        self.in_channels = max(1, int(p('audio_channels')))
        self.in_channel = int(p('audio_channel'))
        if not 0 <= self.in_channel < self.in_channels:
            raise RuntimeError('audio_channel must be between 0 and audio_channels-1')
        self.fast_path = (fmt == 'int16' and self.in_channels == 1
                          and self.in_rate == SAMPLE_RATE)

        vosk.SetLogLevel(-1)
        self.model = vosk.Model(path)
        decoys = [clean(w) for w in p('decoy_words') if clean(w) and clean(w) != self.word]
        self.grammar = json.dumps([self.word] + decoys + ['[unk]'])
        self.rec = None
        self.reset_requested = True         # fresh recogniser when the run is ARMED
        self.utt_peak = 0.0                 # loudest chunk in the current utterance

        self.chunks = queue.Queue(maxsize=400)
        self.audio_topic = p('audio_topic')
        self.create_subscription(
            AudioData, self.audio_topic, self.on_audio,
            QoSProfile(depth=50, reliability=ReliabilityPolicy.RELIABLE))
        self.watchdog = self.create_timer(5.0, self.check_audio)
        threading.Thread(target=self.vosk_loop, daemon=True).start()
        self.get_logger().info(
            f'Vosk model loaded from {path}; start word "{self.word}", '
            f'decoys {decoys}, min_conf {self.min_conf:.2f}.')

    def check_audio(self):
        self.watchdog.cancel()
        if self.msg_count == 0:
            self.get_logger().warn(
                f'No audio on {self.audio_topic} after 5 s. Is respeaker_node running? '
                f'Check: ros2 topic hz {self.audio_topic}')

    # --------------------------------------------------------- referee state
    @property
    def listening(self):
        return self.referee.state == RunStatus.ARMED and not self.fired

    def on_status(self, msg, old):
        if msg.state == old:
            return
        if msg.state == RunStatus.ARMED:
            self.fired = False
            if self.source == 'vosk':
                self.reset_requested = True     # forget anything heard before arming
            self.get_logger().info(f'ARMED: say "{self.word}" to start the run.')
        elif old == RunStatus.ARMED:
            self.get_logger().info(
                f'Referee is {STATE_NAMES.get(msg.state, msg.state)}: no longer listening.')

    # ----------------------------------------------------------- audio input
    def on_audio(self, msg):
        self.msg_count += 1
        if not self.listening:
            return                              # nothing before ARMED, nothing after start
        raw = bytes(msg.data)
        if self.fast_path:
            pcm = raw[:len(raw) // 2 * 2]
            level = float(np.sqrt(np.mean(np.square(
                np.frombuffer(pcm, '<i2').astype(np.float32) / 32768.0)))) if pcm else 0.0
        else:
            width = np.dtype(self.np_dtype).itemsize
            frame = width * self.in_channels
            usable = len(raw) // frame * frame
            if usable == 0:
                return
            x = np.frombuffer(raw[:usable], dtype=self.np_dtype)
            x = x.reshape(-1, self.in_channels)[:, self.in_channel].astype(np.float32)
            x /= self.scale
            if self.in_rate != SAMPLE_RATE:
                n_out = int(len(x) * SAMPLE_RATE / self.in_rate)
                if n_out < 1:
                    return
                x = np.interp(np.linspace(0, len(x) - 1, n_out),
                              np.arange(len(x)), x).astype(np.float32)
            level = float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
            pcm = (np.clip(x, -1.0, 1.0) * 32767).astype('<i2').tobytes()
        try:
            self.chunks.put_nowait((pcm, level))
        except queue.Full:
            pass                                # recogniser is behind: drop, like a live mic

    def vosk_loop(self):
        while rclpy.ok():
            try:
                pcm, level = self.chunks.get(timeout=0.2)
            except queue.Empty:
                continue
            if self.reset_requested or self.rec is None:
                self.rec = vosk.KaldiRecognizer(self.model, SAMPLE_RATE, self.grammar)
                self.rec.SetWords(True)
                self.reset_requested = False
                self.utt_peak = 0.0
            if not self.listening:
                continue
            self.utt_peak = max(self.utt_peak, level)
            if not self.rec.AcceptWaveform(pcm):
                continue                        # utterance not finished yet
            result = json.loads(self.rec.Result())
            peak, self.utt_peak = self.utt_peak, 0.0
            ok, why = judge_vosk_result(result, self.word, self.min_conf)
            if not clean(result.get('text', '')):
                continue
            if ok and self.min_rms > 0.0 and peak < self.min_rms:
                ok, why = False, f'too quiet (level {peak:.4f} < min_rms {self.min_rms:.4f})'
            self.get_logger().info(
                f'Heard "{result.get("text", "")}" (level {peak:.4f}): '
                + ('START' if ok else f'ignored, {why}'))
            if ok:
                self.fire()

    # ------------------------------------------------------- transcript input
    def on_transcript(self, msg):
        if not self.listening:
            return
        ok = only_start_word(msg.data, self.word)
        self.get_logger().info(
            f'Transcript "{msg.data}": ' + ('START' if ok else 'ignored, not the start word on its own'))
        if ok:
            self.fire()

    # ----------------------------------------------------------------- start
    def fire(self):
        with self.fire_lock:
            if not self.listening:
                return
            if self.referee.start_pub.get_subscription_count() == 0:
                self.get_logger().error(
                    'Start word heard, but no referee is listening on /parc/start. Not sending.')
                return
            self.fired = True
            if not self.referee.send_start(heard=self.word):
                self.get_logger().error(
                    'StartSignal was not sent. Start by typing: ros2 run task_solution start_run')
                return
        threading.Thread(target=self.confirm, daemon=True).start()

    def confirm(self):
        end = time.monotonic() + self.confirm_timeout
        while rclpy.ok() and time.monotonic() < end:
            if self.referee.state != RunStatus.ARMED:
                self.get_logger().info(
                    f'Referee is {STATE_NAMES.get(self.referee.state, self.referee.state)}. '
                    'Voice start done.')
                return
            time.sleep(0.1)
        self.get_logger().error(
            f'Referee still ARMED {self.confirm_timeout:.0f} s after the voice start. '
            'Start by typing: ros2 run task_solution start_run')


def main(args=None):
    rclpy.init(args=args)
    try:
        node = VoiceStart()
    except RuntimeError as e:
        print(e)
        rclpy.shutdown()
        return
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
