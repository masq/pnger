#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Defines a PNG file parsing class.

    Date: February 14th 2019
    Author: Spencer Walden
"""

import struct
import binascii
from enum import IntEnum

from pprint import pprint

class PNGParser():
    """
        PNG file format parser
    """
    class ChunkOrder(IntEnum):
        NONE = 0
        FIRST = 1 << 0
        BEFORE_PLTE = 1 << 1
        AFTER_PLTE = 1 << 2
        BEFORE_IDAT = 1 << 3
        IDAT = 1 << 4
        CONSECUTIVE = 1 << 5
        LAST = 1 << 6

    HEADER_MAGIC = b'\x89PNG\r\n\x1a\n'

    CHUNK_TYPES = {
        b'IHDR': {
            'mandatory': True,
            'multiplicity': False,
            'order': ChunkOrder.FIRST
        },
        b'cHRM': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_PLTE | ChunkOrder.BEFORE_IDAT
        },
        b'gAMA': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_PLTE | ChunkOrder.BEFORE_IDAT
        },
        b'iCCP': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_PLTE | ChunkOrder.BEFORE_IDAT
        },
        b'sBIT': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_PLTE | ChunkOrder.BEFORE_IDAT
        },
        b'sRGB': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_PLTE | ChunkOrder.BEFORE_IDAT
        },
        b'PLTE': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_IDAT
        },
        b'bKGD': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_IDAT | ChunkOrder.AFTER_PLTE
        },
        b'hIST': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_IDAT | ChunkOrder.AFTER_PLTE
        },
        b'tRNS': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_IDAT | ChunkOrder.AFTER_PLTE
        },
        b'pHYs': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_IDAT
        },
        b'sPLT': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.BEFORE_IDAT
        },
        b'IDAT': {
            'mandatory': True,
            'multiplicity': True,
            'order': ChunkOrder.IDAT | ChunkOrder.CONSECUTIVE
        },
        b'tIME': {
            'mandatory': False,
            'multiplicity': False,
            'order': ChunkOrder.NONE
        },
        b'iTXt': {
            'mandatory': False,
            'multiplicity': True,
            'order': ChunkOrder.NONE
        }, 
        b'tEXt': {
            'mandatory': False,
            'multiplicity': True,
            'order': ChunkOrder.NONE
        },
        b'zTXt': {
            'mandatory': False,
            'multiplicity': True,
            'order': ChunkOrder.NONE
        },
        b'IEND': {
            'mandatory': True,
            'multiplicity': False,
            'order': ChunkOrder.LAST
        },
    }

    CHUNK_TYPE_FLAGS = [
        'Ancillary',
        'Private',
        'Reserved',
        'Safe-to-Copy'
    ]

    def __init__(self, filename=None, strict=True):
        """
            Initialize the parser.
        """
        self._strict = strict
        self.filename = filename
        self.validity = {
            'header': False,
            'chunks': {
                #{k: [{
                #    'order': True,
                #    'multiplicity': True,
                #    'mandatory': True,
                #    'checksum': True
                #}] for k,_ in filter(
                #    lambda chnk: chnk['mandatory'],
                #    self.CHUNK_TYPES.keys()
                #)}
            }
        }

        self._chunks = self._parse()
        pprint(self._chunks)
        pprint(self.validity)

    def get_chunks(self):
        """
            Generates the chunks of the png
        """
        yield from self._chunks

    def get_bytes(self, type_filter=None, filter_out=True):
        """
            Generates the bytes for a PNG file with an optional filter for
            chunk types

            type_filter: list of chunk types to filter
            filter_out: boolean, default True, makes the filter filter chunk 
                        types in or filter them out.
        """
        def filter_func(chunk):
            """
                Helper function to determine if a chunk should be included
                in the output
            """
            tf = type_filter
            # If no filter is set, everything should be included
            if not isinstance(tf, list) or len(tf) < 1:
                return True

            t = chunk['type']
            fo = filter_out

            result = (t in tf or t in map(lambda x: bytes(x, 'ascii'), tf))
            print(t, not result if filter_out else result)
            return not result if filter_out else result


        with open(self.filename, 'rb') as infile:
            yield PNGParser.HEADER_MAGIC
            for chunk in filter(filter_func, self._chunks):
                infile.seek(chunk['offset'])
                yield infile.read(chunk['length'])

    def get_chunk_types(self):
        return list(self._chunks.keys())

    def _parse(self):
        """
            Parse the png data
        """
        encountered = {
            b'IHDR': 0,
            b'PLTE': 0,
            b'IDAT': 0,
            b'IEND': 0 
        }
        chunks = []
        HEADER_LEN = 8
        CLEN_LEN = 4
        CTYP_LEN = 4
        CCRC_LEN = 4

        with open(self.filename, 'rb') as png:
            # Check the header
            # TODO: get parser to run with the file missing a header?
            # Implmt notes: probably want to check if parsing that, the type 
            #               code will not be ascii
            # but there are potential problems with doing that because then the
            # chunk is also invalid... try except and make chunk['name'] validity
            # false
            self.validity['header'] = png.read(HEADER_LEN) == PNGParser.HEADER_MAGIC

            offset = HEADER_LEN
            prev_chunk_type = b''
            chunk_type = b''

            while 1:
                # Try to read data from file, break if no more
                chunk_lentyp_raw = png.read(CLEN_LEN + CTYP_LEN)
                if not chunk_lentyp_raw:
                    print('[+] End of file reached')
                    break;

                # Parse len and type out of data
                prev_chunk_type = chunk_type
                chunk_len, chunk_type = struct.unpack('>I4s', chunk_lentyp_raw)

                # Valid until proven otherwise
                self.validity['chunks'][chunk_type] = (
                    self.validity['chunks'].get(chunk_type, []) + [{
                        'order': not (self.CHUNK_TYPES[chunk_type]['order'] & PNGParser.ChunkOrder.FIRST
                                    and any(encountered.values())),
                        'multiplicity': True,
                        'mandatory': True,
                        'checksum': True
                    }]
                )

                v = self.validity['chunks'][chunk_type]
                print(v)

                # Increment number of chunks of type encountered
                encountered[chunk_type] = encountered.get(chunk_type, 0) + 1
                chunk_type_index = encountered[chunk_type] - 1

                # Perform chunk type order checks
                v[chunk_type_index]['order'] &= (
                    not (self.CHUNK_TYPES[chunk_type]['order'] & PNGParser.ChunkOrder.BEFORE_PLTE
                    and encountered.get(b'PLTE', False))

                    or

                    not (self.CHUNK_TYPES[chunk_type]['order'] & PNGParser.ChunkOrder.BEFORE_IDAT
                    and encountered.get(b'IDAT', False))

                    or

                    not (self.CHUNK_TYPES[chunk_type]['order'] & PNGParser.ChunkOrder.AFTER_PLTE
                    and not encountered.get(b'PLTE', False))
                )

                # Previous chunk order checks based on current chunk
                if prev_chunk_type:
                    self.validity['chunks'][prev_chunk_type][encountered[prev_chunk_type] - 1]['order'] &= (
                        # A chunk after alleged final chunk invalidates prev_chunk
                        not (self.CHUNK_TYPES[prev_chunk_type]['order'] & PNGParser.ChunkOrder.LAST)

                        #or 

                        # A chunk that's not the previous chunk type
                        # yet previous is supposed to have consecutive chunks of
                        # that type... something something TODO TODO TODO
                        # invalidates prev_chunk 
                        #(chunk_type != prev_chunk_type
                        #and self.CHUNK_TYPES[chunk_type]['order'] & PNGParser.ChunkOrder.CONSECUTIVE)
                    )

                # Multiplicity check
                v[chunk_type_index]['multiplicity'] &= (
                    not (encountered[chunk_type] > 1
                    and not self.CHUNK_TYPES[chunk_type]['multiplicity'])
                )

                # parse (more like pull) out the chunk_data
                chunk_data = png.read(chunk_len)

                # parse crc checksum out of data
                chunk_crc = struct.unpack('>I', png.read(CCRC_LEN))[0]
                calc_crc  = binascii.crc32(chunk_type + chunk_data) & 0xFFFFFFFF

                chunk = {
                    'offset': offset,
                    'length': chunk_len+12, # data length + length, type, crc lengths
                    'type': chunk_type,
                    'type_flags': {self.CHUNK_TYPE_FLAGS[i]: not not x & 0x20 for i,x in enumerate(chunk_type)},
                    'type_index': chunk_type_index,
                    'data_length': hex(chunk_len),
                    'data_offset': hex(offset + 8),
                    'checksum': {
                        'stored': hex(chunk_crc),
                        'calculated': hex(calc_crc)
                    },
                }

                # Check checksum validity
                v[chunk_type_index]['checksum'] = calc_crc == chunk_crc

                # Append this chunk and move our offset along
                chunks.append(chunk)
                offset += CLEN_LEN + CTYP_LEN + chunk_len + CCRC_LEN

            return chunks

