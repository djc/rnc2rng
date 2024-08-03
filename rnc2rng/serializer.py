# Convert an RELAX NG compact syntax schema to a Node tree
# This file released to the Public Domain by David Mertz
from . import parser
from rnc2rng.parser import (
    ANNO_ATTR, ANNOTATION, ANY, ASSIGN, ATTR, CHOICE, DATATAG, DATATYPES,
    DEFAULT_NS, DEFINE, DIV, DOCUMENTATION, ELEM, EMPTY, EXCEPT, GRAMMAR,
    GROUP, INTERLEAVE, LIST, LITERAL, MAYBE, MIXED, NAME, NOT_ALLOWED, NS,
    PARAM, PARENT, REF, ROOT, SEQ, SOME, TEXT, LITERAL_TYPE
)

import html

QUANTS = {SOME: 'oneOrMore', MAYBE: 'optional', ANY: 'zeroOrMore'}
TYPELIBS = {
    'xsd': 'http://www.w3.org/2001/XMLSchema-datatypes'
}
NAMESPACES = {
    'a': 'http://relaxng.org/ns/compatibility/annotations/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
}

class XMLSerializer(object):

    def __init__(self, indent=None):
        self.indent = indent or '  '
        self.reset()

    def reset(self):
        self.buf = []
        self.ns = {}
        self.typelibs = {}
        self.default = ''
        self.level = 0

    def write(self, s):
        self.buf.append(self.indent * self.level + s)

    def datatype_library(self, prefix):
        assert prefix in self.typelibs or prefix in TYPELIBS, prefix
        if prefix not in self.typelibs:
            self.typelibs[prefix] = TYPELIBS[prefix]
        return self.typelibs[prefix]

    def namespace(self, ns):
        assert ns in self.ns or ns in NAMESPACES, ns
        if ns not in self.ns:
            self.ns[ns] = NAMESPACES[ns]
        return self.ns[ns]

    def toxml(self, node):

        self.reset()
        for n in node.value:
            if n.type == DATATYPES:
                self.typelibs[n.name] = n.value[0]
            elif n.type == DEFAULT_NS:
                self.default = n.value[0]
                if n.name is not None:
                    self.ns[n.name] = n.value[0]
            elif n.type == NS:
                self.ns[n.name] = n.value[0]

        prelude = ['<?xml version="1.0" encoding="UTF-8"?>']
        prelude.append('<grammar xmlns="http://relaxng.org/ns/structure/1.0"')
        if self.default and self.default != 'inherit':
            prelude.append('         ns="%s"' % self.default)

        self.visit(node.value)
        for ns, url in sorted(self.ns.items()):
            if url and url != 'inherit':
                prelude.append('         xmlns:%s="%s"' % (ns, url))

        # if xsd:* ever referenced, print it at the grammar level
        if 'xsd' in self.typelibs:
            prelude.append('         datatypeLibrary="%s"' % self.typelibs['xsd'])

        prelude[-1] = prelude[-1] + '>'
        self.write('</grammar>')
        return '\n'.join(prelude + self.buf)

    def anno_attrs(self, nodes):
        select = lambda n: isinstance(n, parser.Node) and n.type == ANNO_ATTR
        pairs = [(n.name, html.escape(n.value[0])) for n in nodes if select(n)]
        if not pairs:
            return ''
        return ' ' + ' '.join('%s="%s"' % attr for attr in pairs)

    def type_attrs(self, name):
        if ':' in name:
            prefix, name = name.split(':', 1)
            ns = self.datatype_library(prefix)
        else:
            assert name in ('string', 'token') # these are the only "built-in" datatypes
            ns = ""

        attrs = ' type="%s"' % name
        if ns != TYPELIBS['xsd']:
            attrs += ' datatypeLibrary="%s"' % ns # write all exceptions explicitly
        return attrs

    def visit(self, nodes, ctx=None, indent=True):
        '''Visiting a list of nodes, writes out the XML content to the internal
        line-based buffer. By default, adds one level of indentation to the
        output compared to the caller's level; passing False as the second
        argument will prevent this from happening.'''
        if indent:
            self.level += 1
        for x in nodes:

            if not isinstance(x, parser.Node):
                raise TypeError("Not a Node: " + repr(x))
            elif x.type in set([ANNO_ATTR, LITERAL_TYPE, DATATYPES, DEFAULT_NS, NS]):
                continue

            attribs = self.anno_attrs(x.value)
            if x.type == DEFINE:
                for op in (x.name for x in x.value if x.type == 'ASSIGN'):
                    modes = {'|=': 'choice', '&=': 'interleave'}
                    if op in modes:
                        attribs = (' combine="%s"' % modes[op]) + attribs
                    break;

                if x.name == 'start':
                    self.write('<start%s>' % attribs)
                else:
                    bits = x.name, attribs
                    self.write('<define name="%s"%s>' % bits)

                self.visit(x.value)
                if x.name == 'start':
                    self.write('</start>')
                else:
                    self.write('</define>')

            elif x.type == ASSIGN:
                self.visit(x.value, indent=False)
            elif x.type == GRAMMAR:
                self.write('<grammar>')
                self.visit(x.value)
                self.write('</grammar>')
            elif x.type in set([MAYBE, SOME, ANY]):
                self.write('<%s>' % QUANTS[x.type])
                self.visit(x.value)
                self.write('</%s>' % QUANTS[x.type])
            elif x.type in set([INTERLEAVE, CHOICE, MIXED, LIST, DIV]):
                self.write('<%s>' % x.type.lower())
                self.visit(x.value)
                self.write('</%s>' % x.type.lower())
            elif x.type == EXCEPT:
                self.write('<except>')
                self.visit(x.value, ctx=ctx)
                self.write('</except>')
            elif x.type == NAME:
                if not x.value and '*' in x.name:
                    if x.name == '*':
                        self.write('<anyName/>')
                    else:
                        uri = self.ns[x.name.split(':', 1)[0]]
                        self.write('<nsName ns="%s"/>' % uri)
                elif x.value:
                    if x.name == '*':
                        self.write('<anyName>')
                    else:
                        uri = self.ns[x.name.split(':', 1)[0]]
                        self.write('<nsName ns="%s">' % uri)
                    self.visit(x.value, ctx=ctx)
                    if x.name == '*':
                        self.write('</anyName>')
                    else:
                        self.write('</nsName>')
                else:
                    ns = '' if ctx == 'ATTR' else self.default
                    name = x.name
                    if ':' in name:
                        parts = x.name.split(':', 1)
                        ns = self.namespace(parts[0])
                        name = parts[1]
                    if ns == 'inherit':
                        self.write('<name>%s</name>' % name)
                    else:
                        self.write('<name ns="%s">%s</name>' % (ns, name))
            elif x.type in set([REF, PARENT]):
                bits = x.type.lower(), x.name, attribs
                if not x.value: # no parameters
                    self.write('<%s name="%s"%s/>' % bits)
                else:
                    self.write('<%s name="%s"%s>' % bits)
                    self.visit(x.value)
                    self.write('</%s>' % x.type.lower())
            elif x.type == LITERAL:
                types = [n.name for n in x.value if isinstance(n, parser.Node) and n.type == LITERAL_TYPE]
                if types:
                    assert len(types) == 1
                    attribs += self.type_attrs(types[0])

                bits = attribs, html.escape(x.name)

                self.write('<value%s>%s</value>' % bits)
                self.visit(x.value, indent=False)
            elif x.type == ANNOTATION:

                literals, rest = [], []
                for n in x.value:
                    if n.type == LITERAL:
                        literals.append(n.name)
                    elif n.type != ANNO_ATTR:
                        rest.append(n)

                end = '/' if not (literals or rest) else ''
                tail = ''
                if literals and not rest:
                    tail = html.escape(''.join(literals)) + '</%s>' % x.name

                bits = x.name, attribs, end, tail

                if ':' in x.name:
                    parts = x.name.split(':', 1)
                    ns = self.namespace(parts[0])

                self.write('<%s%s%s>%s' % bits)
                if not rest:
                    continue

                for n in x.value:
                    if n.type == ANNO_ATTR:
                        continue
                    elif n.type == LITERAL:
                        self.level += 1
                        self.write(html.escape(n.name))
                        self.level -= 1
                    else:
                        self.visit([n])

                self.write('</%s>' % x.name)

            elif x.type == DOCUMENTATION:
                xmlns_attr = ''
                if self.namespace('a') != NAMESPACES['a']:
                    xmlns_attr = ' xmlns:a="%s"' % NAMESPACES['a'] # the user is already using namespace a: for something else

                fmt = '<a:documentation%s>%s</a:documentation>'
                self.write(fmt % (xmlns_attr, html.escape('\n'.join(x.value))))
            elif x.type == GROUP:
                if len(x.value) == 1 and x.value[0].type != SEQ:
                    self.visit(x.value, indent=False)
                else:
                    self.write('<%s>' % x.type.lower())
                    self.visit(x.value)
                    self.write('</%s>' % x.type.lower())
            elif x.type == NOT_ALLOWED:
                self.write('<notAllowed/>')
            elif x.type in set([TEXT, EMPTY]):
                self.write('<%s/>' % x.type.lower())
            elif x.type == SEQ:
                self.visit(x.value, indent=False)
            elif x.type == DATATAG:
                if not x.value: # no parameters
                    self.write('<data%s/>' % self.type_attrs(x.name))
                else:
                    self.write('<data%s>' % self.type_attrs(x.name))
                    self.visit(x.value)
                    self.write('</data>')
            elif x.type == PARAM:
                bits = x.name, html.escape(x.value[0])
                self.write('<param name="%s">%s</param>' % bits)
            elif x.type == ELEM:
                self.write('<element%s>' % attribs)
                self.visit(x.value)
                self.write('</element>')
            elif x.type == ATTR:
                self.write('<attribute%s>' % attribs)
                self.visit(x.value, ctx=x.type)
                self.write('</attribute>')
            elif x.type == ROOT:
                for n in x.value:
                    # Record included document's custom datatypes
                    if n.type == DATATYPES:
                        self.typelibs[n.name] = n.value[0]
                    
                    # Verify the included document has the same metadata
                    if n.type == DEFAULT_NS:
                        assert self.default == n.value[0]
                    elif n.type == NS:
                        assert n.name in self.ns
                        assert self.ns[n.name] == n.value[0]
                self.visit(x.value, indent=False)
            else:
                assert False, x
        if indent:
            self.level -= 1
