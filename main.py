#!/usr/bin/python3

from argparse import ArgumentParser
from sys import stdin, stdout, stderr
from math import tan, atan, degrees, radians, sin, cos, sqrt, isclose
import os
from PIL import Image, ImageSequence
from PIL import ImageFont, ImageDraw, ImageOps


# todo: replace eith argparse.FileType
# https://docs.python.org/3/library/argparse.html#argparse.FileType
def open_file_to_read(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
        return None
    elif not isinstance(arg, str):  # stdin default
        return arg
    elif ".gif" not in arg:  # convert with ffmpeg
        print("inp is not gif, trying to convert", file=stderr)
        converted_inp = f"{arg}.gif"
        os.system(f"ffmpeg -i {arg} -y  {converted_inp}")
        return open(converted_inp, 'rb')
    else:
        return open(arg, 'rb')


def open_file_to_write(parser, arg):
    return open(arg, 'wb') if isinstance(arg, str) else arg


def load_gif_frames(inp_file):
    return ImageSequence.Iterator(Image.open(inp_file))


def save_gif(frames, out_file):
    frames[0].save(out_file,
                   save_all=True,
                   format="GIF",
                   append_images=frames[1:],
                   optimize=False,
                   duration=70,
                   loop=0
                   )
    out_file.close()


def create_text_image(text, font, color):
    txt = Image.new('RGBA', font.getsize(text), (255, 255, 250, 70))
    dr = ImageDraw.Draw(txt)
    dr.text((0, 0), text, color, font=font)
    return txt


def calculate_rotation_angle(text_ratio, text_start, text_end):
    init_tilt = text_ratio
    rotated_tilt = (text_end[1] - text_start[1])/(text_end[0]-text_start[0])
    return degrees(atan(init_tilt)-atan(rotated_tilt))


def calculate_rotated_height(ab_ratio, theta_deg, p1, p2):
    theta = radians(theta_deg)
    ba_ratio = 1 / ab_ratio
    a2 = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) \
        / (1 + (ba_ratio**2))
    a = sqrt(a2)
    b = ba_ratio * a
    up_p1 = abs(b * sin(theta))
    down_p1 = abs(a * cos(theta))
    return up_p1, down_p1


def calculate_p1_p2(frame, place):
    w, h = frame.size
    p1 = w * place[0], h * place[1]
    p2 = w * place[2], h * place[3]
    return p1, p2


def frame_write_gen(text, font, place, example_frame, color):
    p1, p2 = calculate_p1_p2(example_frame, place)

    txt = create_text_image(text, font, color)
    text_ratio = txt.size[1] / txt.size[0]

    rotation_degree = calculate_rotation_angle(text_ratio, p1, p2)

    up_p1, down_p1 = calculate_rotated_height(
        text_ratio, rotation_degree, p1, p2)

    rotated_text_top_left = int(p1[0]), int(p1[1]) #todo

    rotated_text_size = (
        int(p2[0]-p1[0]), int(up_p1+down_p1))

    final_txt = txt.rotate(rotation_degree,  expand=1).resize(rotated_text_size)

    print("final text end: ", p2)
    print(f"rotation degree : {rotation_degree}")
    print("top left e rotated ", rotated_text_top_left)
    print("size e rotated ", rotated_text_size)
    print("down right e rotated ",
          (rotated_text_size[0]+rotated_text_top_left[0],
              rotated_text_size[1]+rotated_text_top_left[1]))

    def inner(inp_frame):
        frame = inp_frame.copy().convert('RGBA')
        frame.paste(
            final_txt,
            box=rotated_text_top_left,
         #   mask=final_txt
        )
        return frame
    return inner


def write_on_gif(inp_file, out_file, text, place, font, color):
    inp_frames = load_gif_frames(inp_file)

    write_on_frame = frame_write_gen(text, font, place, inp_frames[0], color)

    out_frames = [write_on_frame(frame) for frame in inp_frames]

    save_gif(out_frames, out_file)


def parse_place(inp, parser):
    place_tup = tuple(map(float, inp.strip().replace(" ", ",").split(",")))
    if not len(place_tup) == 4:
        parser.error("you should enter exactly 4 numbers, seperated by ','")
        return None
    elif min(place_tup) < 0 or max(place_tup) > 1:
        parser.error("places should be between 0 and 1")
        return None
    else:
        return place_tup


def parse_color(inp, parser):
    color_tup = tuple(map(int, inp.strip().replace(" ", ",").split(",")))
    if not len(color_tup) == 3:
        parser.error(
            "you should enter exactly 3 numbers for rgb, seperated by ','")
        return None
    elif min(color_tup) < 0 or max(color_tup) > 255:
        parser.error("colors should be between 0 and 255")
        return None
    else:
        return color_tup


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

    parser.add_argument("-f", "--font", dest="font",
                        help="specify text font",
                        type=lambda f: ImageFont.truetype(f, size=100),
                        default=ImageFont.load_default())

    parser.add_argument("-p", "--place", dest="place",
                        help="specify up-left and down right position of image, relative",
                        type=lambda d: parse_place(d, parser),
                        default=(0, 0, 1, 1))

    parser.add_argument("-c", "--color", dest="color",
                              help="your text color",
                              type=lambda c: parse_color(c, parser),
                              default=(255, 255, 255))

    conf = parser.parse_args()

    write_on_gif(conf.input_file, conf.output_file,
                 conf.text, conf.place, conf.font, conf.color)
