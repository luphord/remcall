from enum import Enum
from types import ModuleType, new_class
from inspect import Signature, Parameter
from .error import UnknownType
from .util import TypeWrapper


class RecordType:
    pass


def create_enum_implementation(enum, name_converter):
    name = name_converter.enum_name(enum.name)
    enum_dict = {name_converter.enum_field_name(value): idx
                 for idx, value in enumerate(enum.values)}
    return Enum(name, enum_dict)  # Note: python stdlib Enum!


def create_record_implementation(record, name_converter):
    name = name_converter.record_name(record.name)
    params = [Parameter(name_converter.parameter_name(name),
                        Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=TypeWrapper(tp, name_converter))
              for tp, name in record.fields]
    params.insert(0, Parameter('self', Parameter.POSITIONAL_ONLY,
                               annotation=TypeWrapper(record, name_converter)))
    __signature__ = Signature(parameters=params)

    def __init__(self, *args, **kwargs):
        bound_values = __signature__.bind(self, *args, **kwargs)
        for key, val in bound_values.arguments.items():
            setattr(self, key, val)

    __init__.__signature__ = __signature__
    return new_class(name, (RecordType,), {},
                     lambda ns: ns.update(dict(__init__=__init__)))


class EnumRecordImplementation:
    def __init__(self, schema, name_converter):
        self.name_converter = name_converter
        self.types = {}
        for enum in schema.enums:
            self.types[enum] = create_enum_implementation(enum, name_converter)
        for record in schema.records:
            self.types[record] = create_record_implementation(record,
                                                              name_converter)
        self.impl = ModuleType('enum_record_implementation')
        for typ, impl in self.types.items():
            setattr(self.impl, impl.__name__, impl)

    def __call__(self, typ):
        if typ not in self.types:
            raise UnknownType(typ)
        return self.types[typ]
