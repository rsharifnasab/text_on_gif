#!/usr/bin/python3

from argparse import ArgumentParser
from sys import stdin, stdout
import os
from PIL import Image, ImageSequence


# todo: replace eith argparse.FileType
# https://docs.python.org/3/library/argparse.html#argparse.FileType
def open_file_to_read(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
        return None
    else:
        return open(arg, 'rb') if isinstance(arg, str) else arg


def open_file_to_write(parser, arg):
    return open(arg, 'wb') if isinstance(arg, str) else arg


def load_gif_frames(inp_file):
    return ImageSequence.Iterator(Image.open(inp_file))


def save_gif(frames, out_file):
    frames[0].save(out_file,
                   save_all=True,
                   format="GIF",
                   append_imgaes=frames[1:],
                   optimize=False)


i = 0


def frame_write_gen(t):
    def inner(frame):
        global i
        print(f"frame #{i}")
        i += 1
        return frame
    return inner


def write_on_gif(inp_file, out_file, text):
    inp_frames = load_gif_frames(inp_file)
    print("load complete")

    write_on_frame = frame_write_gen(text)

    out_frames = [write_on_frame(frame) for frame in inp_frames]

    save_gif(out_frames, out_file)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="main.py",
        description="add text to gif image",
        epilog="originally made for someone special :)"
    )
    parser.add_argument("-t", "--text", type=str, required=True,
                        help="your text to be added on gif")
    parser.add_argument("-i", "--input", dest="input_file",
                        help="input gif as base file",
                        metavar="FILE",
                        type=lambda x: open_file_to_read(parser, x),
                        default=stdin.buffer)

    parser.add_argument("-o", "--output", dest="output_file",
                        help="where to save result gif",
                        metavar="FILE",
                        type=lambda x: open_file_to_write(parser, x),
                        default=stdout.buffer)

    conf = parser.parse_args()
    print(conf.input_file)
    print(conf.output_file)

    write_on_gif(conf.input_file, conf.output_file, conf.text)
