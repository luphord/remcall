from logging import log, DEBUG
from ..schema import Type
from .proxy import ProxyType
from .util import UnknownProxyObject, UnknownImplementationObjectReference

class IdStore:
    def __init__(self):
        self.id_to_obj = {}
        self.obj_to_id = {}

    def __getitem__(self, key: int):
        return self.id_to_obj[key]

    def __setitem__(self, key: int, obj):
        self.id_to_obj[key] = obj
        self.obj_to_id[obj] = key

    def __delitem__(self, key):
        value = self.id_to_obj[key]
        del self.id_to_obj[key]
        del self.obj_to_id[value]

    def __contains__(self, key):
        return key in self.id_to_obj

    def get_id_for_object(self, obj):
        return self.obj_to_id[obj]

    def delete_object(self, obj):
        key = self.obj_to_id[obj]
        del self.obj_to_id[obj]
        del self.id_to_obj[key]

    def contains_object(self, obj):
        return obj in self.obj_to_id


class ReferenceStore:
    def __init__(self, is_client, proxy_factory):
        self.is_client = is_client
        self.proxy_factory = proxy_factory
        self.proxy_objects = IdStore()
        self.implementation_objects = IdStore()
        self._next_object_id = 0

    @property
    def object_id_sign(self):
        return -1 if self.is_client else 1

    def next_object_id(self):
        self._next_object_id += self.object_id_sign
        return self._next_object_id

    def get_proxy_object(self, key: int, typ: Type):
        if not key in self.proxy_objects:
            self.proxy_objects[key] = self.proxy_factory(typ)
        return self.proxy_objects[key]

    def get_implementation_object(self, key: int):
        if not key in self.implementation_objects:
            raise UnknownImplementationObjectReference(key)
        return self.implementation_objects[key]

    def get_id_for_proxy_object(self, obj):
        if not self.proxy_objects.contains_object(obj):
            raise UnknownProxyObject(obj)
        return self.proxy_objects.get_id_for_object(obj)

    def get_id_for_implementation_object(self, obj):
        if not self.implementation_objects.contains_object(obj):
            self.implementation_objects[self.next_object_id()] = obj
        return self.implementation_objects.get_id_for_object(obj)

    def get_object(self, key: int, typ: Type):
        log(DEBUG, '{} store is getting object for ID {}'.format('client' if self.is_client else 'server', key))
        if key == 0:
            return None
        is_proxy_obj = (self.is_client and key > 0) or (not self.is_client and key < 0)
        log(DEBUG, '{} references {} object'.format(key, 'a proxy' if is_proxy_obj else 'an implementation'))
        return self.get_proxy_object(key, typ) if is_proxy_obj else self.get_implementation_object(key)

    def get_id_for_object(self, obj):
        if obj is None:
            return 0
        is_proxy_obj = isinstance(obj, ProxyType)
        return self.get_id_for_proxy_object(obj) if is_proxy_obj else self.get_id_for_implementation_object(obj)
