import unittest
from remcall import schema_from_bytes, Bridge
from remcall.communication.proxy import create_proxy_classes_dict
from remcall.communication.util import QueueStream
from threading import Thread

#import logging
#logging.basicConfig(level=logging.DEBUG)

class UserImpl:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.friends = {}

    def GetAge(self):
        return self.age

    def AddFriend(self, user, degree):
        #print('Adding {} as a friend of degree {}'.format(user, degree))
        #print('Age of {} is {}'.format(user, user.GetAge()))
        #print('Adding friend completed')
        self.friends[user] = (degree, user.GetAge())

class MainImpl:
    def __init__(self):
        self.first_user = UserImpl('First User', 2**32-1)

    def GetFirstUser(self):
        return self.first_user

class ClientUserImpl:
    def GetAge(self):
        return 666

class TestCommunication(unittest.TestCase):

    def setUp(self):
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
        self.schema = schema_from_bytes(serialized_schema)
        self.stream1 = QueueStream('server-calls-client')
        self.stream2 = QueueStream('client-calls-server')

    def test_basic_communication(self):
        client_bridge = Bridge(self.schema, self.stream1, self.stream2, None)
        server_bridge = Bridge(self.schema, self.stream2, self.stream1, "not-required-here")
        Thread(target=client_bridge.receiver.mainloop).start()
        Thread(target=server_bridge.receiver.mainloop).start()

        brian = UserImpl(name='Brian', age=29)
        brian_id = server_bridge.store.get_id_for_object(brian)
        brian_proxy = client_bridge.store.get_object(brian_id, self.schema.type_schemas.User) #UserProxy()
        self.assertEqual(brian.age, brian_proxy.GetAge())
        _client_u = ClientUserImpl()
        brian_proxy.AddFriend(_client_u, 1.1)
        self.assertEqual(1, len(brian.friends))
        client_bridge.receiver.exit_mainloop = True
        server_bridge.receiver.exit_mainloop = True
        client_bridge.sender.noop()
        server_bridge.sender.noop()

    def test_main_start(self):
        main = MainImpl()
        client_bridge = Bridge(self.schema, self.stream1, self.stream2, None)
        server_bridge = Bridge(self.schema, self.stream2, self.stream1, main)

        Thread(target=client_bridge.receiver.mainloop).start()
        Thread(target=server_bridge.receiver.mainloop).start()

        first_user = client_bridge.server.GetFirstUser()
        self.assertEqual(main.first_user.age, first_user.GetAge())

        client_bridge.receiver.exit_mainloop = True
        server_bridge.receiver.exit_mainloop = True
        client_bridge.sender.noop()
        server_bridge.sender.noop()


if __name__ == '__main__':
    unittest.main()
