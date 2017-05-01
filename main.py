# !/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import gui
import utils
import gifparser


# CONS_PROG = "console version"
GUI_PROG = "gui version"


def parse_args():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-f",
                            required=True,
                            help="path to gif file")
        parser.add_argument("-r",
                            action='store_const',
                            const=True,
                            help="random palette")
        parser.add_argument("-d",
                            action='store_const',
                            const=True,
                            help="show only hexdump")
        parser.add_argument("-i",
                            action='store_const',
                            const=True,
                            help="show only information about file")
        args = parser.parse_args()
        file_path = args.f
        if args.d:
            gif_obj = gifparser.get_gif_obj_from_file(file_path)
            hexdump = utils.get_only_hexdump(gif_obj)
            print(hexdump + '\n')
        if args.i:
            gif_obj = gifparser.get_gif_obj_from_file(file_path)
            info = utils.get_full_info(gif_obj)
            print(info + '\n')
        else:
            if args.r:
                gui.run_prog_with_random_palette(file_path)
            else:
                gui.run_prog(file_path)
    except FileNotFoundError:
        print("No such file or directory.")


parse_args()
