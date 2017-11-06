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

class ClientUserImpl:
    def GetAge(self):
        return 666

class TestSchema(unittest.TestCase):

    def setUp(self):
        import base64, io
        serialized_schema = base64.decodebytes(b'''
        UkVNQ0FMTFNDSEVNQQAAAAhNeVNjaGVtYQAAAAIAAAAEAAAAAQAAAAAAAAACAgAAABAAAAAGU3Rh
        dHVzAAAAAwAAAApSZWdpc3RlcmVkAAAACUFjdGl2YXRlZAAAAAZMb2NrZWQEAAAAEQAAAARUZXN0
        AAAAAAQAAAASAAAABFVzZXIAAAAIAAAAAAAHR2V0TmFtZQAAAAAAAAAMAAEAAAAHU2V0TmFtZQAA
        AAEAAAAMAAAABG5hbWUAAAAAAAIAAAAMR2V0QmlydGhkYXRlAAAAAAAAAA0AAwAAAAxHZXRMYXN0
        TG9naW4AAAAAAAAADwAEAAAACkdldEZyaWVuZHMAAAAA////7gAFAAAACUFkZEZyaWVuZAAAAAIA
        AAASAAAABHVzZXIAAAAKAAAABmRlZ3JlZQAAAAAABgAAAAZHZXRBZ2UAAAAAAAAABwAHAAAACUdl
        dFN0YXR1cwAAAAAAAAAQhoDJxvkhM+M9xtjOp6wMhIUpsyKgRUApgH+LoWkvOxg=
        ''')
        self.schema = schema_from_bytes(serialized_schema)

    def test_basic_communication(self):
        stream1 = QueueStream('server-calls-client')
        stream2 = QueueStream('client-calls-server')
        client_bridge = Bridge(self.schema, stream1, stream2, True)
        server_bridge = Bridge(self.schema, stream2, stream1, False)
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


if __name__ == '__main__':
    unittest.main()
