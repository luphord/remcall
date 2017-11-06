from ..codec import SchemaReader
from ..codec import SchemaWriter
from .receive import Receiver
from .send import Sender
from .store import ReferenceStore
from .proxy import ProxyFactory
from ..schema import Type

class Bridge:
    def __init__(self, schema, instream, outstream, is_client):
        self.receiver = Receiver(schema, instream, None, self.return_method)
        self.sender = Sender(schema, outstream, None)
        self.proxy_factory = ProxyFactory(schema, self)
        self.is_client = is_client
        self.store = ReferenceStore(is_client, self.proxy_factory)
        self.receiver.get_object = self.store.get_object
        self.sender.get_id_for_object = self.store.get_id_for_object

    def call_method(self, method, this, args_dict):
        request_id = self.sender.call_method(method, this, args_dict)
        return self.receiver.wait_for_method_return(request_id, method.return_type)

    def return_method(self, request_id: int, return_type: Type, return_value):
        self.sender.return_method(request_id, return_type, return_value)
