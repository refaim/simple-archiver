# -*- coding: utf-8 -*-

import heapq
import marshal

import pyximport; pyximport.install()
import huffman_c

from common import ArchiverException

BITS_IN_BYTE = 8

def _convert_tree_to_table(tree):

    def convert(tree, prefix):
        if len(tree) == 2:
            byte = tree[1]
            table[byte] = prefix or '0'
        else:
            convert(tree[1], prefix + '0')
            convert(tree[2], prefix + '1')

    table = {}
    convert(tree, '')
    return table

def _make_tree(reader, pbar):
    raw_table = {}
    for chunk in reader:
        for byte in chunk:
            if byte in raw_table:
                raw_table[byte] += 1
            else:
                raw_table[byte] = 1
        pbar.update(reader.chunk_size / 2)
    tree = [(v, k) for k, v in raw_table.iteritems()]
    heapq.heapify(tree)
    while len(tree) > 1:
        left, right = heapq.heappop(tree), heapq.heappop(tree)
        parent = (left[0] + right[0], left, right)
        heapq.heappush(tree, parent)
    return tree[0]

def compress(reader, fdst, pbar):
    code_table = _convert_tree_to_table(_make_tree(reader, pbar))
    marshal.dump(dict(zip(code_table.itervalues(), code_table.iterkeys())), fdst)
    marshal.dump(pbar.maxval, fdst)

    reader.fobj.seek(0)
    tail_len = 0
    for chunk in reader:
        result = []
        if tail_len:
            result.append(tail)
            tail_len = 0
        result.extend(code_table[byte] for byte in chunk)
        result = ''.join(result)

        tail_len = len(result) % BITS_IN_BYTE
        if tail_len:
            tail, result = result[-tail_len:], result[:-tail_len]

        result = bytearray(int(result[i:i+BITS_IN_BYTE], 2)
            for i in xrange(0, len(result), BITS_IN_BYTE))

        fdst.write(result)
        pbar.update(reader.chunk_size / 2)
    if tail_len:
        fdst.write(bytearray([int(tail, 2)]))

def uncompress(reader, fdst, pbar):
    try:
        code_table = marshal.load(reader.fobj)
        source_size = marshal.load(reader.fobj)
    except ValueError:
        raise ArchiverException('Bad file format')

    new_table = {}
    for k, v in code_table.iteritems():
        new_table[(int(k, 2), len(k))] = v
    code_table = new_table

    processed_bytes = 0
    for chunk in reader:
        result = huffman_c.uncompress(bytearray(chunk), code_table)
        processed_bytes += len(result)
        if processed_bytes > source_size:
            tail = processed_bytes - source_size
            result = result[:-tail]
        fdst.write(bytearray(result))
        pbar.update(reader.chunk_size)
