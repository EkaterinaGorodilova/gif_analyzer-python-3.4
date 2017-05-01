# !/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter
import utils
import gifparser
from my_types import GraphicControlExtension, ImgBlock
from PIL import Image, ImageDraw
import os
import gif_drawer

from gui_consts import *
'''
    SCREEN_WIDTH, \
    SCREEN_HEIGHT, \
    SAVE_PALETTE_BUTTON_WIDTH, \
    SAVE_PALETTE_BUTTON_HEIGHT, \
    SAVE_PALETTE_BUTTON_LEFT_POS, \
    SAVE_PALETTE_BUTTON_TOP_POS
'''

PANEL_BG_COLOR = 'black'
ENTRY_PANEL_BG = "white"
TEXT_COLOR = 'white'
FRAME_SIZE = 10
COLOR_PANEL_SIZE = 10
PATH_LABEL_HEIGHT = 20
CURRENT_DIRECTORY = os.getcwd()


class GUI:
    def __init__(self, gif_obj, filename):
        self.filename = filename
        self.gif_obj = gif_obj
        self.root = tkinter.Tk()
        self.root_height = SCREEN_HEIGHT
        self.root_width = SCREEN_WIDTH
        self.root.geometry("%dx%d" % (self.root_width, self.root_height))
        self.root["bg"] = ROOT_BG_COLOR
        self.root.title('Gif analyzer')

    def start(self):
        self.display_current_path()
        self.add_menu()
        self.display_img_panel()
        self.create_info_panel()
        self.display_palette()
        self.display_gif()
        self.root.mainloop()

    @staticmethod
    def create_pixel(x, y, color, img_screen):
        img_screen.create_line(x, y, x + 1, y + 1, width=1, fill=color)
        img_screen.pack()

    def display_current_path(self):
        current_path = os.getcwd()
        label_width = SCREEN_WIDTH
        path_frame = tkinter.Frame(self.root,
                                   height=PATH_LABEL_HEIGHT,
                                   width=label_width)
        path_frame.place(x=0, y=0)
        path_frame.pack_propagate(0)
        label_text = "Current directory: {0}".format(current_path)
        path_label = tkinter.Label(path_frame,
                                   width=label_width,
                                   text=label_text,
                                   bg=PANEL_BG_COLOR,
                                   fg=TEXT_COLOR)
        path_label.pack()

    def create_image(self, image):
        left_pos = (self.root_width // 4) * 3 - (image.width//2)
        top_pos = self.root_height // 2 - (image.height//2)
        img_screen = tkinter.Canvas(self.root,
                                    width=image.width,
                                    height=image.height)

        current_x = image.left_pos
        current_y = image.top_pos
        for color_index in image.image_list:
            color = image.color_table[color_index]
            if current_x > image.width - 1:
                current_y += 1
                current_x = 0
            self.create_pixel(current_x, current_y, color, img_screen)
            current_x += 1
        img_screen.place(x=left_pos, y=top_pos)
        img_screen.pack_propagate(0)

    def display_img_panel(self):
        width = self.root_width // 2 - FRAME_SIZE * 3
        height = self.root_height - FRAME_SIZE * 2 - PATH_LABEL_HEIGHT
        left_pos = self.root_width // 2 + FRAME_SIZE * 2
        top_pos = FRAME_SIZE + PATH_LABEL_HEIGHT
        bg_color = "black"
        img_panel_frame = tkinter.Frame(self.root,
                                        height=height,
                                        width=width,
                                        bg=bg_color)
        img_panel_frame.place(x=left_pos, y=top_pos)
        self.display_switch_buttons(img_panel_frame)
        img_panel_frame.pack_propagate(0)

    def display_gif(self):
        delay_time = 0
        ls_descriptor = self.gif_obj.logical_screen_descriptor
        screen_width = ls_descriptor.ls_width
        screen_height = ls_descriptor.ls_height
        for block in self.gif_obj.img_blocks:
            if isinstance(block, GraphicControlExtension):
                delay_time = block.delay_time
            if isinstance(block, ImgBlock):
                image = block.image
                self.create_image(image)
                break

    def display_palette(self):
        palette_list = self.gif_obj.palette
        color_count = len(palette_list)
        count_color_in_line = utils.get_palette_width(color_count)
        panel_width = self.root_width // 2
        panel_height = self.root_height - FRAME_SIZE * 2 - PATH_LABEL_HEIGHT
        left_pos = FRAME_SIZE
        top_pos = FRAME_SIZE + PATH_LABEL_HEIGHT
        palette_frame = tkinter.Frame(self.root,
                                      height=panel_height,
                                      width=panel_width,
                                      bg=PANEL_BG_COLOR)
        palette_frame.place(x=left_pos, y=top_pos)
        color_left_pos = COLOR_PANEL_SIZE
        color_top_pos = COLOR_PANEL_SIZE
        cur_color_count = 0
        for color in palette_list:
            color_panel = tkinter.Canvas(palette_frame,
                                         width=COLOR_PANEL_SIZE,
                                         height=COLOR_PANEL_SIZE, bg=color)
            color_panel.pack()
            color_panel.place(x=color_left_pos, y=color_top_pos)
            color_left_pos += COLOR_PANEL_SIZE * 2
            cur_color_count += 1
            if cur_color_count == count_color_in_line:
                cur_color_count = 0
                color_left_pos = COLOR_PANEL_SIZE
                color_top_pos += COLOR_PANEL_SIZE * 2
        self.display_save_palette_button(palette_frame)

    def add_menu(self):
        menubar = tkinter.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tkinter.Menu(menubar, tearoff=0)
        file_menu.add_command(label=OPEN_FILE,
                              command=self.get_new_filename)
        file_menu.add_command(label=CHANGE_DIRECTORY,
                              command=self.get_new_directory)
        file_menu.add_command(label=EXPORT_IMAGES,
                              command=self.save_images)
        file_menu.add_command(label=EXIT, command=self.close_window)
        menubar.add_cascade(label=FILE, menu=file_menu)
        show_menu = self.create_show_menu(menubar)
        palette_menu = self.create_palette_menu(show_menu)
        show_menu.add_cascade(label=PALETTE, menu=palette_menu)
        menubar.add_cascade(label=SHOW, menu=show_menu)

    def create_show_menu(self, main_menu):
        show_menu = tkinter.Menu(main_menu, tearoff=0)
        show_menu.add_command(label=GIF,
                              command=self.draw_gif)
        show_menu.add_command(label=INFO,
                              command=self.display_gif_info_panel)
        show_menu.add_command(label=HEXDUMP,
                              command=self.display_hexdump_panel)
        show_menu.add_command(label=BYTES,
                              command=self.display_bytes_panel)
        return show_menu

    def draw_gif(self):
        gd = gif_drawer.GifDrawer(self.gif_obj.img_blocks)
        gd.start()

    def create_palette_menu(self, main_menu):
        palette_menu = tkinter.Menu(main_menu, tearoff=0)
        palette_menu.add_command(label=CORRECT_PALETTE,
                                 command=self.display_correct_palette)
        palette_menu.add_command(label=MIX_COLORS,
                                 command=self.mix_palette)
        palette_menu.add_command(label=CHANGE_COLORS,
                                 command=self.change_palette)
        palette_menu.add_command(label=SAVE,
                                 command=self.save_palette)
        return palette_menu

    def display_save_palette_button(self, palette_frame):
        save_button = tkinter.Button(palette_frame,
                                     text="Save",
                                     width=SAVE_PALETTE_BUTTON_WIDTH,
                                     height=SAVE_PALETTE_BUTTON_HEIGHT,
                                     command=self.save_palette)
        save_button.pack()
        save_button.place(x=SAVE_PALETTE_BUTTON_LEFT_POS,
                          y=SAVE_PALETTE_BUTTON_TOP_POS)

    def mix_palette(self):
        self.gif_obj = gifparser.get_gif_obj_from_file_m(self.filename)
        self.display_gif()
        self.display_palette()

    def display_correct_palette(self):
        self.gif_obj = gifparser.get_gif_obj_from_file(self.filename)
        self.display_gif()
        self.display_palette()

    def change_palette(self):
        self.gif_obj = gifparser.get_gif_obj_from_file_ch(self.filename)
        self.display_gif()
        self.display_palette()

    def create_info_panel(self):
        info_width = self.root_width // 2
        info_height = \
            self.root_height - FRAME_SIZE * 2 - PATH_LABEL_HEIGHT
        left_pos = FRAME_SIZE
        top_pos = FRAME_SIZE + PATH_LABEL_HEIGHT
        info_frame = tkinter.Frame(self.root,
                                   height=info_height,
                                   width=info_width,
                                   bg=PANEL_BG_COLOR)
        info_frame.place(x=left_pos, y=top_pos)
        return info_frame

    def display_info_panel(self, text):
        info_width = self.root_width // 2
        info_height = \
            self.root_height - FRAME_SIZE * 2 - PATH_LABEL_HEIGHT
        left_pos = FRAME_SIZE
        top_pos = FRAME_SIZE + PATH_LABEL_HEIGHT
        text_frame = tkinter.Frame(self.root, height=info_height,
                                   width=info_width, bg=PANEL_BG_COLOR)
        text_frame.place(x=left_pos, y=top_pos)
        text_frame.pack_propagate(0)
        text_panel = tkinter.Text(text_frame,
                                  font=('Monaco', 9),
                                  height=info_height,
                                  width=info_width,
                                  # state="disabled",
                                  bg=PANEL_BG_COLOR,
                                  fg=TEXT_COLOR)
        text_panel.insert(1.0, text)
        scrollbar = tkinter.Scrollbar(text_frame)
        scrollbar.pack(side='right')
        scrollbar[
            'command'] = text_panel.yview
        text_panel['yscrollcommand'] = scrollbar.set
        text_panel.pack()

    def display_hexdump_panel(self):
        bytes_amount = len(self.gif_obj.filebytes)
        hexdump_text = utils.get_hexdump_str(self.gif_obj.hexdump,
                                             bytes_amount,
                                             self.gif_obj.non_decoded_imgs)
        self.display_info_panel(hexdump_text)

    def display_gif_info_panel(self):
        gif_info_text = utils.get_full_info(self.gif_obj)
        self.display_info_panel(gif_info_text)

    def display_bytes_panel(self):
        bytes_str_length = 16
        bytes_text = utils.get_bytes(self.gif_obj.filebytes, bytes_str_length)
        self.display_info_panel(bytes_text)

    def draw_mainwindow(self):
        self.start()
        # self.root.mainloop()

    def get_new_filename(self):
        frame_width = 300
        frame_height = 300
        frame_left_pos = SCREEN_WIDTH // 2 - frame_width // 2
        frame_top_pos = SCREEN_HEIGHT // 2 - frame_height // 2
        caption = 'Enter file name:'
        entry_frame = tkinter.Frame(self.root, bg=ENTRY_PANEL_BG)
        entry_frame.place(x=frame_left_pos, y=frame_top_pos)
        entry_label = tkinter.Label(entry_frame,
                                    text=caption,
                                    bg=ENTRY_PANEL_BG)
        entry_label.pack()
        entry_filename = tkinter.Entry(entry_frame,
                                       width=50,
                                       borderwidth=3)
        entry_filename.place(x=0, y=0)
        entry_filename.pack()

        def open_new_file():
            new_filename = entry_filename.get()
            entry_filename.destroy()
            entry_frame.destroy()
            self.open_file(new_filename)

        ok_button = tkinter.Button(entry_frame,
                                   text="OK",
                                   width=10,
                                   command=open_new_file)
        ok_button.place(x=50, y=50)
        ok_button.pack()

    def display_error(self, err_text, enter_again_func):
        frame_width = 300
        frame_height = 300
        frame_left_pos = SCREEN_WIDTH // 2 - frame_width // 2
        frame_top_pos = SCREEN_HEIGHT // 2 - frame_height // 2

        error_frame = tkinter.Frame(self.root)
        error_frame.place(x=frame_left_pos, y=frame_top_pos)
        path_label = tkinter.Label(error_frame,
                                   text=err_text)
        path_label.pack()

        def enter_again():
            error_frame.destroy()
            enter_again_func()

        def close_this_window():
            error_frame.destroy()
        ok_button = tkinter.Button(error_frame,
                                   text="Ok",
                                   width=10,
                                   command=enter_again)
        ok_button.place(x=50, y=50)
        ok_button.pack(side=tkinter.LEFT)
        close_button = tkinter.Button(error_frame,
                                      text="Close",
                                      width=10,
                                      command=close_this_window)
        close_button.place(x=0, y=50)
        close_button.pack(side=tkinter.RIGHT)

    def display_switch_buttons(self, img_panel_frame):
        btn_width = 5
        btn_height = 2
        next_btn_left_pos = SCREEN_WIDTH // 2 - 100
        next_btn_top_pos = SCREEN_HEIGHT - 100
        next_button = tkinter.Button(img_panel_frame,
                                     text=">",
                                     width=btn_width,
                                     height=btn_height,
                                     command=self.open_next_image)
        next_button.pack()
        next_button.place(x=next_btn_left_pos, y=next_btn_top_pos)
        prev_btn_left_pos = 20
        prev_btn_top_pos = SCREEN_HEIGHT - 100
        prev_button = tkinter.Button(img_panel_frame,
                                     text="<",
                                     width=btn_width,
                                     height=btn_height,
                                     command=self.open_prev_image)
        prev_button.pack()
        prev_button.place(x=prev_btn_left_pos, y=prev_btn_top_pos)

    def open_next_image(self):
        new_filename = utils.switch_to_next_image(self.filename)
        if new_filename != self.filename:
            self.open_file(new_filename)

    def open_prev_image(self):
        new_filename = utils.switch_to_prev_image(self.filename)
        if new_filename != self.filename:
            self.open_file(new_filename)

    def change_directory(self, new_directory):
        try:
            os.chdir(new_directory)
            self.display_current_path()
        except IOError:
            self.display_error(OPEN_DIRECTORY_ERROR_TEXT,
                               self.get_new_directory)

    def get_new_directory(self):
        frame_width = 300
        frame_height = 300
        frame_left_pos = SCREEN_WIDTH // 2 - frame_width // 2
        frame_top_pos = SCREEN_HEIGHT // 2 - frame_height // 2
        caption = 'Enter directory:'
        entry_frame = tkinter.Frame(self.root, bg=ENTRY_PANEL_BG)
        entry_frame.place(x=frame_left_pos, y=frame_top_pos)
        entry_label = tkinter.Label(entry_frame,
                                    text=caption,
                                    bg=ENTRY_PANEL_BG)
        entry_label.pack()
        entry_directory = tkinter.Entry(entry_frame,
                                        width=50,
                                        borderwidth=3)
        entry_directory.place(x=0, y=0)
        entry_directory.pack()

        def change_dir():
            new_directoty = entry_directory.get()
            entry_directory.destroy()
            entry_frame.destroy()
            self.change_directory(new_directoty)

        ok_button = tkinter.Button(entry_frame,
                                   text="OK",
                                   width=10,
                                   command=change_dir)
        ok_button.place(x=50, y=50)
        ok_button.pack()

    def open_file(self, new_filename):
        current_dir = os.getcwd()
        current_path = os.path.join(current_dir, new_filename)
        if os.path.exists(current_path):
            self.gif_obj = gifparser.get_gif_obj_from_file(new_filename)
            self.filename = new_filename
            self.draw_mainwindow()
        else:
            self.display_error(OPEN_FILE_ERROR_TEXT, self.get_new_filename)

    def save_images(self):
        prev_dir = os.getcwd()
        directory = os.path.join(prev_dir, self.filename[:-4])
        if os.path.exists(directory):
            files = os.listdir(directory)
            for file in files:
                file_path = os.path.join(directory, file)
                os.remove(file_path)
        else:
            os.mkdir(directory)
        os.chdir(directory)
        block_count = len(self.gif_obj.img_blocks)
        for block_index in range(block_count):
            block = self.gif_obj.img_blocks[block_index]
            if isinstance(block, ImgBlock):
                image = block.image
                self.save_image(image, block_index)
        os.chdir(prev_dir)

    @staticmethod
    def save_image(image_obj, image_index):
        image_filename = "{0}.jpg".format(image_index)
        img_width = image_obj.width
        img_height = image_obj.height
        image = Image.new("RGB", (img_width, img_height), PANEL_BG_COLOR)
        image_canvas = ImageDraw.Draw(image)
        current_x = image_obj.left_pos
        current_y = image_obj.top_pos
        for color_index in image_obj.image_list:
            color = image_obj.color_table[color_index]
            if current_x > image.width - 1:
                current_y += 1
                current_x = 0
            image_canvas.point([current_x, current_y], fill=color)
            current_x += 1
        image.save(image_filename)

    def save_palette(self):
        palette_list = self.gif_obj.palette
        color_count = len(palette_list)
        count_color_in_line = utils.get_palette_width(color_count)
        line_count = color_count // count_color_in_line
        img_width = count_color_in_line * COLOR_PANEL_SIZE * 2 + 1
        img_height = line_count * COLOR_PANEL_SIZE * 2 + 1
        outline_color = "white"
        palette_img = Image.new("RGB", (img_width, img_height), PANEL_BG_COLOR)
        palette_canvas = ImageDraw.Draw(palette_img)
        topleft_x = COLOR_PANEL_SIZE
        topleft_y = COLOR_PANEL_SIZE
        cur_color_count = 0
        for color in palette_list:
            downright_x = topleft_x + COLOR_PANEL_SIZE
            downright_y = topleft_y + COLOR_PANEL_SIZE
            palette_canvas.rectangle([topleft_x,
                                      topleft_y,
                                      downright_x,
                                      downright_y],
                                     outline=outline_color,
                                     fill=color)
            topleft_x += COLOR_PANEL_SIZE * 2
            cur_color_count += 1
            if cur_color_count == count_color_in_line:
                cur_color_count = 0
                topleft_x = COLOR_PANEL_SIZE
                topleft_y += COLOR_PANEL_SIZE * 2
        filename = "{0}_palette.jpg".format(self.filename[:-4])
        palette_img.save(filename)

    def close_window(self):
        self.root.destroy()


def get_filaname(file_path):
    dir = os.path.split(file_path)[0]
    filename = os.path.split(file_path)[1]
    currenr_dir = os.path.join(os.getcwd(), dir)
    os.chdir(currenr_dir)
    return filename


def run_prog(file_path):
    filename = get_filaname(file_path)
    gif_obj = gifparser.get_gif_obj_from_file(filename)
    dr = GUI(gif_obj, filename)
    dr.draw_mainwindow()


def run_prog_with_random_palette(file_path):
    filename = get_filaname(file_path)
    gif_obj = gifparser.get_gif_obj_from_file_ch(filename)
    dr = GUI(gif_obj, filename)
    dr.draw_mainwindow()
