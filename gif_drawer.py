# !/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter
from my_types import ImgBlock


class GifDrawer:
    def __init__(self, img_blocks):
        self.root = tkinter.Tk()
        self.current_image_index = 0
        self.img_blocks = img_blocks

    def start(self):
        if len(self.img_blocks) == 0:
            self.display_err()
        elif len(self.img_blocks) == 1:
            self.current_image = self.get_image()
        else:
            # self.change_cur_index()
            self.current_image = self.get_image()
            self.current_delay_time = self.get_delay_time()
            self.display_gif()
        self.root.mainloop()

    def display_gif(self):
        self.current_image = self.get_image()
        self.change_cur_index()
        self.current_image.after(self.current_delay_time * 10,
                                 self.display_gif)

    def change_cur_index(self):
        self.current_image_index += 1
        img_count = len(self.img_blocks)
        if self.current_image_index == img_count:
            self.current_image_index = 0

    def get_image(self):

        block = self.img_blocks[self.current_image_index]
        if not isinstance(block, ImgBlock):
            return
        image = block.image
        return self.create_image(image)

    def get_delay_time(self):
        block = self.img_blocks[self.current_image_index]
        if not isinstance(block, ImgBlock):
            print('No ImgBlock')
            return
        return block.delay_time

    @staticmethod
    def create_pixel(x, y, color, img_screen):
        img_screen.create_line(x, y, x + 1, y + 1, width=1, fill=color)
        img_screen.pack()

    def create_image(self, image):
        img_frame = tkinter.Frame(self.root,
                                  height=image.height,
                                  width=image.width)
        img_frame.place(x=0, y=0)
        img_frame.pack_propagate(0)
        img_screen = tkinter.Canvas(img_frame,
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
        img_screen.pack()
        return img_frame

    def display_err(self):
        error_frame = tkinter.Frame(self.root)
        error_frame.place(x=0, y=0)
        err_text = "No decoded image."
        path_label = tkinter.Label(error_frame,
                                   text=err_text)
        path_label.pack()
