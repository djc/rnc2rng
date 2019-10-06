from __future__ import print_function

import rply, sys, os
from codecs import BOM_UTF16_BE, BOM_UTF16_LE
if sys.version_info[0] < 3:
    from urllib2 import urlopen as _urlopen
    from urlparse import urljoin
    from contextlib import closing
    def urlopen(f):
        return closing(_urlopen(f))
else:
    from urllib.request import urlopen
    from urllib.parse import urljoin

KEYWORDS = set([
    'attribute', 'datatypes', 'default', 'div', 'element', 'empty', 'external',
    'grammar', 'include', 'inherit', 'list', 'mixed', 'namespace',
    'notAllowed', 'parent', 'start', 'string', 'text', 'token',
])

NCNAME = r'[A-Za-z_][\w.-]*'

def lexer():
    lg = rply.LexerGenerator()
    lg.add('LPAREN', r'\(')
    lg.add('RPAREN', r'\)')
    lg.add('LBRACE', r'{')
    lg.add('RBRACE', r'}')
    lg.add('LBRACKET', r'\[')
    lg.add('RBRACKET', r'\]')
    lg.add('COMBINE', r'\|=|&=')
    lg.add('EQUAL', r'=')
    lg.add('PIPE', r'[|]')
    lg.add('COMMA', r',')
    lg.add('AMP', r'&')
    lg.add('MINUS', r'[-]')
    lg.add('STAR', r'[*]')
    lg.add('PLUS', r'[+]')
    lg.add('QMARK', r'[?]')
    lg.add('CNAME', r'%s:(%s|\*)' % (NCNAME, NCNAME))
    lg.add('QID', r'\\%s' % NCNAME)
    lg.add('ID', NCNAME)
    lg.add('LITERAL', r'".*?"')
    lg.add('DOCUMENTATION', r'##.*')
    lg.add('COMMENT', r'#.*')
    lg.add('TILDE', r'~')
    lg.ignore(r'\s+')
    return lg.build()

LEXER = lexer()

def lex(src):
    for t in LEXER.lex(src):
        if t.name == 'ID' and t.value in KEYWORDS:
            t.name = t.value.upper()
        elif t.name == 'LITERAL':
            t.value = t.value[1:-1]
        elif t.name == 'COMMENT':
            continue
        yield t

pg = rply.ParserGenerator([
    'AMP', 'CNAME', 'COMBINE', 'COMMA', 'DOCUMENTATION', 'EQUAL', 'ID',
    'LBRACE', 'LBRACKET', 'LPAREN', 'LIST', 'LITERAL', 'MINUS', 'MIXED',
    'PLUS', 'PIPE', 'QID', 'QMARK', 'RBRACE', 'RBRACKET', 'RPAREN', 'STAR',
    'TILDE',
] + [s.upper() for s in KEYWORDS], precedence=[("left", ['TILDE'])])


class Node(object):
    __slots__ = 'type', 'name', 'value'
    def __init__(self, type, name, value=None):
        self.type = type
        self.name = name
        self.value = value or []
        assert isinstance(self.value, list), self.value
    def __repr__(self):
        bits = [(k, getattr(self, k, None)) for k in self.__slots__]
        strs = ['%s=%r' % (k, v) for (k, v) in bits if v is not None]
        return 'Node(%s)' % ', '.join(strs)

def pprint(n, level=0):
    if isinstance(n, list):
        print('[')
        for v in n:
            pprint(v, level + 2)
        print('%s]' % (' ' * level))
    else:
        print('%s%s' % (' ' * level, n.type), end=' ')
        if n.name is not None:
            print(n.name, end=' ')
        if not n.value:
            print('[]')
        else:
            pprint(n.value, level)

NODE_TYPES = [
    'ANNO_ATTR', 'ANNOTATION', 'ANY', 'ASSIGN', 'ATTR', 'CHOICE', 'DATATAG',
    'DATATYPES', 'DEFAULT_NS', 'DEFINE', 'DIV', 'DOCUMENTATION', 'ELEM',
    'EMPTY', 'EXCEPT', 'GRAMMAR', 'GROUP', 'INTERLEAVE', 'LIST', 'LITERAL',
    'MAYBE', 'MIXED', 'NAME', 'NOT_ALLOWED', 'NS', 'PARAM', 'PARENT', 'REF',
    'ROOT', 'SEQ', 'SOME', 'TEXT',
]

for _node_type in NODE_TYPES:
    globals()[_node_type] = _node_type

