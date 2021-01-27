#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path
import struct
import sys


# MATLAB: doc fread
known_matlab_types = {
    # Unsigned integers
    'uint': 'I', # 32 bits
    'uint8': 'B',
    'uint16': 'H',
    'uint32': 'I',
    'uint64': 'Q',
    'uchar': 'B',
    'unsigned char': 'B',
    'ushort': 'H',
    'ulong': None, # system-dependent
    'ubitn': None,
    # Signed integers
    'int': 'i',
    'int8': 'b',
    'int16': 'h',
    'int32': 'i',
    'int64': 'q',
    'integer*1': 'b',
    'integer*2': 'h',
    'integer*3': 'i',
    'integer*4': 'q',
    'schar': 'b',
    'signed char': 'b',
    'short': 'h',
    'long': None, # system-dependent
    'bitn': None,
    # Floating-point numbers
    'single': '',
    'double': '',
    'float': '',
    'float32': '',
    'float64': '',
    'real*4': '',
    'real*8': '',
    # Characters
    'char*1': '',
    'char': None,
    }


def matlab_format_to_struct_format(fmt):
    """Convert MATLAB fread style format to Python struct style format."""
    pass



def main():
    prog = os.path.splitext(os.path.basename(__file__))[0]

    parser = argparse.ArgumentParser(
        prog=prog,
        description='',
    )
    parser.add_argument('--input-file', required=True, help='Input file path')
    parser.add_argument('--skip-bytes',
                        type=int,
                        default=0,
                        help='Skip how many bytes at the begin of the file')
    parser.add_argument('--format',
                        help='Format string to describe the struct of each chunk')
    parser.add_argument('--endian',
                        choices=('little', 'ieee-le', 'le', 'l', 'big', 'ieee-be', 'be', 'b', 'native', 'n'),
                        default='native',
                        help='Endianess of binary data')
    parser.add_argument('--output-file', help='Output file path')
    parser.add_argument('--delimiter',
                        default=' ',
                        help='Column delimiter of output file')
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='Overwrite existing file')

    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        sys.stderr.write('Input file \'{0}\' doesn\'t exist!\n'.format(
            args.input_file))
        sys.exit(1)

    if args.skip_bytes < 0:
        sys.stderr.write('Invalid skip bytes: {0}.'.format(
            args.skip_bytes))
        sys.exit(1)

    if args.output_file and os.path.isfile(
            args.output_file) and not args.overwrite:
        sys.stderr.write('Output file \'{0}\' already exists! '
                         'Please use a different file path or specify '
                         '\'--overwrite\' on the command line.\n'.format(
                             args.output_file))
        sys.exit(1)

    if not args.delimiter:
        args.delimiter = ' '

    if args.output_file:
        output_fp = open(args.output_file, 'w', encoding='ascii')
    else:
        output_fp = sys.stdout

    if args.output_file:
        output_fp.close()


if __name__ == '__main__':
    main()


# References:
# [Need Convert Binary file to Txt file](https://stackoverflow.com/questions/5168676/need-convert-binary-file-to-txt-file)
# [python float to string without precision loss](https://stackoverflow.com/questions/38055000/python-float-to-string-without-precision-loss)
