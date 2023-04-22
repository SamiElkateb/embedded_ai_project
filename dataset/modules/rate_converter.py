from pydub import AudioSegment
import sys
from os import path

def convert(src: str, dest: str):
    sound = AudioSegment.from_file(src)
    sound = sound.set_frame_rate(16000)
    sound = sound.set_channels(1)
    sound = sound.set_sample_width(2)
    sound.export(dest, format ="wav")

def __main(args):
    absolute_path = path.dirname(__file__)
    src = args[0]
    dest = args[1]
    full_src = path.join(absolute_path, src)
    full_dest = path.join(absolute_path, dest)
    convert(full_src, full_dest)

if __name__ == '__main__':
    if len(sys.argv[1:]) != 2:
        sys.stderr.write(
            'Usage: rate_converter.py <src file> <dest file>\n')
        sys.exit(1)
    __main(sys.argv[1:])
