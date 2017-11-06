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
        self.user_schema = Schema('MySchema', [Array(User), User, Array(Status), Status, Interface('Test', [])])

    def test_csharp_generation(self):
        generator = CSharphCodeGenerator(self.user_schema)
        with io.StringIO() as f:
            generator.write_schema(f)
        # todo: read and check


if __name__ == '__main__':
    unittest.main()
