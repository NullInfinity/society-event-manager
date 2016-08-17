#!/usr/bin/env python3
import unittest
from membership import Name
from membership import Member

class MemberTestCase(unittest.TestCase):
    def setUp(self):
        self.barcode = '00000000'
        self.name = Name('Ted', 'Bobson')
        self.college = 'Wolfson'

    def test_falsiness(self):
        self.assertTrue(Member(self.barcode, name=self.name))
        self.assertTrue(Member(self.barcode, name=self.name, college=self.college))
        self.assertTrue(Member(self.barcode))
        self.assertTrue(Member(None, name=self.name))

        self.assertFalse(Member(None)) # name=None by default
        self.assertFalse(Member(None, college=self.college))

    def test_equality(self):
        self.assertEqual(Member(self.barcode, name=self.name), Member(self.barcode, name=self.name))
        self.assertEqual(Member(self.barcode), Member(self.barcode))
        self.assertEqual(Member(None, self.name), Member(None, self.name))

    def test_inequality(self):
        self.assertNotEqual(Member(None, name=self.name), Member(self.barcode))
        self.assertNotEqual(Member(self.barcode, name=self.name), Member(self.barcode))
        self.assertNotEqual(Member(self.barcode, name=self.name), Member('11111111', name=self.name))

    def test_varargs_init(self):
        self.assertEqual(Member(None, name=self.name), Member(None, self.name.first(), self.name.last()))
        self.assertEqual(Member(self.barcode, name=Name('Ted', 'Bobson', 'Jones')), Member(self.barcode, 'Ted', 'Bobson', 'Jones'))
        self.assertEqual(Member(self.barcode, name=self.name), Member(self.barcode, 'Billy', name=self.name))

if __name__ == '__main__':
    unittest.main()
