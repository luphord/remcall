from threading import Thread, Event, Lock
from logging import log, DEBUG, INFO, WARN, ERROR, CRITICAL
from binascii import hexlify

from .base import *
from ..schema import *
from ..codec.read import ReaderBase
from ..codec.util import WrongNumberOfBytesRead, view_hex
from ..codec.write import SchemaWriter, schema_to_bytes
from ..util import UnknownCommand, MethodNotAvailable, DuplicateRegistrationForMethodReturn, DuplicateMethodReturnValue, MissingMethodReturnValueEvent

class Receiver(ReaderBase):
    def __init__(self, schema, instream, get_object, return_method_result, acknowledge_disconnect, name_converter):
        super().__init__(instream)
        self.schema = schema
        self.method_lookup = self.schema.method_lookup
        self.method_to_interface = self.schema.method_to_interface
        self.serialized_schema = schema_to_bytes(schema)
        self.get_object = get_object
        self.method_return_events = {}
        self.method_return_values = {}
        self.return_method_result = return_method_result
        self.acknowledge_disconnect = acknowledge_disconnect
        self.name_converter = name_converter

        self._read_value_functions = {
            int8: self.read_int8,
            int16: self.read_int16,
            int32: self.read_int32,
            int64: self.read_int64,
            uint8: self.read_uint8,
            uint16: self.read_uint16,
            uint32: self.read_uint32,
            uint64: self.read_uint64,
            float32: self.read_float32,
            float64: self.read_float64,
            string: self.read_string,
            void: lambda *args: None
        }

    def read_from_stream(self, bytes_count: int):
        b = self._instream.read(bytes_count)
        log(DEBUG, 'Read data of length {} from stream: {}'.format(len(b), hexlify(b)))
        if len(b) != bytes_count:
            ex = WrongNumberOfBytesRead(bytes_count, len(b), None)
            log(ERROR, str(ex))
            raise ex
        return b

    def read_request_id(self):
        return self.read_uint32()

    def read_method_ref(self):
        return self.read_unsigned_integer(self.schema.bytes_method_ref)

    def read_object_ref(self, typ: Type):
        oid = self._read_signed_integer_functions[self.schema.bytes_object_ref]()
        log(DEBUG, 'Read object ID {}'.format(oid))
        return oid

    def read_object(self, typ: Type):
        oid = self.read_object_ref(typ)
        obj = self.get_object(oid, typ)
        log(DEBUG, 'Found object {}'.format(obj))
        return obj

    def read_enum_value(self, typ: Type):
        enum_value = self.read_uint32()
        return self.get_enum_implementation(typ)(enum_value) # todo: better api

    def read_value(self, typ: Type):
        if isinstance(typ, Interface):
            return self.read_object(typ)
        elif isinstance(typ, Enum):
            return self.read_enum_value(typ)
        else:
            return self._read_value_functions[typ]()

    def mainloop(self):
        self.exit_mainloop = False
        while not self.exit_mainloop:
            self.process_next()

    def process_next(self):
        log(DEBUG, 'Processing next command on stream {}'.format(self._instream))
        cmd = self.read_from_stream(1)
        if cmd == NOOP:
            log(DEBUG, 'Received NOOP command, doing nothing')
        elif cmd == DISCONNECT:
            log(DEBUG, 'Received DISCONNECT command, exiting mainloop')
            self.exit_mainloop = True
            self.acknowledge_disconnect()
        elif cmd == ACKNOWLEDGE_DISCONNECT:
            log(DEBUG, 'Received ACKNOWLEDGE_DISCONNECT command, exiting mainloop')
            self.exit_mainloop = True
        elif cmd == REQUEST_SCHEMA:
            self.send_schema()
        elif cmd == SEND_SCHEMA:
            self.receive_and_check_schema()
        elif cmd == CALL_METHOD:
            self.process_method_call()
        elif cmd == RETURN_FROM_METHOD:
            self.process_method_return()
        else:
            raise UnknownCommand(cmd)

    def process_method_call(self):
        request_id = self.read_request_id()
        method_ref = self.read_method_ref()
        log(INFO, 'Received method call with request ID {} and method reference {}'.format(request_id, method_ref))
        assert method_ref in self.method_lookup, 'Received method call with request ID {} and unknown method reference {}'.format(request_id, method_ref)
        method = self.method_lookup[method_ref]
        log(DEBUG, 'Found method {}'.format(method))
        this = self.read_object(self.method_to_interface[method_ref])
        impl_method_name = self.name_converter.method_name(method.name)
        try:
            method_impl = getattr(this, impl_method_name)
        except AttributeError:
            raise MethodNotAvailable(method, impl_method_name, this)
        args = {}
        for typ, name in method.arguments:
            args[name] = self.read_value(typ)
        def method_call_thread():
            log(DEBUG, 'Calling method implementation {} with arguments {}'.format(method_impl, args))
            return_value = method_impl(**args)
            log(DEBUG, 'Return value of method implementation call is {}'.format(return_value))
            self.return_method_result(request_id, method.return_type, return_value)
        Thread(target=method_call_thread).start()

    def process_method_return(self):
        request_id = self.read_request_id()
        log(DEBUG, 'Received return from method call with request ID {}'.format(request_id))
        if request_id in self.method_return_values:
            raise DuplicateMethodReturnValue(request_id)
        if request_id in self.method_return_events:
            event, return_type = self.method_return_events.pop(request_id)
            return_value = self.read_value(return_type)
            log(DEBUG, 'Return value for method call with request ID {} is {} of type {}'.format(request_id, return_value, return_type))
            self.method_return_values[request_id] = return_value
            event.set()
        else:
            raise MissingMethodReturnValueEvent(request_id)
            # ToDo: Wait and retry?


    def receive_and_check_schema(self):
        received_schema = SchemaReader(self._instream).read_schema()
        assert SchemaWriter(received_schema).to_bytes() == self.serialized_schema

    def wait_for_method_return(self, request_id, return_type):
        log(DEBUG, 'Waiting for method return corresponding to request {} with return type {} on stream {}'.format(request_id, return_type, self._instream))
        if request_id in self.method_return_events or request_id in self.method_return_values:
            raise DuplicateRegistrationForMethodReturn(request_id)
        wait_for_method_return_event = Event()
        self.method_return_events[request_id] = (wait_for_method_return_event, return_type)
        log(DEBUG, 'Waiting event registered for request {}'.format(request_id))
        wait_for_method_return_event.wait()
        return self.method_return_values.pop(request_id)
