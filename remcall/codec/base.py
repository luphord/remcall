from binascii import hexlify

MAGIC = b'REMCALL'
SCHEMA = b'SCHEMA'
COMM = b'COMM'

def view_hex(b: bytes):
    return '0x{}'.format(hexlify(b).decode('ascii'))

# Commands
DECLARE_ENUM = b'\x02'
DECLARE_RECORD = b'\x03'
DECLARE_INTERFACE = b'\x04'
