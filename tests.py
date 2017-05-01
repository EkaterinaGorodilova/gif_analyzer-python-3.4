# !/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import gifparser
import utils


from constants import \
    EXTENSION_IDENTIFIER, \
    A_EXTENSION_IDENTIFIER, \
    GC_EXTENSION_IDENTIFIER, \
    IMAGE_IDENTIFIER


class TestImageNameLoading(unittest.TestCase):
    def setUp(self):
        self.filename = 'images/loading.gif'
        self.gif_obj = gifparser.get_gif_obj_from_file(self.filename)
        with open(self.filename, 'rb') as gif_file:
            self.filebytes = gif_file.read()
        self.g_parser = gifparser.GifParser(self.filebytes)
        self.exp_ls_descriptor_bytes = \
            b'\x47\x49\x46\x38\x39\x61\x80\x00\x80\x00\xC6\x00\x00'
        # !! читать из файла:
        self.exp_gct_bytes = \
            b'\x04\x02\x04\x84\x82\x84\x44\x42\x44\xC4\xC2\xC4\x24' \
            b'\x22\x24\xA4\xA2\xA4\x64\x62\x64\xE4\xE2\xE4\x14\x12' \
            b'\x14\x94\x92\x94\x54\x52\x54\xD4\xD2\xD4\x34\x32\x34' \
            b'\xB4\xB2\xB4\x74\x72\x74\xF4\xF2\xF4\x0C\x0A\x0C\x8C' \
            b'\x8A\x8C\x4C\x4A\x4C\xCC\xCA\xCC\x2C\x2A\x2C\xAC\xAA' \
            b'\xAC\x6C\x6A\x6C\xEC\xEA\xEC\x1C\x1A\x1C\x9C\x9A\x9C' \
            b'\x5C\x5A\x5C\xDC\xDA\xDC\x3C\x3A\x3C\xBC\xBA\xBC\x7C' \
            b'\x7A\x7C\xFC\xFA\xFC\x04\x06\x04\x84\x86\x84\x44\x46' \
            b'\x44\xC4\xC6\xC4\x24\x26\x24\xA4\xA6\xA4\x64\x66\x64' \
            b'\xE4\xE6\xE4\x14\x16\x14\x94\x96\x94\x54\x56\x54\xD4' \
            b'\xD6\xD4\x34\x36\x34\xB4\xB6\xB4\x74\x76\x74\xF4\xF6' \
            b'\xF4\x0C\x0E\x0C\x8C\x8E\x8C\x4C\x4E\x4C\xCC\xCE\xCC' \
            b'\x2C\x2E\x2C\xAC\xAE\xAC\x6C\x6E\x6C\xEC\xEE\xEC\x1C' \
            b'\x1E\x1C\x9C\x9E\x9C\x5C\x5E\x5C\xDC\xDE\xDC\x3C\x3E' \
            b'\x3C\xBC\xBE\xBC\x7C\x7E\x7C\xFC\xFE\xFC\xFF\xFF\xFF' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
            b'\x00\x00\x00\x00\x00\x00\x00'
        self.netscape_block = \
            b'\x21\xFF\x0B\x4E\x45\x54\x53\x43\x41\x50\x45\x32\x2E' \
            b'\x30\x03\x01\x00\x00\x00'
        self.gc_extension_1 = \
            b'\x21\xF9\x04\x09\x06\x00\x40\x00'
        self.img_descriptor_1 = \
            b'\x2C\x00\x00\x00\x00\x80\x00\x80\x00\x00'
        self.image_block_1 = b''
        self.gct_size = 384

    def test_parse_ls_descriptor(self):
        ls_descriptor_bytes = self.g_parser.get_bytes(0, 13)
        ls_descriptor = \
            gifparser.parse_logical_screen_descriptor(ls_descriptor_bytes)
        self.assertEqual(self.exp_ls_descriptor_bytes, ls_descriptor_bytes)
        self.assertEqual('GIF89a', ls_descriptor.header)
        self.assertEqual(128, ls_descriptor.ls_width)
        self.assertEqual(128, ls_descriptor.ls_height)
        self.assertEqual(True, ls_descriptor.global_color_table_flag)
        self.assertEqual(4, ls_descriptor.color_resolution)
        self.assertEqual(False, ls_descriptor.sort_flag)
        self.assertEqual(6, ls_descriptor.global_color_table_size)
        self.assertEqual(0, ls_descriptor.background_color)

    def test_gct(self):
        gct_bytes = self.g_parser.get_bytes(13, 397)
        self.assertEqual(self.exp_gct_bytes, gct_bytes)
        exp_gct = \
            ['#040204', '#848284', '#444244', '#c4c2c4', '#242224', '#a4a2a4',
             '#646264', '#e4e2e4', '#141214', '#949294', '#545254', '#d4d2d4',
             '#343234', '#b4b2b4', '#747274', '#f4f2f4', '#0c0a0c', '#8c8a8c',
             '#4c4a4c', '#cccacc', '#2c2a2c', '#acaaac', '#6c6a6c', '#eceaec',
             '#1c1a1c', '#9c9a9c', '#5c5a5c', '#dcdadc', '#3c3a3c', '#bcbabc',
             '#7c7a7c', '#fcfafc', '#040604', '#848684', '#444644', '#c4c6c4',
             '#242624', '#a4a6a4', '#646664', '#e4e6e4', '#141614', '#949694',
             '#545654', '#d4d6d4', '#343634', '#b4b6b4', '#747674', '#f4f6f4',
             '#0c0e0c', '#8c8e8c', '#4c4e4c', '#cccecc', '#2c2e2c', '#acaeac',
             '#6c6e6c', '#eceeec', '#1c1e1c', '#9c9e9c', '#5c5e5c', '#dcdedc',
             '#3c3e3c', '#bcbebc', '#7c7e7c', '#fcfefc', '#ffffff', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000', '#000000', '#000000', '#000000', '#000000',
             '#000000', '#000000']
        self.assertEqual(exp_gct, gifparser.parse_color_table(gct_bytes))

    def test_gif_obj(self):
        self.assertEqual(12, len(self.gif_obj.img_blocks))
        self.assertEqual(12, self.gif_obj.image_count)
        self.assertEqual(0, len(self.gif_obj.non_decoded_imgs))
        self.assertEqual(128, len(self.gif_obj.palette))


