from . import read_schema
from .generate import CSharphCodeGenerator

from argparse import ArgumentParser
parser = ArgumentParser(prog='remcall', description='IPC using remote method calls and object proxying between different programming languages')
subparsers = parser.add_subparsers(dest='command')
subparsers.required = True

def print_schema(args):
    with open(args.schema, mode='rb') as f:
        schema = read_schema(f)
    print(schema.pretty_print())
print_parser = subparsers.add_parser('print', description='Pretty print a schema')
print_parser.add_argument('schema')
print_parser.set_defaults(func=print_schema)

def generate(args):
    with open(args.schema, mode='rb') as f:
        schema = read_schema(f)
    if args.language == 'csharp':
        generator = CSharphCodeGenerator(schema, args.namespace)
    else:
        raise NotImplementedError('Would love to be able to generate code for {}'.format(args.language))
    import sys
    generator.write_schema(sys.stdout)
generate_parser = subparsers.add_parser('generate', description='Generate code from schema')
generate_parser.add_argument('-l', '--language', help='Programming language to create code for', default='csharp', type=str, choices=['c', 'csharp', 'go', 'java'])
generate_parser.add_argument('-n', '--namespace', help='Namespace to create code in', default='Remcall.Generated', type=str)
generate_parser.add_argument('schema')
generate_parser.set_defaults(func=generate)


args = parser.parse_args()
args.func(args)