@pg.production('start : preamble top-level-body')
def start(s, p):
    return Node('ROOT', None, p[0] + p[1])

@pg.production('strlit : LITERAL')
def strlit_literal(s, p): # from datatypeValue
    return p[0]

@pg.production('strlit : strlit TILDE strlit')
def strlit_concat(s, p):
    p[0].value += p[2].value
    return p[0]

@pg.production('preamble : decl preamble')
def preamble_multi(s, p):
    p[1].insert(0, p[0])
    return p[1]

@pg.production('preamble : ')
def preamble_empty(s, p):
    return []

@pg.production('decl : DEFAULT NAMESPACE EQUAL strlit')
def decl_default_ns(s, p):
    return Node('DEFAULT_NS', None, [p[3].value.strip('"')])

@pg.production('decl : DEFAULT NAMESPACE id-or-kw EQUAL strlit')
def decl_default_names_ns(s, p):
    return Node('DEFAULT_NS', p[2].name, [p[4].value.strip(' "')])

@pg.production('decl : NAMESPACE id-or-kw EQUAL strlit')
def decl_ns(s, p):
    return Node('NS', p[1].name, [p[3].value.strip(' "')])

@pg.production('decl : DATATYPES id-or-kw EQUAL strlit')
def decl_datatypes(s, p):
    return Node('DATATYPES', p[1].name, [p[3].value.strip('"')])

@pg.production('top-level-body : annotations alt-top-level')
def top_level_body(s, p):
    if isinstance(p[1], list):
        p[1][0].value = p[0] + p[1][0].value
    elif p[1].type == 'ELEM':
        p[1].value = p[0] + p[1].value
        p[1] = [Node('DEFINE', 'start', [Node('ASSIGN', '=', [p[1]])])]
    elif p[1].type == 'GRAMMAR':
        p[1].value = p[0] + p[1].value
        p[1] = [p[1]]
    return p[1]

@pg.production('alt-top-level : component grammar-content')
def top_level_grammar_content(s, p):
    p[1].insert(0, p[0])
    return p[1]

@pg.production('alt-top-level : element-primary')
def top_level_element(s, p):
    return p[0]

@pg.production('alt-top-level : grammar')
def top_level_grammar(s, p):
    return p[0]

@pg.production('grammar-content : member grammar-content')
def grammar_multi(s, p):
    p[1].insert(0, p[0])
    return p[1]

@pg.production('grammar-content : ')
def grammar_empty(s, p):
    return []

@pg.production('member : annotations component')
def member_annotated_component(s, p):
    p[1].value = p[0] + p[1].value
    return p[1]

@pg.production('member : CNAME annotation-attributes-content')
def member_foreign_element_annotation(s, p):
    return Node('ANNOTATION', p[0].value, p[1])

@pg.production('component : define')
def component_define(s, p):
    return p[0]

@pg.production('component : grammar-start')
def component_start(s, p):
    return p[0]

@pg.production('define : identifier definition')
def define(s, p):
    return Node('DEFINE', p[0].name, [p[1]])

@pg.production('grammar-start : START definition')
def grammar_start(s, p):
    return Node('DEFINE', 'start', [p[1]])

@pg.production('definition : EQUAL pattern')
def definition_equal(s, p):
    return Node('ASSIGN', p[0].value, p[1])

@pg.production('definition : COMBINE pattern')
def definition_combine(s, p):
    return Node('ASSIGN', p[0].value, p[1])

@pg.production('component : DIV LBRACE grammar-content RBRACE')
def component_div(s, p):
    return Node('DIV', None, p[2])

@pg.production('component : INCLUDE strlit opt-inherit opt-include-content')
def component_include(s, p):
    if ':' in s.path or ':' in p[1].value:  # it's a URL
        url = urljoin(s.path, p[1].value)
    else:
        url = os.path.join(s.path, p[1].value)
    return parse(f=url)

@pg.production('opt-inherit : INHERIT EQUAL id-or-kw')
def opt_inherit(s, p):
    return Node('INHERIT', p[2])

@pg.production('opt-inherit : ')
def opt_inherit_none(s, p):
    return None

@pg.production('opt-include-content : LBRACE include-body RBRACE')
def opt_include_content(s, p):
    return p[1]

@pg.production('opt-include-content : ')
def opt_include_content_none(s, p):
    return []

@pg.production('include-body : include-member include-body')
def include_content_multi(s, p):
    p[1].insert(0, p[0])
    return p[1]

