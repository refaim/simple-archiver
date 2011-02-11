# -*- coding: utf-8 -*-

ONE_MBYTE = 2 ** 20
DEFAULT_COEF = 10
DEFAULT_BUF_SIZE = DEFAULT_COEF * ONE_MBYTE

class BufferedReader(object):
    def __init__(self, fobj, bufsize=DEFAULT_BUF_SIZE):
        self.fobj = fobj
        self.bufsize = bufsize

    def __iter__(self):
        self.chunk = self.fobj.read(self.bufsize)
        while self.chunk:
            yield self.chunk
            self.chunk = self.fobj.read(self.bufsize)

    @property
    def chunk_size(self):
        return len(self.chunk)

def calc_buffer_size(path):
    fsize = os.path.getsize(path)
    if fsize < DEFAULT_BUF_SIZE * DEFAULT_COEF:
        if fsize < ONE_MBYTE:
            return fsize
        return fsize / DEFAULT_COEF
    return reader.DEFAULT_BUFFER_SIZE
