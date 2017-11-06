import unittest
import io
from remcall.schema import Schema, Enum, Interface, Method, string, float32, uint32, void, date, datetime, Array
from remcall import SchemaReader, read_schema, SchemaWriter, schema_to_bytes

class TestSchema(unittest.TestCase):

    def reserialize_and_check(self, schema):
        serialized_schema = schema_to_bytes(schema)
        with io.BytesIO(serialized_schema) as stream:
            schema2 = read_schema(stream)
        serialized_schema2 = schema_to_bytes(schema2)
        self.assertEqual( serialized_schema, serialized_schema2 )

    def setUp(self):
        Status = Enum('Status', ['Registered', 'Activated', 'Locked'])
        User = Interface('User', [])
        User.methods = [
            Method('GetName', [], string),
            Method('SetName', [(string, 'name')], void),
            Method('GetBirthdate', [], date),
            Method('GetLastLogin', [], datetime),
            Method('GetFriends', [], Array(User)),
            Method('AddFriend', [(User, 'user'), (float32, 'degree')], void),
            Method('GetAge', [], uint32),
            Method('GetStatus', [], Status)
        ]
        self.user_schema = Schema('MySchema', [Array(User), User, Array(Status), Status, Interface('Test', [])])

    def test_user_reserialization(self):
        self.reserialize_and_check(self.user_schema)

    def test_user_serialization_to_file(self):
        from tempfile import TemporaryFile
        with TemporaryFile(mode='w+b') as f:
            SchemaWriter(self.user_schema, f).write_schema()
            f.seek(0)
            schema_read = read_schema(f)
            self.assertEqual(schema_to_bytes(self.user_schema), schema_to_bytes(schema_read))

    def test_bad_stream_reading(self):
        from remcall.codec.util import WrongNumberOfBytesRead
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

if __name__ == '__main__':
    unittest.main()
