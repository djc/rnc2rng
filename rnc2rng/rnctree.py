#!/usr/bin/env python
# Convert an RELAX NG compact syntax schema to a Node tree
# This file released to the Public Domain by David Mertz
from __future__ import generators
import sys
from rnc_tokenize import token_list

class ParseError(SyntaxError):
    pass

for t in """
  ANY SOME MAYBE ONE BODY ANNOTATION ELEM EQUAL ATTR GROUP LITERAL
  NAME COMMENT TEXT EMPTY INTERLEAVE CHOICE SEQ ROOT
  DEFAULT_NS NS DATATYPES DATATAG PATTERN DEFINE STRING
  """.split():
      globals()[t] = t

PAIRS = {
    'BEG_BODY': ('END_BODY', BODY),
    'BEG_PAREN': ('END_PAREN', GROUP),
    'BEG_ANNO': ('END_ANNO', ANNOTATION),
}
TAGS = {ONE: 'group', SOME: 'oneOrMore', MAYBE: 'optional', ANY: 'zeroOrMore'}

ANNO_NS = 'http://relaxng.org/ns/compatibility/annotations/1.0'
TYPELIB_NS = 'http://www.w3.org/2001/XMLSchema-datatypes'

try:
    enumerate
except:
    enumerate = lambda seq: zip(range(len(seq)), seq)

class Node(object):
    __slots__ = ('type', 'value', 'name', 'quant')

    def __iter__(self): yield self
    __len__ = lambda self: 1

    def __init__(self, type='', value=[], name=None, quant=ONE):
        self.type = type
        self.value = value
        self.name = name
        self.quant = quant

    def __repr__(self):
        return "Node(%s, %r, %r, %s)" % (self.type, self.name,
                                         self.value, self.quant)

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
                key, val = n.value.split('=')
                ns[key.strip()] = val.strip(' "')

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

    def quant_start(self, x, write, indent, explicit=False):
        if x.quant == ONE and not explicit:
            return indent
        write('  ' * indent + '<%s>' % TAGS[x.quant])
        return indent + 1

    def quant_end(self, x, write, indent, explicit=False):
        if x.quant == ONE and not explicit:
            return indent
        write('  ' * (indent - 1) + '</%s>' % TAGS[x.quant])
        return indent - 1

    def xmlnode(self, node, indent=0):
        out = []
        write = out.append
        for x in node.value:
            if not isinstance(x, Node):
                raise TypeError("Unhappy Node.value: " + repr(x))
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
            elif x.type == NAME:
                indent = self.quant_start(x, write, indent)
                write('  ' * indent + '<ref name="%s"/>' % x.value)
                indent = self.quant_end(x, write, indent)
            elif x.type == COMMENT:
                write('  ' * indent + '<!-- %s -->' % x.value)
            elif x.type == LITERAL:
                write('  ' * indent + '<value>%s</value>' % x.value)
            elif x.type == ANNOTATION:
                self.needs['anno'] = True
                write('  ' * indent +
                      '<a:documentation>%s</a:documentation>' % x.value)
            elif x.type == INTERLEAVE:
                write('  ' * indent + '<interleave>')
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</interleave>')
            elif x.type == CHOICE:
                write('  ' * indent + '<choice>')
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</choice>')
            elif x.type == GROUP:
                indent = self.quant_start(x, write, indent, True)
                write(self.xmlnode(x, indent))
                indent = self.quant_end(x, write, indent, True)
            elif x.type == TEXT:
                write('  ' * indent + '<text/>')
            elif x.type == EMPTY:
                write('  ' * indent + '<empty/>')
            elif x.type == SEQ:
                write(self.xmlnode(x, indent))
            elif x.type == STRING:
                write('  ' * indent + '<data type="string"/>')
            elif x.type == DATATAG:
                self.needs['types'] = True
                if x.name is None:      # no paramaters
                    write('  ' * indent + '<data type="%s"/>' % x.value)
                else:
                    write('  ' * indent + '<data type="%s">' % x.name)
                    for key, val in x.value.iteritems():
                        p = '<param name="%s">%s</param>' % (key, val)
                        write('  ' * (indent + 1) + p)
                    write('  ' * indent + '</data>')
            elif x.type == ELEM:
                indent = self.quant_start(x, write, indent)
                write('  ' * indent + '<element>')
                if x.name == '*':
                    write('  ' * (indent + 1) + '<anyName/>')
                else:
                    name = '<name>%s</name>' % x.name
                    write('  ' * (indent + 1) + name)
                write(self.xmlnode(x, indent + 1))
                write('  ' * indent + '</element>')
                indent = self.quant_end(x, write, indent)
            elif x.type == ATTR:
                if x.quant == MAYBE:
                    write('  ' * indent + '<%s>' % TAGS[x.quant])

                if isinstance(x.value, Node) and x.value.type == CHOICE:
                    write('  ' * indent + '<attribute name="%s">' % x.name)
                    write('  ' * (indent + 1) + '<choice>')
                    write(self.xmlnode(x.value, indent + 2))
                    write('  ' * (indent + 1) + '</choice>')
                    write('  ' * indent + '</attribute>')
                elif x.value[0].type == TEXT:
                    write('  ' * indent + '<attribute name="%s"/>' % x.name)
                elif x.value[0].type == EMPTY:
                    write('  ' * indent + '<attribute name="%s">' % x.name)
                    write('  ' * (indent + 1) + '<empty/>')
                    write('  ' * indent + '</attribute>')
                elif x.value[0].type == LITERAL:
                    write('  ' * indent + '<attribute name="%s">' % x.name)
                    write('  ' * (indent + 1) + '<value>' +
                          x.value[0].value + '</value>')
                    write('  ' * indent + '</attribute>')
                elif x.value[0].type == NAME:
                    write('  ' * indent + '<attribute name="%s">' % x.name)
                    write(self.xmlnode(x, indent + 1))
                    write('  ' * indent + '</attribute>')
                elif x.value[0].type in (DATATAG, STRING):
                    write('  ' * indent + '<attribute name="%s">' % x.name)
                    write(self.xmlnode(x, indent + 1))
                    write('  ' * indent + '</attribute>')
                else:
                    assert False, x.value

                if x.quant == MAYBE:
                    write('  ' * indent + '</%s>' % TAGS[x.quant])

        return '\n'.join(out)

