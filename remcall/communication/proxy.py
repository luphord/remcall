import types
from inspect import Signature, Parameter
from ..schema import Type
from ..util import TypeWrapper
from ..error import UnknownType


class ProxyType:
    pass


class MethodProxy:
    def __init__(self, interface, method, bridge, name_converter):
        self.interface = interface
        self.method = method
        self.bridge = bridge
        params = [Parameter(name_converter.parameter_name(name),
                            Parameter.POSITIONAL_OR_KEYWORD,
                            annotation=TypeWrapper(tp, name_converter))
                  for tp, name in method.arguments]
        params.insert(0, Parameter('self', Parameter.POSITIONAL_ONLY,
                                   annotation=TypeWrapper(self.interface,
                                                          name_converter)))
        return_type = TypeWrapper(method.return_type, name_converter)
        self.__signature__ = Signature(parameters=params,
                                       return_annotation=return_type)

    def __call__(self, this, *args, **kwargs):
        bound_values = self.__signature__.bind(this, *args, **kwargs)
        return_value = self.bridge.call_method(self.method, this,
                                               bound_values.arguments)
        return return_value

    def __get__(self, instance, cls):
        if instance:
            def bound_method_proxy(*args, **kwargs):
                return self(instance, *args, **kwargs)
            bound_method_proxy.__signature__ = self.__signature__
            return bound_method_proxy
        else:
            return self


def create_proxy_class(interface, bridge, name_converter):
    proxy_class_name = '{}Proxy'.format(name_converter.type_name(interface))
    method_dict = {}
    for method in interface.methods:
        method_dict[name_converter.method_name(method.name)] = \
            MethodProxy(interface, method, bridge, name_converter)

    def _add_methods(ns):
        ns.update(method_dict)

    return types.new_class(proxy_class_name, (ProxyType,), {}, _add_methods)


def create_proxy_classes(schema, bridge):
    for interface in schema.interfaces:
        yield create_proxy_class(interface, bridge)


def create_proxy_classes_dict(schema, bridge, name_converter):
    return {cls.__name__: cls
            for cls in create_proxy_classes(schema, bridge, name_converter)}


class ProxyFactory:
    def __init__(self, schema, bridge, name_converter):
        self.proxy_classes = {}
        for interface in schema.interfaces:
            self.proxy_classes[interface] = create_proxy_class(interface,
                                                               bridge,
                                                               name_converter)

    def __call__(self, typ: Type):
        if typ not in self.proxy_classes:
            raise UnknownType(typ)
        return self.proxy_classes[typ]()
