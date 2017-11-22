import unittest
import io
from remcall.schema import Schema, Enum, Record, Interface, Method, string, float32, uint32, uint16, void, date, datetime, Array
from remcall import SchemaReader, read_schema, SchemaWriter, schema_to_bytes

Status = Enum('Status', ['Registered', 'Activated', 'Locked'])
User = Interface('User', [])
Address = Record('Address', [(string, 'Street'), (uint16, 'Number')])
User.methods = [
    Method('GetName', [], string),
    Method('SetName', [(string, 'name')], void),
    Method('GetBirthdate', [], date),
    Method('GetLastLogin', [], datetime),
    Method('GetFriends', [], Array(User)),
    Method('AddFriend', [(User, 'user'), (float32, 'degree')], void),
    Method('GetAge', [], uint32),
    Method('GetStatus', [], Status),
    Method('GetAddress', [], Address)
]
Main = Interface('Main', [Method('GetFirstUser', [], User)])
USER_SCHEMA = Schema('MySchema', [Main, Array(User), User, Address, Array(Status), Status, Interface('Test', [Method('DoNothing', [], void)])])


class TestSchema(unittest.TestCase):

    def reserialize_and_check(self, schema):
        serialized_schema = schema_to_bytes(schema)
        with io.BytesIO(serialized_schema) as stream:
            schema2 = read_schema(stream)
        serialized_schema2 = schema_to_bytes(schema2)
        self.assertEqual( serialized_schema, serialized_schema2 )

    def setUp(self):
        self.user_schema = USER_SCHEMA

    def test_missing_main(self):
        with self.assertRaises(AssertionError):
            Schema('NoMainSchema', [Interface('SomeInterface', [Method('DoSomething', [], void)])])

    def test_missing_methods(self):
        with self.assertRaises(AssertionError):
            Schema('NoMethodsInterfaceSchema', [Interface('Main', [])])

    def test_bad_argument_definition(self):
        with self.assertRaises(AssertionError):
            Method('m', [(string, '')], void)
        with self.assertRaises(AssertionError):
            Method('m', [(string, '1a')], void)
        with self.assertRaises(AssertionError):
            Method('m', [('test', 'a')], void)
        with self.assertRaises(AssertionError):
            Record('r', [(string, '')])
        with self.assertRaises(AssertionError):
            Record('r', [(string, '1a')])
        with self.assertRaises(AssertionError):
            Record('r', [('test', 'a')])

    def test_void_arguments_or_fields(self):
        with self.assertRaises(AssertionError):
            Method('m', [(void, 'arg')], void)
        with self.assertRaises(AssertionError):
            Record('r', [(void, 'field')])

    def test_too_many_enum_values(self):
        Enum('e', ['value{}'.format(i) for i in range(256)])
        with self.assertRaises(AssertionError):
            Enum('e', ['value{}'.format(i) for i in range(257)])

    def test_user_reserialization(self):
        self.reserialize_and_check(self.user_schema)

    def test_user_serialization_to_file(self):
        from tempfile import TemporaryFile
        with TemporaryFile(mode='w+b') as f:
            SchemaWriter(self.user_schema, f).write_schema()
            f.seek(0)
            schema_read = read_schema(f)
            self.assertEqual(schema_to_bytes(self.user_schema), schema_to_bytes(schema_read))
        #with open('schema.rmc', mode='wb') as f:
        #    import base64
        #    f.write(base64.encodebytes(schema_to_bytes(self.user_schema)))

    def test_bad_stream_reading(self):
        from remcall.error import WrongNumberOfBytesRead
        reader = SchemaReader(io.BytesIO(b'123'))
        with self.assertRaises(WrongNumberOfBytesRead):
            reader.read_from_stream(4)

    def test_name_reading(self):
        namestream = io.BytesIO(b'\x00\x00\x00\x03Abc\x00\x00\x00\x03a_1\x00\x00\x00\x00\x00\x00\x00\x03123')
        reader = SchemaReader(namestream)
        self.assertEqual('Abc', reader.read_name())
        with self.assertRaises(AssertionError):
            reader.read_name() # bad char '_'
        with self.assertRaises(AssertionError):
            reader.read_name() # bad length 0
        with self.assertRaises(AssertionError):
            reader.read_name() # bad first char '1'

    def test_name_writing(self):
        namestream = io.BytesIO()
        writer = SchemaWriter(self.user_schema, namestream)
        writer.write_name('Abc')
        namestream.seek(0)
        self.assertEqual(b'\x00\x00\x00\x03Abc', namestream.read(7))
        with self.assertRaises(AssertionError):
            writer.write_name('a_1') # bad char '_'
        with self.assertRaises(AssertionError):
            writer.write_name('') # bad length 0
        with self.assertRaises(AssertionError):
            writer.write_name('123') # bad first char '1'

    def test_int_type_writing(self):
        import struct
        stream = io.BytesIO()
        writer = SchemaWriter(self.user_schema, stream)
        writer.write_int8(2**7-1)
        with self.assertRaises(struct.error):
            writer.write_int8(2**7)
        writer.write_uint8(2**8-1)
        with self.assertRaises(struct.error):
            writer.write_uint8(2**8)
        writer.write_int16(2**15-1)
        with self.assertRaises(struct.error):
            writer.write_int16(2**15)
        writer.write_uint16(2**16-1)
        with self.assertRaises(struct.error):
            writer.write_uint16(2**16)
        writer.write_int32(2**31-1)
        with self.assertRaises(struct.error):
            writer.write_int32(2**31)
        writer.write_uint32(2**32-1)
        with self.assertRaises(struct.error):
            writer.write_uint32(2**32)
        writer.write_int64(2**63-1)
        with self.assertRaises(struct.error):
            writer.write_int64(2**63)
        writer.write_uint64(2**64-1)
        with self.assertRaises(struct.error):
            writer.write_uint64(2**64)

if __name__ == '__main__':
    unittest.main()
