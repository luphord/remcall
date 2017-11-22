from typing import Iterable, Tuple, Mapping, Union

from .base import assert_name
from .typeref import TypeRef

class Type:
    type_order = -1

    def __init__(self, name: str) -> None:
        assert_name(name)
        self.name = name

    def __str__(self) -> str:
        return self.name

    @property
    def is_declared(self) -> bool:
        return False

    @property
    def sort_key(self):
        assert self.type_order >= 0, 'Type {} has type_order {} < 0 and cannot be sorted'.format(self.name, self.type_order)
        return (self.type_order, self.name)

    def resolve_type_references(self, type_ref_lookup):
        pass

TypeOrRef = Union[Type, TypeRef]
def assert_type_or_ref(typ: TypeOrRef):
    assert isinstance(typ, Type) or isinstance(typ, TypeRef), '{} which not an instance of Type or TypeRef'.format(typ)

class Array(Type):
    type_order = 3

    def __init__(self, typ: Type) -> None:
        super().__init__('ArrayOf{}'.format(typ.name))
        self.typ = typ

    def __eq__(self, other: Type) -> bool:
        '''
        Equality of array types is equaivalent to the equality of their underlying types
        >>> int64 == int64
        True
        >>> Array(int64) == Array(int64)
        True
        >>> int64 == float32
        False
        >>> Array(int32) == Array(float32)
        False
        '''
        return isinstance(other, Array) and other.typ == self.typ

    def __hash__(self):
        return -hash(self.typ)

    def __str__(self) -> str:
        return '{}[]'.format(self.typ.name)

    def __repr__(self) -> str:
        return 'Array({!s})'.format(self.typ)

class Primitive(Type):
    def __repr__(self):
        return 'Primitive("{}")'.format(self.name)