@pg.production('include-body : ')
def include_content_empty(s, p):
    return []

@pg.production('include-member : annotations include-component')
def include_member(s, p):
    p[1].value = p[0] + p[1].value
    return p[1]

@pg.production('include-component : define')
def include_component_define(s, p):
    return p[0]

@pg.production('include-component : grammar-start')
def include_component_start(s, p):
    return p[0]

@pg.production('include-component : DIV LBRACE include-body RBRACE')
def include_component_div(s, p):
    return Node('DIV', None, p[2])

@pg.production('annotation-attributes-content : LBRACKET start-annotation-content RBRACKET')
def annotation_attributes_content(s, p):
    return p[1]

@pg.production('annotations : documentations LBRACKET start-annotations RBRACKET')
def annotations_multi(s, p):
    p[0] += p[2]
    return p[0]

@pg.production('annotations : documentations')
def annotations_empty(s, p):
    return p[0]

@pg.production('start-annotation-content : CNAME cname-annotation-content')
def start_annotation_content_cname(s, p):
    p[1][0].name = p[0].value
    return p[1]

@pg.production('start-annotation-content : ID EQUAL strlit start-annotation-content')
def start_annotation_content_id(s, p):
    return [Node('ANNO_ATTR', p[0].value, [p[2].value])] + p[3]

@pg.production('start-annotation-content : strlit annotation-content')
def start_annotation_content_literal(s, p):
    return [Node('LITERAL', p[0].value)] + p[1]

@pg.production('start-annotation-content : ')
def start_annotation_content_empty(s, p):
    return []

@pg.production('cname-annotation-content : EQUAL strlit start-annotation-content')
def cname_annotation_content_attribute(s, p):
    return [Node('ANNO_ATTR', None, [p[1].value])] + p[2]

@pg.production('cname-annotation-content : annotation-attributes-content annotation-content')
def cname_annotation_content_element(s, p):
    return [Node('ANNOTATION', None, p[0])] + p[1]

@pg.production('start-annotations : CNAME cname-annotations')
def start_annotations_cname(s, p):
    p[1][0].name = p[0].value
    return p[1]

@pg.production('start-annotations : ')
def start_annotations_empty(s, p):
    return []

@pg.production('cname-annotations : EQUAL strlit start-annotations')
def cname_annotations_attrib(s, p):
    return [Node('ANNO_ATTR', None, [p[1].value])] + p[2]

@pg.production('cname-annotations : annotation-attributes-content annotation-elements')
def cname_annotations_element(s, p):
    return [Node('ANNOTATION', None, p[0])] + p[1]

@pg.production('annotation-content : annotation-element annotation-content')
def annotation_content_nested(s, p):
    return [p[0]] + p[1]

@pg.production('annotation-content : strlit annotation-content')
def annotation_content_literal(s, p):
    return [Node('LITERAL', p[0].value)] + p[1]

@pg.production('annotation-content : ')
def annotation_content_empty(s, p):
    return []

@pg.production('annotation-elements : annotation-element annotation-elements')
def annotation_elements_multi(s, p):
    p[1].insert(0, p[0])
    return p[1]

@pg.production('annotation-elements : ')
def annotation_elements_empty(s, p):
    return []

@pg.production('annotation-element : CNAME annotation-attributes-content')
def nested_annotation_element(s, p):
    return Node('ANNOTATION', p[0].value, p[1])

@pg.production('pattern : particle')
def pattern_particle(s, p):
    return [p[0]]

@pg.production('pattern : particle-choice')
def pattern_choice(s, p):
    return [p[0]]

@pg.production('particle-choice : particle PIPE particle-choice')
def particle_choice_multi(s, p):
    p[2].value.insert(0, p[0])
    return p[2]

@pg.production('particle-choice : particle PIPE particle')
def particle_choice_single(s, p):
    return Node('CHOICE', None, [p[0], p[2]])

@pg.production('pattern : particle-group')
def pattern_seq(s, p):
    return [p[0]]

@pg.production('particle-group : particle COMMA particle-group')
def particle_group_multi(s, p):
    p[2].value.insert(0, p[0])
    return p[2]

@pg.production('particle-group : particle COMMA particle')
def particle_group_single(s, p):
    return Node('SEQ', None, [p[0], p[2]])

@pg.production('pattern : particle-interleave')
def pattern_interleave(s, p):
    return [p[0]]

