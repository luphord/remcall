import unittest
import io
from remcall.schema import Schema, Enum, Interface, Method, string, uint8, float32, uint32, int64, uint64, void, date, datetime, Array
from remcall import SchemaReader, read_schema, SchemaWriter, schema_to_bytes

File = Interface('File', [])
Mode = Enum('Mode', ['Read', 'Write', 'Append'])
FileStream = Interface('FileStream', [])
Directory = Interface('Directory', [])
File.methods = [
    Method('GetName', [], string),
    Method('SetName', [(string, 'name')], void),
    Method('GetCreationTime', [], datetime),
    Method('GetModificationTime', [], datetime),
    Method('GetDirectory', [], Directory),
    Method('Open', [(Mode, 'mode')], FileStream),
    Method('Delete', [], void),
    Method('Move', [(Directory, 'directory')], void),
    Method('Copy', [(Directory, 'directory')], void),
]
FileStream.methods = [
    Method('Seek', [(uint64, 'offset')], void),
    Method('Read', [(int64, 'length')], Array(uint8)),
    Method('Write', [(Array(uint8), 'data')], uint64),
]
Directory.methods = [
    Method('GetName', [], string),
    Method('SetName', [(string, 'name')], void),
    Method('CreateFile', [(string, 'name')], File),
    Method('GetFiles', [], Array(File)),
    Method('GetSubDirectories', [], Array(Directory)),
]
Main = Interface('Main', [Method('GetRoot', [], Directory)])
FS_SCHEMA = Schema('FileSystemSchema', [File, Mode, FileStream, Directory, Main])

class TestFileSystemSchema(unittest.TestCase):

    def reserialize_and_check(self, schema):
        serialized_schema = schema_to_bytes(schema)
        with io.BytesIO(serialized_schema) as stream:
            schema2 = read_schema(stream)
        serialized_schema2 = schema_to_bytes(schema2)
        self.assertEqual( serialized_schema, serialized_schema2 )
        #with open('fs.rmc', 'wb') as f:
        #    f.write(serialized_schema2)

    def setUp(self):
        self.fs_schema = FS_SCHEMA

    def test_fs_schema_reserialization(self):
        self.reserialize_and_check(self.fs_schema)
