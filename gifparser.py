# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import lzw
import utils


from my_types import \
    Image, \
    GraphicControlExtension, \
    ImageDescriptor, \
    LogicalScreenDescriptor, \
    GifObj, \
    ImgBlock, \
    HexdumpItem
from constants import \
    LS_DESCRIPTOR_SIZE, \
    IMG_DESCRIPTOR_SIZE, \
    GC_EXTENSION_SIZE, \
    IMAGE_IDENTIFIER, \
    EXTENSION_IDENTIFIER, \
    GC_EXTENSION_IDENTIFIER, \
    C_EXTENSION_IDENTIFIER, \
    PT_EXTENSION_IDENTIFIER, \
    A_EXTENSION_IDENTIFIER, \
    LS_DESCRIPTOR_STR, \
    GLOBAL_COLOR_TABLE_STR, \
    IMG_DESCRIPTOR_STR, \
    IMAGE_STR, \
    LOCAL_COLOR_TABLE_STR, \
    GC_EXTENSION_STR, \
    C_EXTENSION_STR, \
    PT_EXTENSION_STR, \
    A_EXTENSION_STR, \
    GLOBAL_COLOR_TABLE

IMAGES_DIRECTORY = 'images'


def parse_logical_screen_descriptor(descriptor_bytes):
    header = descriptor_bytes[:6].decode("utf-8")
    width = int.from_bytes(descriptor_bytes[6:8], byteorder='little')
    height = int.from_bytes(descriptor_bytes[8:10], byteorder='little')
    packed_fields = "{0:08b}".format(descriptor_bytes[10])
    global_color_table_flag = bool(int(packed_fields[0]))
    color_resolution = int(packed_fields[1:4], 2)
    sort_flag = bool(int(packed_fields[4]))
    global_color_table_size = int(packed_fields[5:], 2)
    background_color = descriptor_bytes[11]
    ls_descriptor = LogicalScreenDescriptor(header,
                                            width,
                                            height,
                                            global_color_table_flag,
                                            color_resolution,
                                            sort_flag,
                                            global_color_table_size,
                                            background_color)
    return ls_descriptor


def parse_color_table(ct_bytes):
    color_table = list()
    for i in range(3, len(ct_bytes) + 1, 3):
        red = ct_bytes[i - 3]
        green = ct_bytes[i - 2]
        blue = ct_bytes[i - 1]
        color = "#{0:02x}{1:02x}{2:02x}".format(red, green, blue)
        color_table.append(color)

    return color_table


def parse_img_descriptor(img_descriptor_bytes):
    image_left_pos = int.from_bytes(img_descriptor_bytes[1:3],
                                    byteorder='little')
    image_top_pos = int.from_bytes(img_descriptor_bytes[3:5],
                                   byteorder='little')
    img_width = int.from_bytes(img_descriptor_bytes[5:7],
                               byteorder='little')
    img_height = int.from_bytes(img_descriptor_bytes[7:9],
                                byteorder='little')
    packed_fields = "{0:08b}".format(img_descriptor_bytes[9])
    local_color_table_flag = bool(int(packed_fields[0]))
    # interlace_flag = bool(int(packed_fields[1]))
    # sort_flag = bool(int(packed_fields[2]))
    local_color_table_size = int(packed_fields[5:], 2)
    img_descriptor = ImageDescriptor(image_left_pos, image_top_pos,
                                     img_width, img_height,
                                     local_color_table_flag,
                                     local_color_table_size)
    return img_descriptor


def parse_graphic_control_extension(extension_bytes):
    packed_fields = "{0:08b}".format(extension_bytes[0])
    disposal_method = int(packed_fields[3:6], 2)
    user_input_flag = bool(int(packed_fields[6]))
    transparent_color_flag = bool(int(packed_fields[7]))
    delay_time = int.from_bytes(extension_bytes[1:3], byteorder='little')
    transparent_color_index = extension_bytes[3]
    gc_extension = GraphicControlExtension(disposal_method,
                                           user_input_flag,
                                           transparent_color_flag,
                                           delay_time,
                                           transparent_color_index)
    return gc_extension


