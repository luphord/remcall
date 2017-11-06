from ..codec import SchemaReader
from ..codec import SchemaWriter
from .receive import Receiver
from .send import Sender
from .store import ReferenceStore
from .proxy import ProxyFactory
from ..schema import Type

class Bridge:
    def __init__(self, schema, instream, outstream, main):
        self.receiver = Receiver(schema, instream, None, self.return_method)
        self.sender = Sender(schema, outstream, None)
        self.proxy_factory = ProxyFactory(schema, self)
        self.main = main
        self.is_client = main is None
        self.store = ReferenceStore(self.is_client, self.proxy_factory)
        self.receiver.get_object = self.store.get_object
        self.sender.get_id_for_object = self.store.get_id_for_object
        main_id = self.sender.get_id_for_object(self.main)
        if self.is_client:
            assert main_id == 0, 'ID of main object is {} but should be 0 on client as it is None'.format(main_id)
        else:
            assert main_id == 1, 'ID of main object is {} but should be 1 on server'.format(main_id)
        if self.is_client:
            self.server = self.receiver.get_object(1, schema.main_type)

    def call_method(self, method, this, args_dict):
        request_id = self.sender.call_method(method, this, args_dict)
        return self.receiver.wait_for_method_return(request_id, method.return_type)

    def return_method(self, request_id: int, return_type: Type, return_value):
        self.sender.return_method(request_id, return_type, return_value)
