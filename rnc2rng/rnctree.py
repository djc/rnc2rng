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
        self.needs = {}

    def toxml(self, node):

        out = []
        write = out.append
        self.needs = {}
        write(self.xmlnode(node, 1))

        default, types, ns = None, None, {}
        for n in node.value:
            if n.type == DATATYPES:
                types = n.value.strip('"')
            elif n.type == DEFAULT_NS:
                default = n.value.strip('"')
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
        out.append('</grammar>')
        return '\n'.join(prelude + out)

    def xmlnode(self, node, indent=0):
        out = []
        write = out.append
        for x in node.value:
            if not isinstance(x, parser.Node):
                raise TypeError("Unhappy Node.value: " + repr(x))
            elif x.type in set([DATATYPES, DEFAULT_NS, NS]):
                continue
            elif x.type == DEFINE:
                if x.name == 'start':
                    write('  ' * indent + '<start>')
                else:
                    write('  ' * indent + '<define name="%s">' % x.name)
                write(self.xmlnode(x, indent + 1))
                if x.name == 'start':
                    write('  ' * indent + '</start>')
                else:
                    write('  ' * indent + '</define>')
            elif x.type in set([MAYBE, SOME, ANY]):
                write('  ' * indent + '<%s>' % TAGS[x.type])
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</%s>' % TAGS[x.type])
            elif x.type == REF:
                write('  ' * indent + '<ref name="%s"/>' % x.value)
            elif x.type == LITERAL:
                write('  ' * indent + '<value>%s</value>' % x.name)
            elif x.type == ANNOTATION:
                params = ['%s="%s"' % (n.name.value, n.value) for n in x.value]
                write('  ' * indent + '<%s %s/>' % (x.name, ' '.join(params)))
            elif x.type == DOCUMENTATION:
                self.needs['anno'] = True
                fmt = '<a:documentation>%s</a:documentation>'
                write('  ' * indent + fmt % x.name[2:].strip())
                write(self.xmlnode(x, indent))
            elif x.type == INTERLEAVE:
                write('  ' * indent + '<interleave>')
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</interleave>')
            elif x.type == CHOICE:
                write('  ' * indent + '<choice>')
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</choice>')
            elif x.type == GROUP:
                write(self.xmlnode(x, indent))
            elif x.type == TEXT:
                write('  ' * indent + '<text/>')
            elif x.type == EMPTY:
                write('  ' * indent + '<empty/>')
            elif x.type == SEQ:
                write(self.xmlnode(x, indent))
            elif x.type == DATATAG:
                self.needs['types'] = True
                if x.value is None:      # no paramaters
                    write('  ' * indent + '<data type="%s"/>' % x.name)
                else:
                    name = x.name
                    if name not in ('string', 'token'):
                        name = x.name.split(':', 1)[1]
                    write('  ' * indent + '<data type="%s">' % name)
                    for param in x.value:
                        key, val = param.name.value, param.value
                        p = '<param name="%s">%s</param>' % (key, val)
                        write('  ' * (indent + 1) + p)
                    write('  ' * indent + '</data>')
            elif x.type == ELEM:
                write('  ' * indent + '<element>')
                if x.name.value == '*':
                    write('  ' * (indent + 1) + '<anyName/>')
                else:
                    name = '<name>%s</name>' % x.name.value
                    write('  ' * (indent + 1) + name)
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</element>')
            elif x.type == ATTR and x.value.type == TEXT:
                write('  ' * indent + '<attribute name="%s"/>' % x.name.value)
            elif x.type == ATTR:
                write('  ' * indent + '<attribute name="%s">' % x.name.value)
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</attribute>')
            else:
                assert False, x

        return '\n'.join(out)

def tree(src):
    return parser.parse(src)
