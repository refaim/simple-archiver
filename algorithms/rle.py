# -*- coding: utf-8 -*-

MAX_BYTE = 255

def compress(reader, fdst, pbar):
    prev = None
    found = False
    count = 0
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
        fdst.write(result)
        pbar.update(reader.chunk_size)
    if count:
        fdst.write(bytearray([count]))

def uncompress(reader, fdst, pbar):
    prev = None
    found = False
    for chunk in reader:
        result = bytearray()
        for byte in chunk:
            if found:
                result.extend(prev * ord(byte))
                found = False
                prev = None
            else:
                result.append(byte)
                found = byte == prev
                prev = byte
        fdst.write(result)
        pbar.update(reader.chunk_size)
