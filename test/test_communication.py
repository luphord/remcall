import unittest
from remcall import schema_from_bytes, Bridge, Receiver
from remcall.communication.proxy import create_proxy_classes_dict
from remcall.communication.util import QueueStream, UnknownCommand

#import logging
#logging.basicConfig(level=logging.DEBUG)

import base64, io
serialized_schema = base64.decodebytes(b'''
UkVNQ0FMTFNDSEVNQQAAAAhNeVNjaGVtYQAAAAIAAAAEAAAAAQAAAAAAAAADAgAAABAAAAAGU3Rh
dHVzAAAAAwAAAApSZWdpc3RlcmVkAAAACUFjdGl2YXRlZAAAAAZMb2NrZWQEAAAAEQAAAARNYWlu
AAAAAQAAAAAADEdldEZpcnN0VXNlcgAAAAAAAAATBAAAABIAAAAEVGVzdAAAAAEAAQAAAAlEb05v
dGhpbmcAAAAAAAAAAAQAAAATAAAABFVzZXIAAAAIAAIAAAAHR2V0TmFtZQAAAAAAAAAMAAMAAAAH
U2V0TmFtZQAAAAEAAAAMAAAABG5hbWUAAAAAAAQAAAAMR2V0QmlydGhkYXRlAAAAAAAAAA0ABQAA
AAxHZXRMYXN0TG9naW4AAAAAAAAADwAGAAAACkdldEZyaWVuZHMAAAAA////7QAHAAAACUFkZEZy
aWVuZAAAAAIAAAATAAAABHVzZXIAAAAKAAAABmRlZ3JlZQAAAAAACAAAAAZHZXRBZ2UAAAAAAAAA
BwAJAAAACUdldFN0YXR1cwAAAAAAAAAQdv/Lr30U9Q/5Cpfv+dI1eic2vy4/AnoInSRbV4y9hXM=
''')
SCHEMA = schema_from_bytes(serialized_schema)

class UserImpl:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.friends = {}

    def get_age(self):
        return self.age

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
        client_bridge = Bridge(self.schema, self.stream1, self.stream2, None)
        server_bridge = Bridge(self.schema, self.stream2, self.stream1, "not-required-here")
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
        server_bridge = Bridge(self.schema, self.stream2, self.stream1, main)
        server_bridge.mainloop_thread.start()

        with Bridge(self.schema, self.stream1, self.stream2, None) as client_bridge:
            first_user = client_bridge.server.get_first_user()
            self.assertEqual(main.first_user.age, first_user.get_age())

    def test_unknown_command(self):
        from io import BytesIO
        receiver = Receiver(self.schema, BytesIO(b'\xff'), None, None, None, None)
        with self.assertRaises(UnknownCommand):
            receiver.mainloop()


if __name__ == '__main__':
    unittest.main()
