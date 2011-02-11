#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import optparse
import locale

import console
import reader

COMPRESSION_METHODS = (
    'huffman',
    'rle',
)

class ArchiverException(Exception): pass

def error(message):
    print(u'sar: %s' % message)
    return 1

def main():
    oparser = optparse.OptionParser(usage='%prog [options] <archive> [files]')
    oparser.disable_interspersed_args()

    oparser.add_option('-c', '--create', action='store_true', default=False,
        help='create archive')
    oparser.add_option('-x', '--extract', action='store_true', default=False,
        help='extract files from archive')
    oparser.add_option('-m', '--method', default='rle',
        help='compression method [{0}] (%default by default)'.format(
            '|'.join(COMPRESSION_METHODS)))

    (options, args) = oparser.parse_args()
    if not (options.create or options.extract):
        oparser.error('')
        # !!!
    if options.create and options.extract:
        oparser.error('')
        # !!!
    if options.method not in COMPRESSION_METHODS:
        oparser.error('Unknown compression method: %s' % options.method)
    if (options.create and len(args) < 2):# or (options.extract and len(args) > 1):
        oparser.error('Wrong number of arguments')
    args = [os.path.abspath(arg).decode(locale.getpreferredencoding())
        for arg in args]
    archive = args[0]
    archive_dir = os.path.dirname(archive)

    # !!!
    files = args[1:]

    if options.extract:
        if not os.access(archive_dir, os.R_OK):
            return error(u'Not enough rights for reading from %s' % archive_dir)
    else:
        if not os.access(archive_dir, os.W_OK):
            return error(u'Not enough rights for writing to %s' % archive_dir)
        #files = args[1:]
        for path in files:
            if not os.access(path, os.R_OK):
                return error(u'Not enough rights for reading from %s' % path)

    worker = __import__('algorithms.%s' % options.method, fromlist=['algorithms'])

    if options.create:
        src = files[0]
        dst = archive
        handler = worker.compress
    else:
        src = archive
        dst = files[0]
        handler = worker.decompress

    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            freader = reader.BufferedReader(fsrc, reader.calc_buffer_size(src))
            pbar = console.ProgressBar(maxval=os.path.getsize(src))
            pbar.start()
            handler(freader, fdst, pbar)
            pbar.finish()

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Interrupted by user'.ljust(console.getTerminalWidth()))
    except ArchiverException, ex:
        print(ex.args[0])
    sys.exit(1)
