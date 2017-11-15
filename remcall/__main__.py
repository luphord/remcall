from . import read_schema, schema_to_bytes
from .schema import Schema
from .generate import CSharphCodeGenerator

def load_schema_from_file(fname):
    if fname.endswith('.py'):
        with open(fname, mode='r') as f:
            source = f.read()
        globals_dict = {}
        from . import schema
        globals_dict.update(vars(schema))
        exec(source, globals_dict)
        schemas = []
        for key, val in globals_dict.items():
            if isinstance(val, Schema):
                schemas.append(val)
        if not schemas:
            raise ValueError('No schema found in {}'.format(fname))
        elif len(schemas) > 1:
            raise ValueError('Multiple schemas found in {}: {}'.format(fname, [schema.label for schema in schemas]))
        else:
            return schemas[0]
    else:
        with open(fname, mode='rb') as f:
            return read_schema(f)

from argparse import ArgumentParser
parser = ArgumentParser(prog='remcall', description='IPC using remote method calls and object proxying between different programming languages')
subparsers = parser.add_subparsers(dest='command')
subparsers.required = True

# Pretty print
def print_schema(args):
    schema = load_schema_from_file(args.schema)
    print(schema.pretty_print())
print_parser = subparsers.add_parser('print', description='Pretty print a schema')
print_parser.add_argument('schema')
print_parser.set_defaults(func=print_schema)

# Encode base64
def base64_schema(args):
    schema = load_schema_from_file(args.schema)
    import base64
    print(base64.encodebytes(schema_to_bytes(schema)).decode('ascii'))
base64_parser = subparsers.add_parser('base64', description='Encode a schema in base64')
base64_parser.add_argument('schema')
base64_parser.set_defaults(func=base64_schema)

# Generate code
def generate(args):
    schema = load_schema_from_file(args.schema)
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
