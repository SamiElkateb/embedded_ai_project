import collections
import contextlib
import sys
import wave
import webrtcvad
from os import path
from pydub import AudioSegment
import rate_converter

# Source: https://ngbala6.medium.com/audio-processing-and-remove-silence-using-python-a7fe1552007a

def __read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        print("sample_rate", sample_rate)
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def __write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def __frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def __vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])

def remove_silence(src: str, dest: str, strength: int):
    audio, sample_rate = __read_wave(src)
    vad = webrtcvad.Vad(strength)
    frames = __frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = __vad_collector(sample_rate, 30, 300, vad, frames)
    concataudio = [segment for segment in segments]
    joinedaudio = b"".join(concataudio)
    __write_wave(dest, joinedaudio, sample_rate)


def __main(args):
    if "mp3" in args[1]:
        # absolute_path = path.dirname(__file__)
        # relative_path = args[1]
        # full_path = path.join(absolute_path, relative_path)
        src = args[1]
        rate_converter.convert(src, src.replace(".mp3", ".wav"))
        args[1] = src.replace(".mp3", ".wav")

    if len(args) != 2:
        sys.stderr.write(
            'Usage: silenceremove.py <aggressiveness> <path to wav file>\n')
        sys.exit(1)
    audio, sample_rate = __read_wave(args[1])
    vad = webrtcvad.Vad(int(args[0]))
    frames = __frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = __vad_collector(sample_rate, 30, 300, vad, frames)

    # Segmenting the Voice audio and save it in list as bytes
    concataudio = [segment for segment in segments]

    joinedaudio = b"".join(concataudio)

    __write_wave("Non-Silenced-Audio.wav", joinedaudio, sample_rate)

if __name__ == '__main__':
    __main(sys.argv[1:])
