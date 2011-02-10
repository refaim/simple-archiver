
DEFAULT_BUF_SIZE = 10 * (2 ** 20) # 10 mb

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