@pg.production('particle-interleave : particle AMP particle-interleave')
def particle_interleave_multi(s, p):
    p[2].value.insert(0, p[0])
    return p[2]

@pg.production('particle-interleave : particle AMP particle')
def particle_interleave_single(s, p):
    return Node('INTERLEAVE', None, [p[0], p[2]])

@pg.production('particle : annotated-primary QMARK')
def particle_maybe(s, p):
    return Node('MAYBE', None, [p[0]])

@pg.production('particle : annotated-primary STAR')
def particle_any(s, p):
    return Node('ANY', None, [p[0]])

@pg.production('particle : annotated-primary PLUS')
def particle_some(s, p):
    return Node('SOME', None, [p[0]])

@pg.production('particle : annotated-primary')
def particle_primary(s, p):
    return p[0]

@pg.production('annotated-primary : LPAREN pattern RPAREN')
def annotated_primary_group(s, p):
    return Node('GROUP', None, p[1])

@pg.production('annotated-primary : annotations primary')
def annotated_primary_annotated(s, p):
    p[1].value = p[0] + p[1].value
    return p[1]

@pg.production('primary : element-primary')
def primary_element(s, p):
    return p[0]

@pg.production('element-primary : ELEMENT name-class LBRACE pattern RBRACE')
def element_primary(s, p):
    return Node('ELEM', None, p[1] + p[3])

@pg.production('primary : ATTRIBUTE name-class LBRACE pattern RBRACE')
def primary_attrib(s, p):
    return Node('ATTR', None, p[1] + p[3])

@pg.production('primary : MIXED LBRACE pattern RBRACE')
def primary_mixed(s, p):
    return Node('MIXED', None, p[2])

@pg.production('primary : LIST LBRACE pattern RBRACE')
def primary_list(s, p):
    return Node('LIST', None, p[2])

@pg.production('primary : strlit')
def primary_literal(s, p): # from datatypeValue
    return Node('LITERAL', p[0].value)

@pg.production('primary : CNAME')
def primary_cname(s, p):
    return Node('DATATAG', p[0].value.split(':', 1)[1])

@pg.production('primary : CNAME LBRACE params RBRACE')
def primary_type_params(s, p):
    return Node('DATATAG', p[0].value, p[2])

@pg.production('primary : STRING')
def primary_string(s, p):
    return Node('DATATAG', 'string')

@pg.production('primary : STRING strlit')
def primary_typed_string(s, p):
    return Node('DATATAG', 'string', [p[1].value])

@pg.production('primary : STRING LBRACE params RBRACE')
def primary_string_parametrized(s, p):
    return Node('DATATAG', 'string', p[2])

@pg.production('primary : TEXT')
def primary_text(s, p):
    return Node('TEXT', None)

@pg.production('primary : EMPTY')
def primary_empty(s, p):
    return Node('EMPTY', None)

@pg.production('primary : identifier')
def primary_id(s, p):
    return Node('REF', p[0].name)

@pg.production('primary : NOTALLOWED')
def primary_notallowed(s, p):
    return Node('NOT_ALLOWED', None)

@pg.production('primary : PARENT ID')
def primary_parent(s, p):
    return Node('PARENT', p[1].value)

@pg.production('primary : grammar')
def primary_grammar(s, p):
    return p[0]

@pg.production('grammar : GRAMMAR LBRACE grammar-content RBRACE')
def grammar(s, p):
    return Node('GRAMMAR', None, p[2])

@pg.production('params : params param')
def params_multi(s, p):
    p[0].append(p[1])
    return p[0]

@pg.production('params : ')
def params_empty(s, p):
    return []

@pg.production('param : id-or-kw EQUAL strlit')
def param_single(s, p):
    return Node('PARAM', p[0].name, [p[2].value])

@pg.production('name-class : simple-name-class')
def name_class_name(s, p):
    return p[0]

@pg.production('name-class : name-class-choice')
def name_class_choice(s, p):
    return p[0]

@pg.production('name-class : except-name-class')
def name_class_except(s, p):
    return p[0]

@pg.production('except-name-class : simple-name-class MINUS except-name-class')
def except_name_class_nested(s, p):
    p[0].value = p[2]
    return p[0]

@pg.production('except-name-class : simple-name-class MINUS simple-name-class')
def except_name_class_simple(s, p):
    p[0][0].value = [Node('EXCEPT', None, p[2])]
    return p[0]

@pg.production('name-class-choice : simple-name-class PIPE name-class-choice')
def name_class_choice_nested(s, p):
    p[2][0].value.insert(0, p[0][0])
    return p[2]

