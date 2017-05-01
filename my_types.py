# !/usr/bin/env python
# -*- coding: utf-8 -*-

import collections


GraphicControlExtension = collections.namedtuple(
    'GraphicControlExtension',
    ['disposal_method',
     'user_input_flag',
     'transparent_color_flag',
     'delay_time',
     'transparent_color_index'])

Image = collections.namedtuple(
    "Image",
    ['left_pos',
     'top_pos',
     'width',
     'height',
     'color_table',
     'image_list'])

ImgBlock = collections.namedtuple(
    "ImgBlock",
    ['image',
     'delay_time'])

ImageDescriptor = collections.namedtuple(
    'ImageDescriptor',
    ['image_left_position',
     'image_top_position',
     'img_width',
     'img_height',
     'local_color_table_flag',
     'local_color_table_size'])

LogicalScreenDescriptor = collections.namedtuple(
    'LogicalScreenDescriptor',
    ['header',
     'ls_width',
     'ls_height',
     'global_color_table_flag',
     'color_resolution',
     'sort_flag',
     'global_color_table_size',
     'background_color'])

GifObj = collections.namedtuple(
    'GifObj',
    ['logical_screen_descriptor',
     'img_blocks',
     'filebytes',
     'hexdump',
     'image_count',
     'non_decoded_imgs',
     'palette'])

HexdumpItem = collections.namedtuple(
    'HexdumpItem',
    ['start_byte',
     'end_byte',
     'item_name'])
