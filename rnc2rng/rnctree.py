#!/usr/bin/env python
# Convert an RELAX NG compact syntax schema to a Node tree
# This file released to the Public Domain by David Mertz
from __future__ import generators
import sys
from . import parser

class ParseError(SyntaxError):
    pass

for type in parser.NODE_TYPES:
    globals()[type] = type

TAGS = {SOME: 'oneOrMore', MAYBE: 'optional', ANY: 'zeroOrMore'}
ANNO_NS = 'http://relaxng.org/ns/compatibility/annotations/1.0'
TYPELIB_NS = 'http://www.w3.org/2001/XMLSchema-datatypes'

try:
    enumerate
except:
    enumerate = lambda seq: zip(range(len(seq)), seq)

class XMLSerializer(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.buf = []
        self.needs = {}

    def write(self, s):
        self.buf.append(s)

    def toxml(self, node):

        self.reset()
        self.xmlnode(node, 1)

        default, types, ns = None, None, {}
        for n in node.value:
            if n.type == DATATYPES:
                types = n.value.strip('"')
            elif n.type == DEFAULT_NS:
                default = n.value.strip('"')
                if n.name is not None:
                    ns[n.name] = n.value.strip(' "')
            elif n.type == NS:
                ns[n.name] = n.value.strip(' "')

        prelude = ['<?xml version="1.0" encoding="UTF-8"?>']
        prelude.append('<grammar xmlns="http://relaxng.org/ns/structure/1.0"')
        if default is not None:
            prelude.append('         ns="%s"' % default)
        if types is not None or self.needs.get('types'):
            url = types if types is not None else TYPELIB_NS
            prelude.append('         datatypeLibrary="%s"' % url)
        for ns, url in ns.items():
            prelude.append('         xmlns:%s="%s"' % (ns, url))
        if 'a' not in ns and self.needs.get('anno'):
            prelude.append('         xmlns:a="%s"' % ANNO_NS)

        prelude[-1] = prelude[-1] + '>'
        self.write('</grammar>')
        return '\n'.join(prelude + self.buf)

    def xmlnode(self, node, indent=0):
        for x in node.value:
            if not isinstance(x, parser.Node):
                raise TypeError("Unhappy Node.value: " + repr(x))
            elif x.type in set([DATATYPES, DEFAULT_NS, NS]):
                continue
            elif x.type == DEFINE:
                if x.name == 'start':
                    self.write('  ' * indent + '<start>')
                else:
                    self.write('  ' * indent + '<define name="%s">' % x.name)
                self.xmlnode(x, indent + 1)
                if x.name == 'start':
                    self.write('  ' * indent + '</start>')
                else:
                    self.write('  ' * indent + '</define>')
            elif x.type in set([MAYBE, SOME, ANY]):
                self.write('  ' * indent + '<%s>' % TAGS[x.type])
                self.xmlnode(x, indent + 1)
                self.write('  ' * indent + '</%s>' % TAGS[x.type])
            elif x.type in set([INTERLEAVE, CHOICE, EXCEPT, MIXED, LIST]):
                self.write('  ' * indent + '<%s>' % x.type.lower())
                self.xmlnode(x, indent + 1)
                self.write('  ' * indent + '</%s>' % x.type.lower())
            elif x.type == NAME:
                if x.value == '*':
                    self.write('  ' * indent + '<anyName/>')
                else:
                    self.write('  ' * indent + '<name>%s</name>' % x.value)
            elif x.type == REF:
                self.write('  ' * indent + '<ref name="%s"/>' % x.value)
            elif x.type == LITERAL:
                self.write('  ' * indent + '<value>%s</value>' % x.name)
            elif x.type == ANNOTATION:
                params = ['%s="%s"' % (n.name.value, n.value) for n in x.value]
                self.write('  ' * indent + '<%s %s/>' % (x.name, ' '.join(params)))
            elif x.type == DOCUMENTATION:
                self.needs['anno'] = True
                fmt = '<a:documentation>%s</a:documentation>'
                self.write('  ' * indent + fmt % x.name[2:].strip())
                self.xmlnode(x, indent)
            elif x.type == GROUP:
                self.xmlnode(x, indent)
            elif x.type == TEXT:
                self.write('  ' * indent + '<text/>')
            elif x.type == EMPTY:
                self.write('  ' * indent + '<empty/>')
            elif x.type == SEQ:
                self.xmlnode(x, indent)
            elif x.type == DATATAG:
                self.needs['types'] = True
                if x.value is None:      # no paramaters
                    self.write('  ' * indent + '<data type="%s"/>' % x.name)
                else:
                    name = x.name
                    if name not in ('string', 'token'):
                        name = x.name.split(':', 1)[1]
                    self.write('  ' * indent + '<data type="%s">' % name)
                    for param in x.value:
                        key, val = param.name.value, param.value
                        p = '<param name="%s">%s</param>' % (key, val)
                        self.write('  ' * (indent + 1) + p)
                    self.write('  ' * indent + '</data>')
            elif x.type == ELEM:
                self.write('  ' * indent + '<element>')
                wrapper = parser.Node(None, None, x.name)
                self.xmlnode(wrapper, indent + 1)
                self.xmlnode(x, indent + 1)
                self.write('  ' * indent + '</element>')
            elif x.type == ATTR:
                self.write('  ' * indent + '<attribute>')
                wrapper = parser.Node(None, None, x.name)
                self.xmlnode(wrapper, indent + 1)
                self.xmlnode(x, indent + 1)
                self.write('  ' * indent + '</attribute>')
            else:
                assert False, x

def tree(src):
    return parser.parse(src)
