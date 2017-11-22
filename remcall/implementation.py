from enum import Enum
from .error import UnknownType
from types import ModuleType

def create_enum_implementation(enum, name_converter):
    name = name_converter.enum_name(enum.name)
    enum_dict = {name_converter.enum_field_name(value): idx for idx, value in enumerate(enum.values)}
    return Enum(name, enum_dict) # Note: python stdlib Enum!

class EnumRecordImplementation:
    def __init__(self, schema, name_converter):
        self.name_converter = name_converter
        self.types = {}
        for enum in schema.enums:
            self.types[enum] = create_enum_implementation(enum, name_converter)
        self.impl = ModuleType('enum_record_implementation')
        for typ, impl in self.types.items():
            setattr(self.impl, typ.name, impl)

    def __call__(self, typ):
        if not typ in self.types:
            raise UnknownType(typ)
        return self.types[typ]
