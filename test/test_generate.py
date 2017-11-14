import unittest
import io
from remcall.schema import *
from remcall import SchemaReader
from remcall.generate import CSharphCodeGenerator

class TestSchema(unittest.TestCase):

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
        Main = Interface('Main', [Method('GetFirstUser', [], User)])
        self.user_schema = Schema('MySchema', [Main, Array(User), User, Array(Status), Status, Interface('Test', [Method('DoNothing', [], void)])])

    def test_csharp_generation(self):
        generator = CSharphCodeGenerator(self.user_schema)
        with io.StringIO() as f:
            generator.write_schema(f)
        # todo: read and check

    def test_csharp_names(self):
        generator = CSharphCodeGenerator(self.user_schema)
        self.assertEqual('Status', generator.typename(self.user_schema.type_schemas.Status))
        self.assertEqual('Status[]', generator.typename(Array(self.user_schema.type_schemas.Status)))
        self.assertEqual('IUser', generator.typename(self.user_schema.type_schemas.User))
        self.assertEqual('IUser[]', generator.typename(Array(self.user_schema.type_schemas.User)))
        self.assertEqual('string', generator.typename(string))
        self.assertEqual('string[]', generator.typename(Array(string)))


if __name__ == '__main__':
    unittest.main()
