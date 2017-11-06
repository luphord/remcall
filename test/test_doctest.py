import unittest
import doctest
import remcall.schema.core

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(remcall.schema.core))
    return tests
