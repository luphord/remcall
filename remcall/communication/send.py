from threading import Thread, Event, Lock
from logging import log, DEBUG, INFO, WARN, ERROR, CRITICAL
from binascii import hexlify

from .base import *
from ..schema import *
from ..codec.write import WriterBase, SchemaWriter, schema_to_bytes
from ..codec.util import view_hex

class Sender(WriterBase):
    def __init__(self, schema, outstream, get_id_for_object):
        super().__init__(schema, outstream)
        self.method_table = self.schema.method_table
        self.serialized_schema = schema_to_bytes(schema)
        self.get_id_for_object = get_id_for_object
        self.request_id = 0

        self._write_value_functions = {
            int8: self.write_int8,
            int16: self.write_int16,
            int32: self.write_int32,
            int64: self.write_int64,
            uint8: self.write_uint8,
            uint16: self.write_uint16,
            uint32: self.write_uint32,
            uint64: self.write_uint64,
            float32: self.write_float32,
            float64: self.write_float64,
            string: self.write_string,
            void: lambda *args: None
        }
        for interface in self.schema.interfaces:
            self._write_value_functions[interface] = self.write_object_ref

    def write_to_stream(self, data: bytes):
        log(DEBUG, 'Writing data of length {} to stream: {}'.format(len(data), hexlify(data)))
        self._outstream.write(data)
        self._outstream.flush()

    def write_request_id(self, request_id=None):
        if request_id is None:
            self.request_id = (self.request_id + 1) % (1 << 32)
            request_id = self.request_id
        self.write_uint32(request_id)

    def request_schema(self):
        self.write_to_stream(REQUEST_SCHEMA)

    def send_schema(self):
        self.write_to_stream(SEND_SCHEMA)
        self.write_to_stream(self.serialized_schema)

    def write_object_ref(self, obj):
        oid = self.get_id_for_object(obj)
        self._write_signed_integer_functions[self.schema.bytes_object_ref](oid)

    def write_value(self, typ, value):
        self._write_value_functions[typ](value)

    def call_method(self, method, this, args_dict):
        log(INFO, 'Preparing to request method call for method {} on object {} with arguments {}'.format(method.name, this, args_dict))
        method_idx = self.method_table[method]
        self.write_to_stream(CALL_METHOD)
        self.write_request_id()
        self.write_method_ref(method_idx)
        self.write_object_ref(this)
        for typ, name in method.arguments:
            self.write_value(typ, args_dict[name])
        log(DEBUG, 'Requested method call with request ID {} on stream {}'.format(self.request_id, self._outstream))
        return self.request_id

    def return_method(self, request_id, return_type, return_value):
        log(DEBUG, 'Returning method call result for request {} with value {} of type {}'.format(request_id, return_value, return_type))
        self.write_to_stream(RETURN_FROM_METHOD)
        self.write_request_id(request_id)
        self.write_value(return_type, return_value)

    def noop(self):
        self.write_to_stream(NOOP)

    def disconnect(self):
        log(INFO, 'Disconnecting')
        self.write_to_stream(DISCONNECT)

    def acknowledge_disconnect(self):
        log(INFO, 'Acknowledging disconnect')
        self.write_to_stream(ACKNOWLEDGE_DISCONNECT)
