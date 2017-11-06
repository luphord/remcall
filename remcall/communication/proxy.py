import types
from inspect import Signature, Parameter
from ..schema import *
from .util import UnknownType

class ProxyType:
    pass

class TypeWrapper:
    '''Wraps a core.Type and provides a nice annotation for Signature instances'''
    def __init__(self, typ):
        self.typ = typ

    def __repr__(self):
        return self.typ.name

class MethodProxy:
    def __init__(self, interface, method, bridge):
        self.interface = interface
        self.method = method
        self.bridge = bridge
        params = [Parameter(name, Parameter.POSITIONAL_OR_KEYWORD, annotation=TypeWrapper(tp)) \
                           for tp, name in method.arguments]
        params.insert(0, Parameter('self', Parameter.POSITIONAL_ONLY, annotation=TypeWrapper(self.interface)))
        self.__signature__ = Signature(parameters=params, return_annotation=TypeWrapper(method.return_type))

    def __call__(self, this, *args, **kwargs):
        bound_values = self.__signature__.bind(this, *args, **kwargs)
        return_value = self.bridge.call_method(self.method, this, bound_values.arguments)
        return return_value

    def __get__(self, instance, cls):
        if instance:
            def bound_method_proxy(*args, **kwargs):
                return self(instance, *args, **kwargs)
            bound_method_proxy.__signature__ = self.__signature__
            return bound_method_proxy
        else:
            return self

def create_proxy_class(interface, bridge):
    proxy_class_name = '{}Proxy'.format(interface.name)
    method_dict = {}
    for method in interface.methods:
        method_dict[method.name] = MethodProxy(interface, method, bridge)
    return types.new_class(proxy_class_name, (ProxyType,), {}, lambda ns: ns.update(method_dict))

def create_proxy_classes(schema, bridge):
    for interface in schema.interfaces:
        yield create_proxy_class(interface, bridge)

def create_proxy_classes_dict(schema, bridge):
    return {cls.__name__: cls for cls in create_proxy_classes(schema, bridge)}

class ProxyFactory:
    def __init__(self, schema, bridge):
        self.proxy_classes = {interface: create_proxy_class(interface, bridge) for interface in schema.interfaces}

    def __call__(self, typ: Type):
        if not typ in self.proxy_classes:
            raise UnknownType(typ)
        return self.proxy_classes[typ]()
