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

    def record_field_name(self, name):
        return self.method_name(name)

class CSharpNameConverter(IdentityNameConverter):
    def parameter_name(self, name):
        return name[0].lower() + name[1:]