def findmatch(beg, nodes, offset):
    level = 1
    end = PAIRS[beg][0]
    for i, t in enumerate(nodes[offset:]):
        if t.type == beg:
            level += 1
        elif t.type == end:
            level -= 1
        if level == 0:
            return i + offset
    raise EOFError("No closing token encountered for %s @ %d"
                   % (beg, offset))

def match_pairs(nodes):
    newnodes = []
    i = 0
    while 1:
        if i >= len(nodes):
            break
        node = nodes[i]
        if node.type in PAIRS.keys():
            # Look for enclosing brackets
            match = findmatch(node.type, nodes, i + 1)
            matchtype = PAIRS[node.type][1]
            node = Node(type=matchtype, value=nodes[i + 1:match])
            node.value = match_pairs(node.value)
            newnodes.append(node)
            i = match + 1
        else:
            newnodes.append(node)
            i += 1
        if i >= len(nodes):
            break
    nodes[:] = newnodes
    return nodes

def type_bodies(nodes):
    newnodes = []
    i = 0
    while 1:
        if i >= len(nodes):
            break
        if nodes[i].type in (ELEM, ATTR):
            assert nodes[i + 2].type == BODY, nodes[i + 2]
            name, body = nodes[i + 1].value, nodes[i + 2]
            value, quant = type_bodies(body.value), body.quant
            node = Node(nodes[i].type, value, name, quant)
            newnodes.append(node)
            i += 3
        elif (nodes[i].type == DATATAG and (len(nodes) > i + 1 and
              nodes[i + 1].type in (PATTERN, BODY))):
            params = {}
            if nodes[i + 1].type == PATTERN:
                params['pattern'] = nodes[i + 1].value
            else:
                cur = []
                for p in nodes[i + 1].value:
                    if p.type == SEQ:
                        assert not len(cur), cur
                        continue
                    if len(cur) < 2:
                        cur.append(p)
                        continue
                    cur.append(p)
                    assert cur[0].type == NAME, cur[0]
                    assert cur[1].type == EQUAL, cur[1]
                    assert cur[2].type == LITERAL, cur[2]
                    params[cur[0].value] = cur[2].value
                    cur = []
                assert not len(cur), cur
            node = Node(DATATAG, params, nodes[i].value)
            newnodes.append(node)
            i += 2
        else:
            if nodes[i].type == GROUP:   # Recurse into groups
                value = type_bodies(nodes[i].value)
                nodes[i] = Node(GROUP, value, None, nodes[i].quant)
            newnodes.append(nodes[i])
            i += 1
        if i < len(nodes) and nodes[i].type in (ANY, SOME, MAYBE):
            newnodes[-1].quant = nodes[i].type
            i += 1
    nodes[:] = newnodes
    return nodes

def nest_defines(nodes):
    "Attach groups to named patterns"
    newnodes = []
    i = 0
    while 1:
        if i >= len(nodes):
            break
        node = nodes[i]
        newnodes.append(node)
        if node.type == DEFINE:
            group = []
            while (i + 1) < len(nodes) and nodes[i + 1].type != DEFINE:
                group.append(nodes[i + 1])
                i += 1
            node.name = node.value
            node.value = group
        i += 1
    nodes[:] = newnodes
    return nodes

def intersperse(nodes):
    "Look for interleaved, choice, or sequential nodes in groups/bodies"
    for node in nodes:
        if node.type in (ELEM, ATTR, GROUP, LITERAL):
            val = node.value
            ntypes = [n.type for n in val if not isinstance(val, str)]
            inters = [t for t in ntypes if t in (INTERLEAVE, CHOICE, SEQ)]
            inters = dict(zip(inters, [0] * len(inters)))
            if len(inters) > 1:
                raise ParseError("Ambiguity in sequencing: %s" % node)
            if len(inters) > 0:
                intertype = inters.keys()[0]
                items = []
                for pat in node.value:
                    if pat.type <> intertype:
                        items.append(pat)
                node.value = Node(intertype, items)
        if not isinstance(node.value, (str, dict)): # No recurse to terminal str
            intersperse(node.value)
    return nodes

def scan_NS(nodes):
    "Look for any namespace configuration lines"
    defines, rules = [], []
    for i, node in enumerate(nodes):
        if node.type in (DEFAULT_NS, NS, DATATYPES, ANNOTATION):
            continue
        elif node.type == DEFINE:
            defines.append((i, node))
        elif node.type == ELEM:
            rules.append((i, node))
        else:
            raise ParseError('no non-element tokens allowed at top level')

    if defines and rules:
        raise ParseError('cannot have defines and top-level pattern')
    if len(rules) > 1:
        raise ParseError('only one top-level pattern allowed')
    if rules:
        node = Node(DEFINE, rules[0][1], 'start')
        nodes[rules[0][0]] = node

def make_nodetree(tokens):
    nodes = [Node(t.type, t.value) for t in tokens]
    match_pairs(nodes)
    type_bodies(nodes)
    nest_defines(nodes)
    intersperse(nodes)
    scan_NS(nodes)
    root = Node(ROOT, nodes)
    return root

def tree(src):
    return make_nodetree(token_list(src))
