#!/usr/bin/env python
from . import parser, serializer
import sys

def main():

    args = sys.argv[1:]
    input = open(args[0]) if len(args) > 0 else sys.stdin
    xml = serializer.XMLSerializer().toxml(parser.parse(input))
    if len(args) > 1:
        open(sys.argv[2], 'w').write(xml + '\n')
    else:
        print xml

if __name__ == '__main__':
    main()
