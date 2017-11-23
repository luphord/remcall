from .schema import *
from .error import UnknownType

class IdentityNameConverter:
    def interface_name(self, name):
        return name

    def method_name(self, name):
        return name

    def parameter_name(self, name):
        return name

    def enum_name(self, name):
        return name

    def enum_field_name(self, name):
        return name

    def record_name(self, name):
        return name

    def record_field_name(self, name):
        return name

    def type_name(self, typ: Type):
        if isinstance(typ, Interface):
            return self.interface_name(typ.name)
        elif isinstance(typ, Enum):
            return self.enum_name(typ.name)
        elif isinstance(typ, Record):
            return self.record_name(typ.name)
        else:
            raise ValueError('No name for {!r}'.format(typ))

class PythonNameConverter(IdentityNameConverter):
    def _iter_method_name(self, name):
        for idx, letter in enumerate(name):
            if letter.isupper() and idx > 0:
                yield '_'
            yield letter.lower()

    def method_name(self, name):
        return ''.join(self._iter_method_name(name))

    def parameter_name(self, name):
        return self.method_name(name)

    def enum_field_name(self, name):
        return self.method_name(name).upper()

    def record_field_name(self, name):
        return self.method_name(name)

    def type_name(self, typ: Type):
        if isinstance(typ, Primitive):
            if typ == string:
                return 'str'
            elif typ in (int8, int16, int32, int64, uint8, uint16, uint32, uint64):
                return 'int'
            elif typ in (float32, float64):
                return 'float'
            elif typ == void:
                return 'None'
            elif typ == boolean:
                return 'bool'
            elif typ == date:
                return 'datetime.date'
            elif typ == datetime:
                return 'datetime.datetime'
            elif typ == time:
                return 'datetime.time'
            else:
                raise UnknownType(typ)
        return super().type_name(typ)

class CSharpNameConverter(IdentityNameConverter):
    def interface_name(self, name):
        return 'I{}'.format(super().interface_name(name))

    def parameter_name(self, name):
        return name[0].lower() + name[1:]
