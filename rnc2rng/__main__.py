#!/usr/bin/env python
from . import rnctree
import sys

def main():

    args = sys.argv[1:]
    if len(args) > 0:
        root = rnctree.tree(open(args[0]).read())
    else:
        root = rnctree.tree(sys.stdin.read())

    xml = rnctree.XMLSerializer().toxml(root)
    if len(args) > 1:
        open(sys.argv[2], 'w').write(xml + '\n')
    else:
        print xml

if __name__ == '__main__':
    main()
