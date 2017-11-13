import unittest

from remcall.naming import PythonNameConverter


class TestSchema(unittest.TestCase):

    def test_python_name_conversion(self):
        nc = PythonNameConverter()
        self.assertEqual('MyCamelCaseClass', nc.interface_name('MyCamelCaseClass'))
        self.assertEqual('AStatusEnum', nc.enum_name('AStatusEnum'))
        self.assertEqual('MyRecord', nc.record_name('MyRecord'))
        self.assertEqual('some_record_field', nc.record_field_name('SomeRecordField'))
        self.assertEqual('do_nothing', nc.method_name('DoNothing'))
        self.assertEqual('some_param', nc.parameter_name('someParam'))
