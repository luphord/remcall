from .receive import Receiver
from .send import Sender
from .store import ReferenceStore
from .proxy import ProxyFactory
from ..implementation import EnumRecordImplementation
from ..schema import Type
from threading import Thread
from ..naming import PythonNameConverter


class Bridge:
    def __init__(self, schema, instream, outstream, main,
                 enum_record_implementation: EnumRecordImplementation):
        enum_record_implementation = enum_record_implementation \
                    or EnumRecordImplementation(schema, PythonNameConverter())
        self.receiver = Receiver(schema, instream, None, self.return_method,
                                 self.acknowledge_disconnect,
                                 enum_record_implementation.name_converter)
        self.sender = Sender(schema, outstream, None)
        self.proxy_factory = ProxyFactory(schema, self,
                                          enum_record_implementation
                                          .name_converter)
        self.main = main
        self.is_client = main is None
        self.store = ReferenceStore(self.is_client, self.proxy_factory)
        self.receiver.get_object = self.store.get_object
        self.receiver.get_enum_implementation = enum_record_implementation
        self.sender.get_id_for_object = self.store.get_id_for_object
        main_id = self.sender.get_id_for_object(self.main)
        if self.is_client:
            assert main_id == 0, ('ID of main object is {} but should ' +
                                  'be 0 on client as it is None') \
                                 .format(main_id)
        else:
            assert main_id == 1, ('ID of main object is {} but should ' +
                                  'be 1 on server').format(main_id)
        if self.is_client:
            self.server = self.receiver.get_object(1, schema.main_type)
        self.mainloop = self.receiver.mainloop
        self.mainloop_thread = Thread(target=self.mainloop)

    def __enter__(self):
        self.mainloop_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def call_method(self, method, this, args_dict):
        request_id = self.sender.call_method(method, this, args_dict)
        return self.receiver.wait_for_method_return(request_id,
                                                    method.return_type)

    def return_method(self, request_id: int, return_type: Type, return_value):
        self.sender.return_method(request_id, return_type, return_value)

    def disconnect(self):
        self.sender.disconnect()

    def acknowledge_disconnect(self):
        self.sender.acknowledge_disconnect()
