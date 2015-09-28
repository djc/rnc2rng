#!/usr/bin/env python
from . import rnctree
import sys

def main():

    args = sys.argv[1:]
    if len(args) > 0:
        tokens = rnctree.token_list(open(args[0]).read())
    else:
        tokens = rnctree.token_list(sys.stdin.read())

    root = rnctree.make_nodetree(tokens)
    if len(args) > 1:
        open(sys.argv[2], 'w').write(root.toxml())
    else:
        print root.toxml()

if __name__ == '__main__':
    main()