@pg.production('name-class-choice : simple-name-class PIPE simple-name-class')
def name_class_choice_simple(s, p):
    return [Node('CHOICE', None, p[0] + p[2])]

@pg.production('simple-name-class : STAR')
def simple_name_class_any(s, p):
    return [Node('NAME', p[0].value)]

@pg.production('simple-name-class : name')
def simple_name_class_name(s, p):
    return [p[0]]

@pg.production('simple-name-class : LPAREN name-class RPAREN')
def name_class_group(s, p):
    return p[1]

@pg.production('documentations : DOCUMENTATION documentations')
def documentations_multi(s, p):
    cur = Node('DOCUMENTATION', None, []) if not p[1] else p[1][0]
    cur.value.insert(0, p[0].value.lstrip('# '))
    return [cur]

@pg.production('documentations : ')
def documentations_empty(s, p):
    return []

@pg.production('name : CNAME')
def name_cname(s, p):
    return Node('NAME', p[0].value)

@pg.production('name : id-or-kw')
def name_id(s, p):
    return p[0]

@pg.production('id-or-kw : identifier')
def id_or_kw_identifier(s, p):
    return p[0]

@pg.production('id-or-kw : keyword')
def id_or_kw_keyword(s, p):
    return p[0]

@pg.production('identifier : ID')
def id_kw_id(s, p):
    return Node('NAME', p[0].value)

@pg.production('identifier : QID')
def id_kw_quoted_identifier(s, p):
    return Node('NAME', p[0].value[1:])

@pg.production('keyword : ATTRIBUTE')
def keyword_attr(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : DATATYPES')
def keyword_dtypes(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : DEFAULT')
def keyword_default(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : DIV')
def keyword_div(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : ELEMENT')
def keyword_elem(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : EMPTY')
def keyword_empty(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : EXTERNAL')
def keyword_external(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : GRAMMAR')
def keyword_grammar(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : INCLUDE')
def keyword_include(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : INHERIT')
def keyword_inherit(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : LIST')
def keyword_list(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : MIXED')
def keyword_mixed(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : NAMESPACE')
def keyword_namespace(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : NOTALLOWED')
def keyword_notallowed(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : PARENT')
def keyword_parent(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : START')
def keyword_start(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : STRING')
def keyword_string(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : TEXT')
def keyword_text(s, p):
    return Node('NAME', p[0].value)

@pg.production('keyword : TOKEN')
def keyword_token(s, p):
    return Node('NAME', p[0].value)

class ParseError(Exception):

    def __init__(self, t, fn, ln, col, line):

        self.token = t
        self.location = fn, ln, col
        self.line = line

        fn = fn if fn is not None else '(unknown)'
        loc = 'in %s [%s:%s]' % (fn, ln + 1, col + 1)
        spaces = col + 3 * min(col, line.count('\t'))
        line = line.replace('\t', ' ' * 4).rstrip()
        self.msg = '\n'.join((loc, line, ' ' * spaces + '^'))
        Exception.__init__(self, self.msg)

@pg.error
def error(s, t):
    ln = t.source_pos.lineno - 1
    if t.value and t.value[0] == '\n':
        ln -= 1
    col = t.source_pos.colno - 1
    line = s.lines[ln] if ln < len(s.lines) else ''
    raise ParseError(t, s.fn, ln, col, line)

parser = pg.build()

class State(object):
    def __init__(self, fn, src):
        self.fn = fn
        self.path = os.getcwd()
        if fn is not None:
            self.path = os.path.dirname(os.path.abspath(fn)) if ':' not in fn else fn
        self.lines = src.splitlines()

if sys.version_info[0] < 3:
    str_types = str, bytes, unicode  # noqa: unicode not defined in Python 3
else:
    str_types = str, bytes

def parse(src=None, f=None):
    assert src is None or f is None
    if f is not None and isinstance(f, str_types):
        fn = f
        if ':' in fn:
            with urlopen(fn) as f:
                bytes = f.read()
        else:
            with open(fn, 'rb') as f:
                bytes = f.read()
        bom = bytes[:2] in {BOM_UTF16_BE, BOM_UTF16_LE}
        src = bytes.decode('utf-16' if bom else 'utf-8')
    elif f is not None:
        fn, src = f.name, f.read()
    else:
        # Caller only gave source code, no filename.
        fn = None
    return parser.parse(lex(src), state=State(fn, src))
