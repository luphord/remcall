from .util import view_hex


class RemcallError(Exception):
    pass


class WrongNumberOfBytesRead(RemcallError):
    def __init__(self, bytes_requested, bytes_read, offset):
        msg = 'Trying to read {} bytes from stream, got {}' \
              .format(bytes_requested, bytes_read)
        if offset:
            msg += ' at offset 0x{:x}'.format(offset)
        super().__init__(msg)
        self.bytes_requested = bytes_requested
        self.bytes_read = bytes_read
        self.offset = offset


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
        msg = 'Unknown implementation object reference {}' \
              .format(key)
        super().__init__(msg)
        self.object_id = key


class MethodNotAvailable(RemcallError):
    def __init__(self, method, impl_method_name, this):
        msg = ('Method {} with expected implementation name {}' +
               ' does not exist on object {}') \
              .format(method.name, impl_method_name, this)
        super().__init__(msg)
        self.method = method
        self.impl_method_name = impl_method_name
        self.this = this


class DuplicateRegistrationForMethodReturn(RemcallError):
    def __init__(self, request_id):
        msg = ('Multiple threads are waiting for method return' +
               ' with request ID {}').format(request_id)
        super().__init__(msg)
        self.request_id = request_id


class DuplicateMethodReturnValue(RemcallError):
    def __init__(self, request_id):
        msg = 'Multiple method return values exits for request ID {}' \
              .format(request_id)
        super().__init__(msg)
        self.request_id = request_id


class MissingMethodReturnValueEvent(RemcallError):
    def __init__(self, request_id):
        super().__init__('No method return event exists for request ID {}'
                         .format(request_id))
        self.request_id = request_id
