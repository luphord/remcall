import unittest

from remcall.naming import PythonNameConverter, CSharpNameConverter


class TestSchema(unittest.TestCase):

    def test_python_name_conversion(self):
        nc = PythonNameConverter()
        self.assertEqual('MyCamelCaseInterface', nc.interface_name('MyCamelCaseInterface'))
        self.assertEqual('AStatusEnum', nc.enum_name('AStatusEnum'))
        self.assertEqual('SOME_ENUM_FIELD', nc.enum_field_name('SomeEnumField'))
        self.assertEqual('MyRecord', nc.record_name('MyRecord'))
        self.assertEqual('some_record_field', nc.record_field_name('SomeRecordField'))
        self.assertEqual('do_nothing', nc.method_name('DoNothing'))
        self.assertEqual('some_param', nc.parameter_name('someParam'))

    def test_csharp_name_conversion(self):
        nc = CSharpNameConverter()
        self.assertEqual('IMyCamelCaseInterface', nc.interface_name('MyCamelCaseInterface'))
        self.assertEqual('AStatusEnum', nc.enum_name('AStatusEnum'))
        self.assertEqual('SomeEnumField', nc.enum_field_name('SomeEnumField'))
        self.assertEqual('MyRecord', nc.record_name('MyRecord'))
        self.assertEqual('SomeRecordField', nc.record_field_name('SomeRecordField'))
        self.assertEqual('DoNothing', nc.method_name('DoNothing'))
        self.assertEqual('someParam', nc.parameter_name('someParam'))
        self.assertEqual('someParam', nc.parameter_name('SomeParam'))
