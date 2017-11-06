from hashlib import sha256
import struct
from binascii import hexlify
from threading import Thread, Event, Lock
from logging import log, DEBUG, INFO, WARN, ERROR, CRITICAL

from .base import *
from .util import WrongNumberOfBytesRead
from ..schema import *
from ..schema.typeref import TypeRef
from .write import SchemaWriter

class ReaderBase:
    def __init__(self, stream):
        super().__init__()
        self._instream = stream
        self._read_signed_integer_functions = {
            1: self.read_int8,
            2: self.read_int16,
            4: self.read_int32,
            8: self.read_int64
        }
        self._read_unsigned_integer_functions = {
            1: self.read_uint8,
            2: self.read_uint16,
            4: self.read_uint32,
            8: self.read_uint64
        }

    def read_from_stream(self, bytes_count: int):
        b = self._instream.read(bytes_count)
        if len(b) != bytes_count:
            raise WrongNumberOfBytesRead(bytes_count, len(b), self._idx)
        self._idx += len(b)
        self._hsh.update(b)
        return b

    def read_constant(self, bytes_const: bytes):
        bts = self.read_from_stream(len(bytes_const))
        assert bts == bytes_const, 'Expecting {} at offset 0x{:x}, got {}'.format(bytes_const, self.idx - len(bytes_const), bts)

    def read_struct_format(self, fmt):
        size = struct.calcsize(fmt)
        bts = self.read_from_stream(size)
        tpl = struct.unpack(fmt, bts)
        assert len(tpl) == 1, 'struct.unpack returned tuple of length {} != 1 when reading {} bytes for format "{}" at offset 0x{:x}'.format(len(tpl), size, fmt, self.idx)
        return tpl[0]

    def read_int8(self):
        return self.read_struct_format('!b')

    def read_uint8(self):
        return self.read_struct_format('!B')

    def read_int16(self):
        return self.read_struct_format('!h')

    def read_uint16(self):
        return self.read_struct_format('!H')

    def read_int32(self):
        return self.read_struct_format('!i')

    def read_uint32(self):
        return self.read_struct_format('!I')

    def read_int64(self):
        return self.read_struct_format('!q')

    def read_uint64(self):
        return self.read_struct_format('!Q')

    def read_signed_integer(self, nbytes: int):
        assert nbytes in (1, 2, 4, 8), 'Integers have to be 1, 2, 4 or 8 bytes long, got {}'.format(nbytes)
        fn = self._read_signed_integer_functions[nbytes]
        return fn()

    def read_unsigned_integer(self, nbytes: int):
        assert nbytes in (1, 2, 4, 8), 'Integers have to be 1, 2, 4 or 8 bytes long, got {}'.format(nbytes)
        fn = self._read_unsigned_integer_functions[nbytes]
        return fn()

    def read_float32(self):
        return self.read_struct_format('!f')

    def read_float64(self):
        return self.read_struct_format('!d')

    def read_string(self):
        size = self.read_uint32()
        bts = self.read_from_stream(size)
        return bts.decode('utf8')

    def read_name(self):
        name = self.read_string()
        assert_name(name)
        return name

    def read_type_ref(self):
        return TypeRef(self.read_int32())


class SchemaReader(ReaderBase):
    def __init__(self, stream):
        super().__init__(stream)
        self._idx = 0
        self._hsh = sha256()

    def read_enum(self):
        self.read_constant(DECLARE_ENUM)
        enum_type_ref = self.read_type_ref()
        enum_name = self.read_name()
        enum_count = self.read_uint32()
        values = []
        for value_idx in range(enum_count):
            values.append(self.read_name())
        return enum_type_ref, Enum(enum_name, values)

    def read_method(self):
        method_ref = self.read_unsigned_integer(self.bytes_method_ref)
        method_name = self.read_name()
        arg_count = self.read_uint32()
        args = []
        for arg_idx in range(arg_count):
            args.append((self.read_type_ref(), self.read_name()))
        return_type_ref = self.read_type_ref()
        return method_ref, Method(method_name, args, return_type_ref)

    def read_interface(self):
        self.read_constant(DECLARE_INTERFACE)
        interface_type_ref = self.read_type_ref()
        interface_name = self.read_name()
        method_count = self.read_uint32()
        methods = []
        for local_method_idx in range(method_count):
            method_ref, method = self.read_method()
            methods.append(method)
        return interface_type_ref, Interface(interface_name, methods)

    def read_schema(self):
        self.read_constant(MAGIC)
        self.read_constant(SCHEMA)

        schema_label = self.read_string()
        self.bytes_method_ref = self.read_uint32()
        self.bytes_object_ref = self.read_uint32()
        enums_count = self.read_uint32()
        records_count = self.read_uint32()
        interfaces_count = self.read_uint32()

        #print(schema_label, bytes_method_ref, bytes_object_ref, enums_count, records_count, interfaces_count)
        types = {TypeRef(idx): typ for idx, typ in enumerate(primitive_types)}
        for enum_idx in range(enums_count):
            type_ref, enum = self.read_enum()
            assert type_ref not in types, 'Trying to specify enum {} twice before offset 0x{:x}'.format(type_ref, self.idx)
            types[type_ref] = enum

        for interface_idx in range(interfaces_count):
            type_ref, interface = self.read_interface()
            assert type_ref not in types, 'Trying to specify interface {} twice before offset 0x{:x}'.format(type_ref, self.idx)
            types[type_ref] = interface

        for type_ref, typ in list(types.items()):
            if type_ref.type_ref > 0: # avoid void[]
                types[TypeRef(-type_ref.type_ref)] = Array(typ)
        for typ in types.values():
            typ.resolve_type_references(types)
        for type_ref, typ in list(types.items()):
            if isinstance(typ, Primitive) or isinstance(typ, Array):
                del types[type_ref]

        hsh_digest = self._hsh.digest()
        hsh_digest_read = self.read_from_stream(len(hsh_digest))
        assert hsh_digest == hsh_digest_read, 'SHA256 sum of schema does not match: computed {}, but read {}'.format(view_hex(hsh_digest), view_hex(hsh_digest_read))
        return Schema(schema_label, types.values(), self.bytes_method_ref, self.bytes_object_ref, sha256_digest=hsh_digest)

def read_schema(stream):
    return SchemaReader(stream).read_schema()

def schema_from_bytes(byt: bytes):
    from io import BytesIO
    with BytesIO(byt) as stream:
        return read_schema(stream)
