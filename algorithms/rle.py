# -*- coding: utf-8 -*-

import console

BUF_SIZE = 10 * (2 ** 20) # 10 mb

def compress(fsrc, fsize, fdst):
    result = bytearray()
    prev = None
    found = False
    count = 0
    pbar = console.ProgressBar(maxval=fsize)
    pbar.start()
    data = fsrc.read(BUF_SIZE)
    while data:
        for char in data:
            if found:
                if char == prev and count < 255:
                    count += 1
                else:
                    result.append(count)
                    if char != prev:
                        result.append(char)
                    else:
                        result.append(prev)
                    count = 0
                    found = False
            else:
                result.append(char)
                found = char == prev
            prev = char
        pbar.update(len(data))
        data = fsrc.read(BUF_SIZE)
        if not data and count > 0:
            result.append(count)
        fdst.write(result)
        result = bytearray()
    pbar.finish()

def decompress(fsrc, fsize, fdst):
    result = bytearray()
    prev = None
    found = False
    pbar = console.ProgressBar(maxval=fsize)
    data = fsrc.read(BUF_SIZE)
    while data:
        for char in data:
            if found:
                count = ord(char)
                if count:
                    result.extend(prev * count)
                found = False
                prev = None
            else:
                result.append(char)
                found = char == prev
                prev = char
        pbar.update(len(data))
        data = fsrc.read(BUF_SIZE)
        fdst.write(result)
        result = bytearray()
    pbar.finish()
