from lark import Lark, Transformer, Token, Tree
from lark.indenter import Indenter

join = lambda xs, str: str.join(xs)

class MyIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = ['_LANG']
    CLOSE_PAREN_types = ['_RANG']
    INDENT_type = '_IND'
    DEDENT_type = '_DED'
    tab_len = 4

parser = Lark.open('xlite.lark', parser='lalr', postlex=MyIndenter())

presets = dict(
    xml = dict(
        ext='xml',
        no_close={'!doctype'},
    ),
    html5 = dict(
        ext='html',
        no_close={'!doctype', 'meta', 'link', 'a', 'br', 'img'},
    ),
)

preset = presets['xml']
no_close = preset['no_close']

def emit_elem(tree, level=0):
    xs = tree.children
    tag = xs.pop(0)

    attrs = []
    while xs and isinstance(xs[0], Tree) and xs[0].data == 'attr':
        attrs.append(xs.pop(0).children)

    children = []
    if xs and isinstance(xs[0], Token) and xs[0].type == 'TEXT':
        text = xs.pop(0)
        children.append(text.value)

    if xs:
        body = xs.pop(0).children
        while body:
            x = body.pop(0)
            if isinstance(x, Token) and x.type == 'TEXT':
                children.append(x)
            if isinstance(x, Tree) and x.data == 'elem':
                children.append(emit_elem(x, level=level+1))
            if isinstance(x, Tree) and x.data == 'line':
                children.append(x.children[0].value)

    head = [tag] + [join(pair, '=') for pair in attrs]
    head = join(head, ' ')
    
    
    body = None
    if not children:
        body = ''
    elif len(children) == 1:
        body = children[0]
    else:
        pad = '\n' + '\t'*level
        body = join(['']+children, pad+'\t') + pad
    
    if not body:
        if tag.lower() in no_close:
            return f'<{head}>'
        else:
            return f'<{head} />'
    else:
        return f'<{head}>{body}</{tag}>'

def emit_root(tree):
    return '\n'.join(emit_elem(x, level=0) for x in tree.children)

def emit(tree, preset='xml'):
    no_close = presets[preset]['no_close']
    return emit_root(tree.copy())

def parse(string):
    return parser.parse(string+'\n')