class TestImageNameDodecahedron(unittest.TestCase):
    def setUp(self):
        self.filename = 'images//dodecahedron.gif'
        with open(self.filename, 'rb') as gif_file:
            self.filebytes = gif_file.read()
        self.g_parser = gifparser.GifParser(self.filebytes)
        self.exp_ls_descriptor_bytes = \
            b'\x47\x49\x46\x38\x39\x61\xA9\x00\xA9\x00\xF7\x00\x00'
        with open('files_for_tests/dodecahedron_exp_gct_bytes', 'rb') \
                as gct_file:
            self.exp_gct_bytes = gct_file.read()
        self.exp_gc_extension_bytes_1 = \
            b'\x21\xF9\x04\x04\x05\x00\x00\x00'
        self.exp_app_extension_bytes = \
            b'\x21\xFF\x0B\x4E\x45\x54\x53\x43\x41\x50\x45\x32\x2E' \
            b'\x30\x03\x01\x00\x00\x00'
        self.exp_img_descriptor_bytes_1 = \
            b'\x2C\x00\x00\x00\x00\xA9\x00\xA9\x00\x00'
        self.exp_lzw_code_image1 = 8

    def test_parse_ls_descriptor(self):
        ls_descriptor_bytes = self.g_parser.get_bytes(0, 13)
        ls_descriptor = \
            gifparser.parse_logical_screen_descriptor(ls_descriptor_bytes)
        self.assertEqual(self.exp_ls_descriptor_bytes, ls_descriptor_bytes)
        self.assertEqual('GIF89a', ls_descriptor.header)
        self.assertEqual(169, ls_descriptor.ls_width)
        self.assertEqual(169, ls_descriptor.ls_height)
        self.assertEqual(True, ls_descriptor.global_color_table_flag)
        self.assertEqual(7, ls_descriptor.color_resolution)
        self.assertEqual(False, ls_descriptor.sort_flag)
        self.assertEqual(7, ls_descriptor.global_color_table_size)
        self.assertEqual(0, ls_descriptor.background_color)


class TestUtils(unittest.TestCase):
    def setup(self):
        self.img_path = 'Images/src3.gif'
        self.img_bytes = b''
        with open(self.img_path, 'rb') as gif_file:
            self.img_bytes = gif_file.read()

    def test_get_palette_width(self):
        self.assertEqual(2, utils.get_palette_width(2))
        self.assertEqual(2, utils.get_palette_width(4))
        self.assertEqual(4, utils.get_palette_width(8))
        self.assertEqual(4, utils.get_palette_width(16))
        self.assertEqual(8, utils.get_palette_width(32))
        self.assertEqual(8, utils.get_palette_width(64))
        self.assertEqual(16, utils.get_palette_width(128))
        self.assertEqual(16, utils.get_palette_width(256))


if __name__ == '__main__':
    unittest.main()
