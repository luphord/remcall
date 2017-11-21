from . import RemcallError
from queue import Queue
from .codec.util import view_hex

class QueueStream:
    stream_counter = 0
    def __init__(self, name=None):
        self.name = name or str(self.stream_counter)
        QueueStream.stream_counter += 1
        self.queue = Queue()

    def __repr__(self):
        return 'QueueStream("{}")'.format(self.name)

    def write(self, data: bytes):
        # lock!
        for byt in data:
            self.queue.put(byt)
        return len(data)

    def read(self, size: int):
        return b''.join(self.queue.get().to_bytes(1, 'little') for i in range(size))

    def flush(self):
        pass

class UnknownCommand(RemcallError):
    def __init__(self, command):
        super().__init__('Unknown command "{}"'.format(view_hex(command)))
        self.command = command

class UnknownType(RemcallError):
    def __init__(self, typ):
        super().__init__('Unknown type {!r}'.format(typ))
        self.typ = typ

class UnknownProxyObject(RemcallError):
    def __init__(self, obj):
        super().__init__('Unknown proxy object {!r}'.format(obj))
        self.proxy_obj = obj

class UnknownImplementationObjectReference(RemcallError):
    def __init__(self, key):
        super().__init__('Unknown implementation object reference {}'.format(key))
        self.object_id = key

class MethodNotAvailable(RemcallError):
    def __init__(self, method, impl_method_name, this):
        super().__init__('Method {} with expected implementation name {} does not exist on object {}'.format(method.name, impl_method_name, this))
        self.method = method
        self.impl_method_name = impl_method_name
        self.this = this


class DuplicateRegistrationForMethodReturn(RemcallError):
    def __init__(self, request_id):
        super().__init__('Multiple threads are waiting for method return with request ID {}'.format(request_id))
        self.request_id = request_id

class DuplicateMethodReturnValue(RemcallError):
    def __init__(self, request_id):
        super().__init__('Multiple method return values exits for request ID {}'.format(request_id))
        self.request_id = request_id

class MissingMethodReturnValueEvent(RemcallError):
    def __init__(self, request_id):
        super().__init__('No method return event exists for request ID {}'.format(request_id))
        self.request_id = request_id
