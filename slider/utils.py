import os
from decimal import Decimal
import yaml
from yaml.composer import Composer
from yaml.constructor import SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import BaseResolver, Resolver as DefaultResolver
from yaml.scanner import Scanner
import re


class Resolver(BaseResolver):
    pass

# Adding implicit resolver for decimal based on
# https://github.com/yaml/pyyaml/blob/957ae4d495cf8fcb5475c6c2f1bce801096b68a5/lib/yaml/resolver.py#L177
Resolver.add_implicit_resolver(
    '!decimal',
    re.compile(r'''^(?:
        [-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+][0-9]+)?
        |\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-9]?[0-9])+\.[0-9_]*
        |[-+]?\.(?:inf|Inf|INF)
        |\.(?:nan|NaN|NAN)
    )$''', re.VERBOSE),
    list('-+0123456789.')
)

for ch, vs in DefaultResolver.yaml_implicit_resolvers.items():
    Resolver.yaml_implicit_resolvers.setdefault(ch, []).extend(
        (tag, regexp) for tag, regexp in vs
        if not tag.endswith('float')
    )


class Loader(Reader, Scanner, Parser, Composer, SafeConstructor, Resolver):
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        Resolver.__init__(self)


def decimal_constructor(loader, node):
    value = loader.construct_scalar(node)
    return Decimal(value)


def dec_representer(dumper, value):
    text = str(value)
    return dumper.represent_scalar(u'tag:yaml.org,2002:float', text)


def produce_output(output: str, filepath: str, data: any, yaml_dump_args: dict = {}):
    os.makedirs(output, exist_ok=True)
    output_path = os.path.join(output, filepath)
    with open(output_path, 'w') as f:
        yaml.dump(data, f, **yaml_dump_args)
