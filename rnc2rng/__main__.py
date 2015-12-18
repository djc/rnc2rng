#!/usr/bin/env python
from __future__ import print_function
from . import parser, serializer
import sys

def main():

    args = sys.argv[1:]
    input = open(args[0]) if len(args) > 0 else sys.stdin
    try:
        xml = serializer.XMLSerializer().toxml(parser.parse(f=input))
    except parser.ParseError as e:
        print('parse error ' + e.msg)
        sys.exit(1)

    if len(args) > 1:
        open(sys.argv[2], 'w').write(xml + '\n')
    else:
        print(xml)

if __name__ == '__main__':
    main()
