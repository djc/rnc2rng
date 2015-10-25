#!/usr/bin/env python
# Compatibility API for rnc2rng 1.0
from . import parser, serializer

class Tree(object):

    def __init__(self, root):
        self.root = root

    def toxml(self):
        return serializer.XMLSerializer().toxml(self.root)

def token_list(src):
    return parser.lex(src)

def make_nodetree(tokens):
    return Tree(parser.parser.parse(tokens, parser.State()))
