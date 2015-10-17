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

QUANTS = {SOME: 'oneOrMore', MAYBE: 'optional', ANY: 'zeroOrMore'}
ANNO_NS = 'http://relaxng.org/ns/compatibility/annotations/1.0'
TYPELIB_NS = 'http://www.w3.org/2001/XMLSchema-datatypes'

class XMLSerializer(object):

    def __init__(self, indent='  '):
        self.indent = indent
        self.reset()

    def reset(self):
        self.buf = []
        self.needs = {}
        self.ns = {}
        self.default = ''
        self.level = 0

    def write(self, s):
        self.buf.append(self.indent * self.level + s)

    def toxml(self, node):

        self.reset()
        types = None
        for n in node.value:
            if n.type == DATATYPES:
                types = n.value.strip('"')
            elif n.type == DEFAULT_NS:
                self.default = n.value.strip('"')
                if n.name is not None:
                    self.ns[n.name] = n.value.strip(' "')
            elif n.type == NS:
                self.ns[n.name] = n.value.strip(' "')

        prelude = ['<?xml version="1.0" encoding="UTF-8"?>']
        prelude.append('<grammar xmlns="http://relaxng.org/ns/structure/1.0"')
        if self.default:
            prelude.append('         ns="%s"' % self.default)
        for ns, url in self.ns.items():
            prelude.append('         xmlns:%s="%s"' % (ns, url))

        self.xmlnode(node.value)
        if 'a' not in self.ns and self.needs.get('anno'):
            prelude.append('         xmlns:a="%s"' % ANNO_NS)
        if types is not None or self.needs.get('types'):
            url = types if types is not None else TYPELIB_NS
            prelude.append('         datatypeLibrary="%s"' % url)

        prelude[-1] = prelude[-1] + '>'
        self.write('</grammar>')
        return '\n'.join(prelude + self.buf)

    def xmlnode(self, node, indent=True):
        if indent:
            self.level += 1
        for x in node:
            if not isinstance(x, parser.Node):
                raise TypeError("Unhappy Node.value: " + repr(x))
            elif x.type in set([DATATYPES, DEFAULT_NS, NS]):
                continue
            elif x.type == DEFINE:
                if x.name == 'start':
                    self.write('<start>')
                else:
                    self.write('<define name="%s">' % x.name)
                self.xmlnode(x.value)
                if x.name == 'start':
                    self.write('</start>')
                else:
                    self.write('</define>')
            elif x.type in set([MAYBE, SOME, ANY]):
                self.write('<%s>' % QUANTS[x.type])
                self.xmlnode(x.value)
                self.write('</%s>' % QUANTS[x.type])
            elif x.type in set([INTERLEAVE, CHOICE, MIXED, LIST, DIV]):
                self.write('<%s>' % x.type.lower())
                self.xmlnode(x.value)
                self.write('</%s>' % x.type.lower())
            elif x.type == EXCEPT:
                self.write('<except>')
                self.xmlnode(x.value)
                self.write('</except>')
            elif x.type == NAME:
                if x.value is not None:
                    self.write('<anyName>')
                    self.xmlnode(x.value)
                    self.write('</anyName>')
                elif x.name == '*':
                    self.write('<anyName/>')
                else:
                    self.write('<name>%s</name>' % x.name)
            elif x.type == REF:
                self.write('<ref name="%s"/>' % x.value)
            elif x.type == PARENT:
                self.write('<parent name="%s"/>' % x.value)
            elif x.type == LITERAL:
                self.write('<value>%s</value>' % x.name)
            elif x.type == ANNOTATION:
                params = ['%s="%s"' % (n.name, n.value) for n in x.value]
                self.write('<%s %s/>' % (x.name, ' '.join(params)))
            elif x.type == DOCUMENTATION:
                self.needs['anno'] = True
                fmt = '<a:documentation>%s</a:documentation>'
                self.write(fmt % x.name[2:].strip())
                self.xmlnode(x.value, False)
            elif x.type == GROUP:
                self.xmlnode(x.value, False)
            elif x.type in set([TEXT, EMPTY, NOTALLOWED]):
                self.write('<%s/>' % x.type.lower())
            elif x.type == SEQ:
                self.xmlnode(x.value, False)
            elif x.type == DATATAG:
                self.needs['types'] = True
                if x.value is None:      # no paramaters
                    self.write('<data type="%s"/>' % x.name)
                else:
                    name = x.name
                    if name not in ('string', 'token'):
                        name = x.name.split(':', 1)[1]
                    self.write('<data type="%s">' % name)
                    self.xmlnode(x.value)
                    self.write('</data>')
            elif x.type == PARAM:
                self.write('<param name="%s">%s</param>' % (x.name, x.value))
            elif x.type == ELEM:
                self.write('<element>')
                self.xmlnode(x.name)
                self.xmlnode(x.value)
                self.write('</element>')
            elif x.type == ATTR:
                self.write('<attribute>')
                self.xmlnode(x.name)
                self.xmlnode(x.value)
                self.write('</attribute>')
            else:
                assert False, x
        if indent:
            self.level -= 1

def tree(src):
    return parser.parse(src)
