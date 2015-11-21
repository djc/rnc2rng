from . import parser, serializer

def load(f):
    return parser.parse(f=f)

def loads(src):
    return parser.parse(src)

def dump(root, f, indent=None):
    f.write(serializer.XMLSerializer(indent).toxml(root))

def dumps(root, indent=None):
    return serializer.XMLSerializer(indent).toxml(root)
