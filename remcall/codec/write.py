from hashlib import sha256
import struct
import io
from binascii import hexlify
from logging import log, DEBUG, INFO, WARN, ERROR, CRITICAL

from .base import *
from ..schema import *

class WriterBase:
    def __init__(self, schema, outstream):
        super().__init__()
        self.schema = schema
        self._outstream = outstream
        self.type_table = schema.type_table
        self._write_signed_integer_functions = {
            1: self.write_int8,
            2: self.write_int16,
            4: self.write_int32,
            8: self.write_int64
        }
        self._write_unsigned_integer_functions = {
            1: self.write_uint8,
            2: self.write_uint16,
            4: self.write_uint32,
            8: self.write_uint64
        }

    def write_to_stream(self, data: bytes):
        raise NotImplementedError()

    def write_int8(self, i: int):
        self.write_to_stream(struct.pack('!b', i))

    def write_uint8(self, i: int):
        self.write_to_stream(struct.pack('!B', i))

    def write_int16(self, i: int):
        self.write_to_stream(struct.pack('!h', i))

    def write_uint16(self, i: int):
        self.write_to_stream(struct.pack('!H', i))

    def write_int32(self, i: int):
        self.write_to_stream(struct.pack('!i', i))

    def write_uint32(self, i: int):
        self.write_to_stream(struct.pack('!I', i))

    def write_int64(self, i: int):
        self.write_to_stream(struct.pack('!q', i))

    def write_uint64(self, i: int):
        self.write_to_stream(struct.pack('!Q', i))

    def write_signed_integer(self, i: int, nbytes: int):
        assert nbytes in (1, 2, 4, 8), 'Integers have to be 1, 2, 4 or 8 bytes long, got {}'.format(nbytes)
        fn = self._write_signed_integer_functions[nbytes]
        return fn(i)

    def write_unsigned_integer(self, i: int, nbytes: int):
        assert nbytes in (1, 2, 4, 8), 'Integers have to be 1, 2, 4 or 8 bytes long, got {}'.format(nbytes)
        fn = self._write_unsigned_integer_functions[nbytes]
        return fn(i)

    def write_float32(self, f: float):
        self.write_to_stream(struct.pack('!f', f))

    def write_float64(self, f: float):
        self.write_to_stream(struct.pack('!d', f))

    def write_bytes(self, b):
        self.write_uint32(len(b))
        self.write_to_stream(b)

    def write_string(self, s):
        b = s.encode('utf8')
        self.write_bytes(b)

    def write_type_ref(self, typ):
        type_ref = self.type_table.get(typ)
        if type_ref is None:
            raise Exception('Trying to write type reference to unknown type {}'.format(typ))
        self.write_int32(type_ref)

    def write_method_ref(self, method_idx):
        assert self.schema.bytes_method_ref in (1, 2, 4, 8), 'Method references have to be 1, 2, 4 or 8 bytes long, got {}'.format(bytes_method_ref)
        assert method_idx < 2 << (self.schema.bytes_method_ref * 8 - 1), 'Trying to store method reference {} using only {} bytes'.format(method_idx, bytes_method_ref)
        self.write_unsigned_integer(method_idx, self.schema.bytes_method_ref)


class SchemaWriter(WriterBase):
    def __init__(self, schema, stream):
        super().__init__(schema, stream)
        self._idx = 0
        self._hsh = sha256()
        self._method_idx = 0

    def write_to_stream(self, data: bytes):
        self._outstream.write(data)
        self._idx += len(data)
        self._hsh.update(data)

    def write_name(self, s):
        assert_name(s)
        b = s.encode('ascii')
        self.write_bytes(b)

    def write_enum(self, enum):
        self.write_to_stream(DECLARE_ENUM)
        self.write_type_ref(enum)
        self.write_name(enum.name)
        self.write_uint32(len(enum.values))
        for value in enum.values:
            self.write_name(value)

    def write_method(self, method):
        self.write_method_ref(self._method_idx)
        self.write_name(method.name)
        self.write_uint32(len(method.arguments))
        for argtype, argname in method.arguments:
            self.write_type_ref(argtype)
            self.write_name(argname)
        self.write_type_ref(method.return_type)
        self._method_idx += 1

    def write_interface(self, interface):
        self.write_to_stream(DECLARE_INTERFACE)
        self.write_type_ref(interface)
        self.write_name(interface.name)
        self.write_uint32(len(interface.methods))
        for method in interface.methods:
            self.write_method(method)

    def write_schema(self):
        self.write_to_stream(MAGIC)
        self.write_to_stream(SCHEMA)

        self.write_string(self.schema.label)
        self.write_uint32(self.schema.bytes_method_ref)
        self.write_uint32(self.schema.bytes_object_ref)
        self.write_uint32(len(self.schema.enums))
        self.write_uint32(len(self.schema.records))
        self.write_uint32(len(self.schema.interfaces))

        for typ in self.schema.declared_types:
            if isinstance(typ, Enum):
                self.write_enum(typ)
            elif isinstance(typ, Record):
                pass
            elif isinstance(typ, Interface):
                self.write_interface(typ)
            else:
                raise Exception('Unknown type {}'.format(typ))

        hsh_digest = self._hsh.digest()
        if self.schema.sha256_digest:
            assert hsh_digest == self.schema.sha256_digest, 'SHA256 sum of schema does not match: computed {} while writing, but got {}'.format(view_hex(hsh_digest), view_hex(self.schema.sha256_digest))
        self.write_to_stream(hsh_digest)
        idx = self._idx
        return hsh_digest, idx

def write_schema(schema, stream):
    SchemaWriter(schema, stream).write_schema()

def schema_to_bytes(schema):
    with io.BytesIO() as stream:
        write_schema(schema, stream)
        stream.seek(0)
        return stream.read()