primitive_types = []
for typename in ('void', 'boolean', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64', 'float32', 'float64', 'string', 'date', 'time', 'datetime'):
    primitive = Primitive(typename)
    primitive_types.append(primitive)
    locals()[typename] = primitive

class Enum(Type):
    type_order = 0

    def __init__(self, name: str, values: Iterable[str]) -> None:
        super().__init__(name)
        self.values = list(values)
        assert len(self.values) <= 256, 'Enums may contain at most 256 values, got {}'.format(len(self.values))
        for value in self.values:
            assert_name(value)

    @property
    def is_declared(self) -> bool:
        return True

    def pretty_print(self) -> str:
        return 'enum {} {{\n{}\n}}'.format(self.name, '\n'.join('  {},'.format(value) for value in self.values))

    def __repr__(self) -> str:
        return '{}(name="{}", values={})'.format(self.__class__.__name__, self.name, self.values)

class Record(Type):
    type_order = 1

    def __init__(self, name: str, fields: Iterable[Tuple[TypeOrRef, str]]) -> None:
        super().__init__(name)
        self.fields = list(fields)
        for typ, name in self.fields:
            assert_name(name)
            assert_type_or_ref(typ)
            assert typ is not void, 'Fields cannot be of type void'

    def resolve_type_references(self, type_ref_lookup: Mapping[TypeRef, Type]) -> None:
        for field_idx, field in enumerate(list(self.fields)):
            field_type, field_name = field
            if isinstance(field_type, TypeRef):
                actual_type = type_ref_lookup[field_type]
                assert actual_type is not void, 'Fields cannot be of type void'
                self.fields[field_idx] = (actual_type, field_name)

    @property
    def is_declared(self) -> bool:
        return True

    @property
    def fields_sorted(self):
        return sorted(self.fields, key=lambda field: field[1])

    def pretty_print(self) -> str:
        return 'record {} {{\n{}\n}}'.format(self.name, '\n'.join('  {} {};'.format(field_type, field_name) for field_type, field_name in self.fields_sorted))

    def __repr__(self) -> str:
        return '{}(name="{}", fields={})'.format(self.__class__.__name__, self.name, self.fields)

class Method:
    def __init__(self, name: str, arguments: Iterable[Tuple[TypeOrRef, str]], return_type: Type) -> None:
        assert_name(name)
        self.name = name
        self.arguments = list(arguments)
        for typ, name in self.arguments:
            assert_name(name)
            assert_type_or_ref(typ)
            assert typ is not void, 'Arguments cannot be of type void'
        self.return_type = return_type

    def __str__(self) -> str:
        return '{!s} {}({});'.format(self.return_type, self.name, ', '.join('{!s} {}'.format(typ, name) for typ, name in self.arguments))

    def __repr__(self) -> str:
        return '{}(name="{}", arguments={}, return_type="{}")'.format(self.__class__.__name__, self.name, self.arguments, self.return_type)

class Interface(Type):
    type_order = 2

    def __init__(self, name: str, methods: Iterable[Method]):
        super().__init__(name)
        self.methods = list(methods)

    @property
    def is_declared(self):
        return True

    @property
    def methods_sorted(self):
        return sorted(self.methods, key=lambda m: m.name)

    def resolve_type_references(self, type_ref_lookup: Mapping[TypeRef, Type]) -> None:
        for method in self.methods:
            for arg_idx, arg in enumerate(list(method.arguments)):
                arg_type, arg_name = arg
                if isinstance(arg_type, TypeRef):
                    method.arguments[arg_idx] = (type_ref_lookup[arg_type], arg_name)
            if isinstance(method.return_type, TypeRef):
                method.return_type = type_ref_lookup[method.return_type]

    def pretty_print(self) -> str:
        return 'interface {} {{\n{}\n}}'.format(self.name, '\n'.join('  {!s}'.format(method) for method in self.methods_sorted))

    def __repr__(self) -> str:
        return '{}(name="{}", methods={!r})'.format(self.__class__.__name__, self.name, self.methods)

class Schema:
    def __init__(self, label, types, bytes_method_ref=2, bytes_object_ref=4, sha256_digest=None):
        self.label = label
        self.types = set(typ for typ in types if typ.is_declared)
        assert bytes_method_ref in (1, 2, 4, 8), 'Method references have to be 1, 2, 4 or 8 bytes long, got {}'.format(bytes_method_ref)
        assert bytes_object_ref in (1, 2, 4, 8), 'Object references have to be 1, 2, 4 or 8 bytes long, got {}'.format(bytes_method_ref)
        self.bytes_method_ref = bytes_method_ref
        self.bytes_object_ref = bytes_object_ref
        if sha256_digest:
            assert len(sha256_digest) == 32, 'SHA256 digest must be 32 bytes long'
        self.sha256_digest = sha256_digest
        assert hasattr(self.type_schemas, 'Main'), 'Every schema requires an interface called "Main", got only {}'.format(', '.join('"{}"'.format(ifc.name) for ifc in self.interfaces_sorted))
        self.main_type = self.type_schemas.Main
        for ifc in self.interfaces_sorted:
            assert len(ifc.methods) > 0, 'Every interface requires at least one method, "{}" has none'.format(ifc.name)

    @property
    def iter_declared_types(self):
        for typ in self.types:
            if typ.is_declared:
                yield typ

    @property
    def declared_types(self):
        return sorted(self.iter_declared_types, key=lambda tp: tp.sort_key)

    @property
    def enums(self):
        return [typ for typ in self.types if isinstance(typ, Enum)]

    @property
    def records(self):
        return [typ for typ in self.types if isinstance(typ, Record)]

    @property
    def interfaces(self):
        return [typ for typ in self.types if isinstance(typ, Interface)]

    @property
    def enums_sorted(self):
        for typ in self.declared_types:
            if isinstance(typ, Enum):
                yield typ

    @property
    def records_sorted(self):
        for typ in self.declared_types:
            if isinstance(typ, Record):
                yield typ

    @property
    def interfaces_sorted(self):
        for typ in self.declared_types:
            if isinstance(typ, Interface):
                yield typ

    @property
    def type_table(self):
        assert primitive_types[0].name == 'void', 'First type with index 0 has to be void, got {}'.format(primitive_types[0])
        table = {typ: idx for idx, typ in enumerate(primitive_types + self.declared_types)}
        for typ, idx in list(table.items()):
            table[Array(typ)] = -idx
        return table

    @property
    def type_schemas(self):
        class _: pass
        tps = _()
        for typ in self.declared_types:
            setattr(tps, typ.name, typ)
        return tps

    @property
    def method_table(self):
        return {v: k for k, v in self.method_lookup.items()}

    @property
    def method_lookup(self):
        return {idx: method for idx, method in enumerate(sum((iface.methods_sorted for iface in self.interfaces_sorted), []))}

    @property
    def method_to_interface(self):
        mi = {}
        for iface in self.interfaces_sorted:
            for method in iface.methods_sorted:
                mi[self.method_table[method]] = iface
        return mi

    def pretty_print(self):
        return '\n\n'.join(typ.pretty_print() for typ in self.declared_types)

    def __repr__(self):
        return '{}(label="{}", types={!r})'.format(self.__class__.__name__, self.label, self.types)

__all__ = ['Type', 'Array', 'Primitive', 'Enum', 'Record', 'Method', 'Interface', 'Schema', 'primitive_types'] + [tp.name for tp in primitive_types]
