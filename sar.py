#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import optparse
import locale

import reader
from common import ArchiverException
from utils import console

COMPRESSION_METHODS = (
    'huffman',
    'rle',
)

def check_access(path, mode):
    strings = {
        os.R_OK: 'reading from',
        os.W_OK: 'writing to',
    }
    if not os.access(path, mode):
        raise ArchiverException(
            u'Not enough rights for %s %s' % (strings[mode], path))

def check_existence(path):
    if not os.path.exists(path):
        raise ArchiverException(u'File not found: %s' % path)

def main():
    oparser = optparse.OptionParser(usage='%prog -f <archive> [options] [files...]')
    oparser.disable_interspersed_args()

    optgroup = optparse.OptionGroup(oparser, 'Operations')
    optgroup.add_option('-c', '--create', action='store_true', default=False,
        help='create archive')
    optgroup.add_option('-x', '--extract', action='store_true', default=False,
        help='extract files from archive')
    oparser.add_option_group(optgroup)

    oparser.add_option('-m', '--method', default='rle',
        help='compression method [{0}] (%default by default)'.format(
            '|'.join(COMPRESSION_METHODS)))
    oparser.add_option('-f', '--file', dest='archive', metavar='FILE',
        help='archive file name')

    (options, args) = oparser.parse_args()

    if not (options.create or options.extract):
        oparser.error('Missing operation')
    if options.create and options.extract:
        oparser.error('Only one operation must be specified')
    if not options.archive:
        oparser.error('Missing archive file name')
    if options.extract:
        check_existence(options.archive)
        check_access(options.archive, os.R_OK)

    if options.method not in COMPRESSION_METHODS:
        oparser.error(u'Unknown compression method: %s' % options.method)
    compressor = __import__('algorithms.%s' % options.method, fromlist=['algorithms'])

    work_dir = os.path.dirname(options.archive) or os.getcwd()
    check_access(work_dir, os.R_OK)
    check_access(work_dir, os.W_OK)

    if options.extract:
        process = compressor.uncompress
        # temporary
        src = options.archive
        dst = options.archive + '.ex'
    else:
        process = compressor.compress
        if not args:
            oparser.error('Wrong number of arguments')
        else:
            for arg in args:
                check_existence(arg)
                check_access(arg, os.R_OK)
        # temporary
        src = args[0]
        dst = options.archive

    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            freader = reader.BufferedReader(fsrc, reader.calc_buffer_size(src))
            pbar = console.ProgressBar(maxval=os.path.getsize(src))
            pbar.start()
            process(freader, fdst, pbar)
            pbar.finish()

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.writeline('Interrupted by user')
    except ArchiverException, ex:
        console.writeline(
            u'%s: error: %s' % (os.path.basename(__file__), ex.args[0]))
    sys.exit(1)
