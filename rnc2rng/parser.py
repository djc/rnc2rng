import rply, sys, os

KEYWORDS = set([
    'attribute', 'datatypes', 'default', 'div', 'element', 'empty', 'include',
    'list', 'mixed', 'namespace', 'notAllowed', 'parent', 'start', 'string',
    'text',
])

def lexer():
    lg = rply.LexerGenerator()
    lg.add('LPAREN', '\(')
    lg.add('RPAREN', '\)')
    lg.add('LBRACE', '{')
    lg.add('RBRACE', '}')
    lg.add('LBRACKET', '\[')
    lg.add('RBRACKET', '\]')
    lg.add('EQUAL', '=')
    lg.add('PIPE', '[|]')
    lg.add('COMMA', ',')
    lg.add('AMP', '&')
    lg.add('MINUS', '[-]')
    lg.add('STAR', '[*]')
    lg.add('PLUS', '[+]')
    lg.add('QMARK', '[?]')
    lg.add('CNAME', '[\w*]+:[\w*]+')
    lg.add('ID', '\w+')
    lg.add('LITERAL', '".*?"')
    lg.add('DOCUMENTATION', '##.*')
    lg.add('COMMENT', '#.*')
    lg.ignore('\s+')
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
    'AMP', 'CNAME', 'COMMA', 'DOCUMENTATION', 'EQUAL', 'ID', 'LBRACE',
    'LBRACKET', 'LPAREN', 'LIST', 'LITERAL', 'MINUS', 'MIXED', 'PLUS', 'PIPE',
    'QMARK', 'RBRACE', 'RBRACKET', 'RPAREN', 'STAR',
] + [s.upper() for s in KEYWORDS])

class Node(object):
    __slots__ = 'type', 'name', 'value'
    def __init__(self, type, name, value=None):
        self.type = type
        self.name = name
        self.value = value or []
    def __repr__(self):
        bits = [(k, getattr(self, k, None)) for k in self.__slots__]
        strs = ['%s=%r' % (k, v) for (k, v) in bits if v is not None]
        return 'Node(%s)' % ', '.join(strs)

NODE_TYPES = [
    'ANNOTATION', 'ANY', 'ATTR', 'CHOICE', 'DATATAG', 'DATATYPES',
    'DEFAULT_NS', 'DEFINE', 'DIV', 'DOCUMENTATION', 'ELEM', 'EMPTY', 'EXCEPT',
    'GROUP', 'INTERLEAVE', 'LIST', 'LITERAL', 'MAYBE', 'MIXED', 'NAME',
    'NOTALLOWED', 'NS', 'PARAM', 'PARENT', 'REF', 'ROOT', 'SEQ', 'SOME',
    'TEXT',
]

@pg.production('start : decls element-primary')
def start_pattern(s, p):
    start = Node('DEFINE', 'start', [p[1]])
    p[0].append(start)
    return Node('ROOT', None, p[0])

@pg.production('start : decls DOCUMENTATION element-primary')
def start_annotated_element(s, p):
    p[2].value.insert(0, Node('DOCUMENTATION', p[1].value))
    p[0].append(Node('DEFINE', 'start', [p[2]]))
    return Node('ROOT', None, p[0])

@pg.production('start : decls include-content')
def start_rules(s, p):
    return Node('ROOT', None, p[0] + p[1])

@pg.production('decls : decls decl')
def decls_multi(s, p):
    p[0].append(p[1])
    return p[0]

@pg.production('decls : ')
def decls_empty(s, p):
    return []

@pg.production('decl : DEFAULT NAMESPACE EQUAL LITERAL')
def decl_default_ns(s, p):
    return Node('DEFAULT_NS', None, [p[3].value])

@pg.production('decl : DEFAULT NAMESPACE id-or-kw EQUAL LITERAL')
def decl_default_names_ns(s, p):
    return Node('DEFAULT_NS', p[2].name, [p[4].value])

