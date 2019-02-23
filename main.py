#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Uses the PNG Parser class to parse a PNG file.
    Kinda meant as an example.

    Date: February 14th 2019
    Author: Spencer Walden
"""

from png_parser import PNGParser

def main(infile, outfile):
    pngp = PNGParser(filename=infile)
    output = pngp.get_bytes()

    with open(outfile, 'wb') as out:
        out.write(output)

    return 

def cli():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--infile', help='name/path to the file you want to manipulate')
    ap.add_argument('-o', '--outfile', default='out.png', help='name/path of the file you want written out to')
    args = ap.parse_args()
    return {
        'infile': args.infile,
        'outfile': args.outfile
    }

if __name__ == '__main__':
    main(**cli())

