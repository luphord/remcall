from binascii import hexlify

class RemcallError(Exception):
    pass

class WrongNumberOfBytesRead(RemcallError):
    def __init__(self, bytes_requested, bytes_read, offset):
        msg = 'Trying to read {} bytes from stream, got {}'.format(bytes_requested, bytes_read)
        if offset:
            msg += ' at offset 0x{:x}'.format(offset)
        super().__init__(msg)
        self.bytes_requested = bytes_requested
        self.bytes_read = bytes_read
        self.offset = offset

def view_hex(b: bytes):
    return '0x{}'.format(hexlify(b).decode('ascii'))
