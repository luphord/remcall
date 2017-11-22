import unittest
from remcall import schema_from_bytes, Bridge, Receiver
from remcall.communication.proxy import create_proxy_classes_dict
from remcall.util import QueueStream
from remcall.error import UnknownCommand
from remcall.implementation import EnumRecordImplementation
from remcall.naming import PythonNameConverter

#import logging
#logging.basicConfig(level=logging.DEBUG)

import base64, io
serialized_schema = base64.decodebytes(b'''
UkVNQ0FMTFNDSEVNQQAAAAhNeVNjaGVtYQAAAAIAAAAEAAAAAQAAAAEAAAADAgAAABAAAAAGU3Rh
dHVzAAAAAwAAAApSZWdpc3RlcmVkAAAACUFjdGl2YXRlZAAAAAZMb2NrZWQDAAAAEQAAAAdBZGRy
ZXNzAAAAAgAAAAUAAAAGTnVtYmVyAAAADAAAAAZTdHJlZXQEAAAAEgAAAARNYWluAAAAAQAAAAAA
DEdldEZpcnN0VXNlcgAAAAAAAAAUBAAAABMAAAAEVGVzdAAAAAEAAQAAAAlEb05vdGhpbmcAAAAA
AAAAAAQAAAAUAAAABFVzZXIAAAAJAAIAAAAHR2V0TmFtZQAAAAAAAAAMAAMAAAAHU2V0TmFtZQAA
AAEAAAAMAAAABG5hbWUAAAAAAAQAAAAMR2V0QmlydGhkYXRlAAAAAAAAAA0ABQAAAAxHZXRMYXN0
TG9naW4AAAAAAAAADwAGAAAACkdldEZyaWVuZHMAAAAA////7AAHAAAACUFkZEZyaWVuZAAAAAIA
AAAUAAAABHVzZXIAAAAKAAAABmRlZ3JlZQAAAAAACAAAAAZHZXRBZ2UAAAAAAAAABwAJAAAACUdl
dFN0YXR1cwAAAAAAAAAQAAoAAAAKR2V0QWRkcmVzcwAAAAAAAAARFMkyjcRCzj7DYZ5SzZdAy94d
1GLcXw1fiChjAPOZETA=
''')
SCHEMA = schema_from_bytes(serialized_schema)
enum_record_implementation = EnumRecordImplementation(SCHEMA, PythonNameConverter())
Status = enum_record_implementation.impl.Status

class UserImpl:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.friends = {}

    def get_age(self):
        return self.age

    def get_status(self):
        return Status.ACTIVATED

    def add_friend(self, user, degree):
        #print('Adding {} as a friend of degree {}'.format(user, degree))
        #print('Age of {} is {}'.format(user, user.GetAge()))
        #print('Adding friend completed')
        self.friends[user] = (degree, user.get_age())

class MainImpl:
    def __init__(self):
        self.first_user = UserImpl('First User', 2**32-1)

    def get_first_user(self):
        return self.first_user

class ClientUserImpl:
    def get_age(self):
        return 666

class TestCommunication(unittest.TestCase):

    def setUp(self):
        self.schema = SCHEMA
        self.stream1 = QueueStream('server-calls-client')
        self.stream2 = QueueStream('client-calls-server')

    def test_basic_communication(self):
        client_bridge = Bridge(self.schema, self.stream1, self.stream2, None, None)
        server_bridge = Bridge(self.schema, self.stream2, self.stream1, "not-required-here", None)
        client_bridge.mainloop_thread.start()
        server_bridge.mainloop_thread.start()

        brian = UserImpl(name='Brian', age=29)
        brian_id = server_bridge.store.get_id_for_object(brian)
        brian_proxy = client_bridge.store.get_object(brian_id, self.schema.type_schemas.User) #UserProxy()
        self.assertEqual(brian.age, brian_proxy.get_age())
        _client_u = ClientUserImpl()
        brian_proxy.add_friend(_client_u, 1.1)
        self.assertEqual(1, len(brian.friends))

        client_bridge.disconnect()

    def test_main_start(self):
        main = MainImpl()
        server_bridge = Bridge(self.schema, self.stream2, self.stream1, main, enum_record_implementation)
        server_bridge.mainloop_thread.start()

        with Bridge(self.schema, self.stream1, self.stream2, None, enum_record_implementation) as client_bridge:
            first_user = client_bridge.server.get_first_user()
            self.assertEqual(main.first_user.age, first_user.get_age())
            self.assertEqual(first_user.get_status(), Status.ACTIVATED)

    def test_unknown_command(self):
        from io import BytesIO
        receiver = Receiver(self.schema, BytesIO(b'\xff'), None, None, None, None)
        with self.assertRaises(UnknownCommand):
            receiver.mainloop()


if __name__ == '__main__':
    unittest.main()
