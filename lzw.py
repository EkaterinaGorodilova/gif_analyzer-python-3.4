# !/usr/bin/env python
# -*- coding: utf-8 -*-


CLEAR = 'clear'
END = 'end'
LZW_MAX_CODE_SIZE = 12


def create_lzw_list(color_table_length):
    lzw_list = list()
    for i in range(color_table_length):
        lzw_list.append([i])
    lzw_list.append(CLEAR)
    lzw_list.append(END)
    return lzw_list


def update_code_size(lzw_list_len, code_size):
    cur_code_size = len(bin(lzw_list_len)[2:])
    if cur_code_size > code_size:
        code_size += 1
    return code_size


def decode_lzw(img_data, color_table_length, lzw_min_code_size):
    lzw_list = create_lzw_list(color_table_length)
    code_size = lzw_min_code_size + 1
    result = list()
    current_bits = current_bits = \
        "{1:08b}{0:08b}".format(img_data[0], img_data[1])
    i = 2
    old = int(current_bits[-code_size:], 2)
    current_bits = current_bits[:-code_size]
    if old < len(lzw_list):
        if lzw_list[old] == CLEAR:
            old = int(current_bits[-code_size:], 2)
            current_bits = current_bits[:-code_size]
            for x in lzw_list[old]:
                result.append(x)
            code = old
    while i < len(img_data):
        while len(current_bits) < code_size:
            current_bits = "{0:08b}".format(img_data[i]) + current_bits
            i += 1
        code = int(current_bits[-code_size:], 2)
        current_bits = current_bits[:-code_size]
        if code < len(lzw_list):
            if lzw_list[code] == CLEAR:
                continue
            elif lzw_list[code] == END:
                return result
            else:
                for x in lzw_list[code]:
                    result.append(x)
                prfx = lzw_list[old]
                k = lzw_list[code][0]
                lzw_list.append(prfx + [k])
                old = code
        else:
            prfx = lzw_list[old]
            k = prfx[0]
            for x in prfx + [k]:
                result.append(x)
            lzw_list.append(prfx + [k])
            old = code
        code_size = update_code_size(len(lzw_list), code_size)
