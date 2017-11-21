from enum import Enum
from .communication.util import UnknownType

def create_enum_implementation(enum, name_converter):
    name = name_converter.enum_name(enum.name)
    enum_dict = {name_converter.enum_field_name(value): idx for idx, value in enumerate(enum.values)}
    return Enum(name, enum_dict) # Note: python stdlib Enum!

class EnumRecordFactory:
    def __init__(self, schema, name_converter):
        self.types = {}
        for enum in schema.enums:
            self.types[enum] = create_enum_implementation(enum, name_converter)

    def __call__(self, typ):
        if not typ in self.types:
            raise UnknownType(typ)
        return self.types[typ]