class GifParser:
    def __init__(self, filebytes):
        self.filebytes = filebytes
        self.current_index = 0
        self.img_count = 0
        self.hexdump = list()
        self.global_color_table = GLOBAL_COLOR_TABLE
        self.non_decoded_img = []

    def get_bytes(self, start, end):
        return self.filebytes[start:end]

    def get_image_bytes(self):
        start_img = self.current_index - 1
        image_data = b''
        subblock_size = self.get_current_byte()
        while subblock_size != 0:
            self.current_index += 1
            subblock_end = self.current_index + subblock_size
            image_data += self.filebytes[self.current_index:subblock_end]
            self.current_index += subblock_size
            subblock_size = self.get_current_byte()
        self.current_index += 1
        end_img = self.current_index
        self.add_item_to_hexdump_list(start_img, end_img, IMAGE_STR)
        return image_data

    def add_item_to_hexdump_list(self, start, end, item_name):
        hexdump_item = HexdumpItem(start, end, item_name)
        self.hexdump.append(hexdump_item)

    @staticmethod
    def get_real_color_table_size(ct_size):
        ct_real_size = 3 * 2 ** (ct_size + 1)
        return ct_real_size

    def get_ls_descriptor(self):
        start_ls_desc = self.current_index
        end_ls_desc = start_ls_desc + LS_DESCRIPTOR_SIZE
        ls_descriptor_bytes = self.get_bytes(start_ls_desc, end_ls_desc)
        ls_descriptor = parse_logical_screen_descriptor(ls_descriptor_bytes)
        self.add_item_to_hexdump_list(start_ls_desc,
                                      end_ls_desc,
                                      LS_DESCRIPTOR_STR)
        self.current_index = end_ls_desc
        return ls_descriptor

    def get_global_color_table(self, gct_size):
        gct_real_size = self.get_real_color_table_size(gct_size)
        start_gct = self.current_index
        end_gct = start_gct + gct_real_size
        gct_bytes = self.get_bytes(start_gct, end_gct)
        gct = parse_color_table(gct_bytes)
        self.add_item_to_hexdump_list(start_gct, end_gct,
                                      GLOBAL_COLOR_TABLE_STR)
        self.current_index = end_gct
        return gct

    def get_local_color_table(self, lct_size):
        lct_real_size = self.get_real_color_table_size(lct_size)
        start_lct = self.current_index
        end_lct = start_lct + lct_real_size
        lct_bytes = self.get_bytes(start_lct, end_lct)
        lct = parse_color_table(lct_bytes)
        self.add_item_to_hexdump_list(start_lct,
                                      end_lct,
                                      LOCAL_COLOR_TABLE_STR)
        self.current_index = end_lct
        return lct

    def get_img_descriptor(self):
        start_img_desc = self.current_index
        end_img_desc = start_img_desc + IMG_DESCRIPTOR_SIZE
        img_descriptor_bytes = self.get_bytes(start_img_desc, end_img_desc)
        img_descriptor = parse_img_descriptor(img_descriptor_bytes)
        self.add_item_to_hexdump_list(start_img_desc,
                                      end_img_desc,
                                      IMG_DESCRIPTOR_STR)
        self.current_index = end_img_desc
        return img_descriptor

    def get_min_lzw_code(self):
        code = self.filebytes[self.current_index]
        self.current_index += 1
        return code

    def get_image(self):
        self.img_count += 1
        img_descriptor = self.get_img_descriptor()
        local_color_table = self.global_color_table
        if img_descriptor.local_color_table_flag:
            lct_size = img_descriptor.local_color_table_size
            local_color_table = self.get_local_color_table(lct_size)
        lzw_min_code_size = self.get_min_lzw_code()
        image_data = self.get_image_bytes()
        img_list = lzw.decode_lzw(image_data,
                                  len(local_color_table),
                                  lzw_min_code_size)
        image = Image(left_pos=img_descriptor.image_left_position,
                      top_pos=img_descriptor.image_top_position,
                      width=img_descriptor.img_width,
                      height=img_descriptor.img_height,
                      color_table=local_color_table,
                      image_list=img_list)
        return image

    def get_graphic_control_extension(self):
        start_byte = self.current_index - 1
        self.current_index += 2
        gc_extension_bytes = self.filebytes[
                             self.current_index:
                             self.current_index + GC_EXTENSION_SIZE]
        gc_extension = parse_graphic_control_extension(gc_extension_bytes)
        self.current_index += GC_EXTENSION_SIZE
        self.add_item_to_hexdump_list(start_byte,
                                      self.current_index,
                                      GC_EXTENSION_STR)
        return gc_extension

    def __skip_subblocks(self):
        subblock_size = self.get_current_byte()
        while subblock_size != 0:
            self.current_index += 1
            self.current_index += subblock_size
            subblock_size = self.get_current_byte()
        self.current_index += 1

    def skip_comment_extension(self):
        start_byte = self.current_index - 1
        self.current_index += 1
        self.__skip_subblocks()
        self.add_item_to_hexdump_list(start_byte,
                                      self.current_index,
                                      C_EXTENSION_STR)

    def skip_application_extension(self):
        start_byte = self.current_index - 1
        self.current_index += 2
        ext_id = self.filebytes[self.current_index:self.current_index + 8]
        self.current_index += 8
        code = self.filebytes[self.current_index:self.current_index + 3]
        self.current_index += 3
        self.__skip_subblocks()
        self.add_item_to_hexdump_list(start_byte,
                                      self.current_index,
                                      A_EXTENSION_STR)

    def skip_plain_text_extension(self):
        start_byte = self.current_index - 1
        self.current_index += 14
        self.__skip_subblocks()
        self.add_item_to_hexdump_list(start_byte,
                                      self.current_index,
                                      PT_EXTENSION_STR)

    def get_extension_identifier(self):
        self.current_index += 1
        return '{0:02x}'.format(self.get_current_byte())

    def get_current_byte(self):
        return self.filebytes[self.current_index]

    def is_end_of_file(self):
        return self.current_index == len(self.filebytes) - 1

    def get_changed_gct(self, gct_size):
        gct = self.get_global_color_table(gct_size)
        gct = utils.change_palette_colors(gct)
        return gct

    def get_mixed_gct(self, gct_size):
        gct = self.get_global_color_table(gct_size)
        utils.mix_palette_colors(gct)
        return gct

    def __get_gif(self, ls_descriptor):
        cur_img_delay_time = 0
        img_blocks = []
        while not self.is_end_of_file():
            current_byte = chr(self.get_current_byte())
            if current_byte == IMAGE_IDENTIFIER:
                try:
                    image = self.get_image()
                    img_block = ImgBlock(image, cur_img_delay_time)
                    img_blocks.append(img_block)
                    cur_img_delay_time = 0
                except:
                    #  !!!ВАЖНО!!!
                    # найти связь наличия локальной таблицы
                    # с багами в дешифровщике
                    self.non_decoded_img.append(self.current_index)
            if current_byte == EXTENSION_IDENTIFIER:
                extnsn_identifier = self.get_extension_identifier()
                if extnsn_identifier == GC_EXTENSION_IDENTIFIER:
                    extension = self.get_graphic_control_extension()
                    cur_img_delay_time = extension.delay_time
                elif extnsn_identifier == C_EXTENSION_IDENTIFIER:
                    self.skip_comment_extension()
                elif extnsn_identifier == PT_EXTENSION_IDENTIFIER:
                    self.skip_plain_text_extension()
                elif extnsn_identifier == A_EXTENSION_IDENTIFIER:
                    self.skip_application_extension()
        gif_obj = GifObj(ls_descriptor,
                         img_blocks,
                         self.filebytes,
                         self.hexdump,
                         self.img_count,
                         self.non_decoded_img,
                         self.global_color_table)
        return gif_obj

    def get_gif_with_changed_gct(self):
        ls_descriptor = self.get_ls_descriptor()
        if ls_descriptor.global_color_table_flag:
            gct_size = ls_descriptor.global_color_table_size
            gct = self.get_global_color_table(gct_size)
            gct = utils.change_palette_colors(gct)
            self.global_color_table = gct
        return self.__get_gif(ls_descriptor)

    def get_gif_with_mixed_gct(self):
        ls_descriptor = self.get_ls_descriptor()
        if ls_descriptor.global_color_table_flag:
            gct_size = ls_descriptor.global_color_table_size
            gct = self.get_global_color_table(gct_size)
            utils.mix_palette_colors(gct)
            self.global_color_table = gct
        return self.__get_gif(ls_descriptor)

    def get_gif(self):
        ls_descriptor = self.get_ls_descriptor()
        if ls_descriptor.global_color_table_flag:
            gct_size = ls_descriptor.global_color_table_size
            self.global_color_table = self.get_global_color_table(gct_size)
        return self.__get_gif(ls_descriptor)


def get_gif_obj_from_file(filename):
    path_to_file = os.path.join(os.getcwd(), filename)
    with open(path_to_file, 'rb') as gif_file:
        filebytes = gif_file.read()
        g_parser = GifParser(filebytes)
        gif_obj = g_parser.get_gif()
    return gif_obj


def get_gif_obj_from_file_m(filename):
    path_to_file = os.path.join(os.getcwd(), filename)
    with open(path_to_file, 'rb') as gif_file:
        filebytes = gif_file.read()
        g_parser = GifParser(filebytes)
        gif_obj = g_parser.get_gif_with_mixed_gct()
    return gif_obj


def get_gif_obj_from_file_ch(filename):
    path_to_file = os.path.join(os.getcwd(), filename)
    with open(path_to_file, 'rb') as gif_file:
        filebytes = gif_file.read()
        g_parser = GifParser(filebytes)
        gif_obj = g_parser.get_gif_with_changed_gct()
    return gif_obj
