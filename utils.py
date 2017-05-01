# !/usr/bin/env python
# -*- coding: utf-8 -*-


from constants import \
    UNRECOGNIZED_BYTES_STR, \
    IMAGE_STR
from math import log
import random
import os


def get_bytes(filebytes, line_length):
    hexdump_lines = []
    first_line = " Offset(h):   " + \
                 ' '.join(["{0:02X}".format(x) for x in range(line_length)])
    hexdump_lines.append(first_line)
    second_line = ""
    hexdump_lines.append(second_line)
    offset = 0
    l = len(filebytes) + 1
    for i in range(0, l, line_length):
        cur_bytes = filebytes[i:i+line_length]
        hex = ' '.join(["{0:02X}".format(x) for x in cur_bytes])
        printable = ''.join(
            [(chr(x) if len(repr(chr(x))) == 3 else '.') for x in cur_bytes])
        line = "  {0:08X}:   {1:<{3}}   {2}".format(
            offset, hex, printable, line_length * 3 - 1)
        offset += line_length
        hexdump_lines.append(line)
    res_str = '\n'.join(hexdump_lines)
    return res_str


def get_gereral_info(gif_obj):
    version = gif_obj.logical_screen_descriptor.header[3:]
    screen_width = gif_obj.logical_screen_descriptor.ls_width
    screen_height = gif_obj.logical_screen_descriptor.ls_height
    bg_color = gif_obj.logical_screen_descriptor.background_color
    general_info_lines = []
    first_line = '  General information:'
    general_info_lines.append(first_line)
    version_line = "    Version: {0}".format(version)
    general_info_lines.append(version_line)
    screen_size_line = \
        "    Logical screen size: {0} x {1} (width x height)".format(
            screen_width, screen_height)
    general_info_lines.append(screen_size_line)
    bg_color_line = "    Background color number: {0}".format(bg_color)
    general_info_lines.append(bg_color_line)
    img_count_line = "    Image count: {0}".format(gif_obj.image_count)
    general_info_lines.append(img_count_line)
    result_str = '\n'.join(general_info_lines)
    return result_str


def get_global_color_table_info(gif_obj):
    gct_info_lines = []
    first_line = '  Global color table:'
    gct_info_lines.append(first_line)
    gct_flag = gif_obj.logical_screen_descriptor.global_color_table_flag
    gct_presence_line = "    Presence of global color table: {0}".format(
        "present" if gct_flag else "absent")
    gct_info_lines.append(gct_presence_line)
    if gct_flag:
        ct_size = gif_obj.logical_screen_descriptor.global_color_table_size
        color_count = 2 ** (ct_size + 1)
        color_count_line = "    Number of colors: {0}".format(color_count)
        gct_info_lines.append(color_count_line)
        if gif_obj.logical_screen_descriptor.sort_flag:
            color_order = "decreasing importance"
        else:
            color_order = "random"
        color_order_line = "    Order of colors in table: {0}".format(
            color_order)
        gct_info_lines.append(color_order_line)
    result_str = '\n'.join(gct_info_lines)
    return result_str


def hexdump_item_to_str(hexdump_item):
    return '{0:<8} {1:<8}    {2:<28}    {0:08X}'.format(
        hexdump_item.start_byte,
        hexdump_item.end_byte - 1,
        hexdump_item.item_name)


def get_unrecognized_line(start, end):
    line = '{0:<8} {1:<8}    {2:<28}    {0:08X}'.format(
            start,
            end,
            UNRECOGNIZED_BYTES_STR)
    return line


def get_hexdump_str(hexdump_list, bytes_amount, non_decoded_imgs):
    hexdump_lines = []
    first_line = '{0:<8} {1:<8}    {2:<28}    {3:<8}'.format(
        'Start:', 'End:', 'Block name:', 'Offset:')
    second_line = '{0:<8} {1:<8}   {2:>38}'.format('(dec)', '(dec)', '(hex)')
    hexdump_lines.append(first_line)
    hexdump_lines.append(second_line)
    prev_end_byte = 0
    for item in hexdump_list:
        if item.start_byte != prev_end_byte:
            new_line = get_unrecognized_line(prev_end_byte,
                                             item.start_byte - 1)
            hexdump_lines.append(new_line)
        new_line = hexdump_item_to_str(item)
        if item.item_name == IMAGE_STR:
            if item.end_byte in non_decoded_imgs:
                new_line += '    non-decoded'
            else:
                new_line += '    +'
        hexdump_lines.append(new_line)
        prev_end_byte = item.end_byte
    if prev_end_byte != bytes_amount - 1:
        new_line = get_unrecognized_line(prev_end_byte, bytes_amount - 1)
        hexdump_lines.append(new_line)
    end_line = 'File size: %d' % bytes_amount
    hexdump_lines.append(end_line)
    return '\n'.join(hexdump_lines)


def get_full_info(gif_obj):
    result = ''
    result += get_gereral_info(gif_obj) + '\n'
    result += get_global_color_table_info(gif_obj) + '\n'
    return result


def get_palette_width(color_count):
    if color_count == 2:
        return 2
    count_log = int(log(color_count, 2))
    if count_log % 2 != 0:
        new_color_count = color_count * 2
        count_sqrt = int(new_color_count ** 0.5)
        return count_sqrt
    else:
        count_sqrt = int(color_count ** 0.5)
        return count_sqrt


def change_palette_colors(color_table):
    ff_channel = int("FF", 16)
    red_shift = random.randint(0, ff_channel)
    green_shift = random.randint(0, ff_channel)
    blue_shift = random.randint(0, ff_channel)
    new_color_table = list()
    for color in color_table:
        red = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue = int(color[5:], 16)
        new_red = (red + red_shift) % ff_channel
        new_green = (green + green_shift) % ff_channel
        new_blue = (blue + blue_shift) % ff_channel
        new_color = \
            "#{0:02x}{1:02x}{2:02x}".format(new_red, new_green, new_blue)
        new_color_table.append(new_color)
    return new_color_table


def mix_palette_colors(color_table):
    random.shuffle(color_table)


def switch_to_next_image(filename):
    files = [f for f in os.listdir(os.getcwd()) if f.endswith('.gif')]
    if files[-1] == filename:
        return filename
    for file_index in range(len(files) - 1):
        if files[file_index] == filename:
            return files[file_index + 1]


def switch_to_prev_image(filename):
    files = [f for f in os.listdir(os.getcwd()) if f.endswith('.gif')]
    if files[0] == filename:
        return filename
    for file_index in range(1, len(files)):
        if files[file_index] == filename:
            return files[file_index - 1]


def get_only_hexdump(gif_obj):
    bytes_amount = len(gif_obj.filebytes)
    hexdump_text = get_hexdump_str(gif_obj.hexdump,
                                   bytes_amount,
                                   gif_obj.non_decoded_imgs)
    return hexdump_text
