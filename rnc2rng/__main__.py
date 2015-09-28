#!/usr/bin/env python
import sys
from rnctree import make_nodetree, token_list

def main():

    args = sys.argv[1:]
    if len(args) > 0:
        tokens = token_list(open(args[0]).read())
    else:
        tokens = token_list(sys.stdin.read())

    root = make_nodetree(tokens)
    if len(args) > 1:
        open(sys.argv[2], 'w').write(root.toxml())
    else:
        print root.toxml()

if __name__ == '__main__':
    main()