@pg.production('decl : NAMESPACE id-or-kw EQUAL LITERAL')
def decl_ns(s, p):
    return Node('NS', p[1].name, [p[3].value])

@pg.production('decl : DATATYPES id-or-kw EQUAL LITERAL')
def decl_datatypes(s, p):
    return Node('DATATYPES', p[1].name, [p[3].value])

@pg.production('include-content : include-content component')
def include_content_multi(s, p):
    p[0].append(p[1])
    return p[0]

@pg.production('include-content : ')
def include_content_empty(s, p):
    return []

@pg.production('component : ID EQUAL pattern')
def component_define(s, p):
    return Node('DEFINE', p[0].value, p[2])

@pg.production('component : START EQUAL pattern')
def component_start(s, p):
    return Node('DEFINE', 'start', p[2])

@pg.production('component : DIV LBRACE include-content RBRACE')
def component_div(s, p):
    return Node('DIV', None, p[2])

@pg.production('component : INCLUDE LITERAL')
def component_include(s, p):
    with open(os.path.join(s.path, p[1].value)) as f:
        return parse(f)

@pg.production('component : CNAME LBRACKET params RBRACKET')
def component_annotation_element(s, p):
    return Node('ANNOTATION', p[0].value, p[2])

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

@pg.production('annotated-primary : DOCUMENTATION primary')
def annotated_primary_annotated(s, p):
    p[1].value.insert(0, Node('DOCUMENTATION', p[0].value))
    return p[1]

@pg.production('annotated-primary : primary')
def annotated_primary_primary(s, p):
    return p[0]

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

@pg.production('primary : LITERAL')
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

@pg.production('primary : STRING LBRACE params RBRACE')
def primary_string_parametrized(s, p):
    return Node('DATATAG', 'string', p[2])

@pg.production('primary : TEXT')
def primary_text(s, p):
    return Node('TEXT', None)

@pg.production('primary : EMPTY')
def primary_empty(s, p):
    return Node('EMPTY', None)

@pg.production('primary : ID')
def primary_id(s, p):
    return Node('REF', p[0].value)

@pg.production('primary : NOTALLOWED')
def primary_notallowed(s, p):
    return Node('NOTALLOWED', None)

@pg.production('primary : PARENT ID')
def primary_parent(s, p):
    return Node('PARENT', p[1].value)

@pg.production('params : params param')
def params_multi(s, p):
    p[0].append(p[1])
    return p[0]

@pg.production('params : ')
def params_empty(s, p):
    return []

@pg.production('param : id-or-kw EQUAL LITERAL')
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

@pg.production('simple-name-class : CNAME')
def simple_name_class_cname(s, p):
    return [Node('NAME', p[0].value)]

@pg.production('simple-name-class : LPAREN name-class RPAREN')
def name_class_group(s, p):
    return p[1]

@pg.production('name : id-or-kw')
def name_id(s, p):
    return p[0]

@pg.production('id-or-kw : ID')
def id_kw_id(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : ELEMENT')
def id_kw_elem(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : ATTRIBUTE')
def id_kw_elem(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : EMPTY')
def id_kw_empty(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : TEXT')
def id_kw_text(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : START')
def id_kw_start(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : LIST')
def id_kw_list(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : MIXED')
def id_kw_mixed(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : NOTALLOWED')
def id_kw_notallowed(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : DIV')
def id_kw_div(s, p):
    return Node('NAME', p[0].value)

@pg.production('id-or-kw : INCLUDE')
def id_kw_div(s, p):
    return Node('NAME', p[0].value)

@pg.error
def error(s, t):
    raise Exception(s, t)

parser = pg.build()

class State(object):
    def __init__(self, path):
        self.path = path

if sys.version_info[0] < 3:
    str_types = str, bytes, unicode
else:
    str_types = str, bytes

def parse(src):
    path = os.getcwd()
    if not isinstance(src, str_types):
        if hasattr(src, 'name'):
            path = os.path.dirname(os.path.abspath(src.name))
        src = src.read()
    return parser.parse(lex(src), state=State(path))
