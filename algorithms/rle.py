# -*- coding: utf-8 -*-

import console

MAX_BYTE = 255

def compress(reader, fsize, fdst):
    prev = None
    found = False
    count = 0
    pbar = console.ProgressBar(maxval=fsize)
    pbar.start()
    for chunk in reader:
        result = bytearray()
        for byte in chunk:
            if found:
                if byte == prev and count < MAX_BYTE:
                    count += 1
                else:
                    result.append(count)
                    result.append(byte)
                    count = 0
                    found = False
            else:
                result.append(byte)
                found = byte == prev
            prev = byte
        pbar.update(reader.chunk_size)
        fdst.write(result)
    if count:
        fdst.write(bytearray([count]))
    pbar.finish()

def decompress(reader, fsize, fdst):
    result = bytearray()
    prev = None
    found = False
    pbar = console.ProgressBar(maxval=fsize)
    pbar.start()
    for chunk in reader:
        for byte in chunk:
            if found:
                result.extend(prev * ord(byte))
                found = False
                prev = None
            else:
                result.append(byte)
                found = byte == prev
                prev = byte
        pbar.update(reader.chunk_size)
        fdst.write(result)
        result = bytearray()
    pbar.finish()
