#!/usr/bin/env python3
import unittest
from membership import Name

class NameTestCase(unittest.TestCase):

    def setUp(self):
        self.first_name = 'Ted'
        self.middle_name = 'Rogers'
        self.last_name = 'Bobson'
        self.empty_name = Name()
        self.short_name = Name(self.last_name)
        self.name = Name(self.first_name, self.last_name)
        self.long_name = Name(self.first_name, self.middle_name, self.last_name)

    def test_falsiness(self):
        self.assertFalse(self.empty_name)
        self.assertTrue(self.short_name)
        self.assertTrue(self.name)
        self.assertTrue(self.long_name)

    def test_first(self):
        self.assertEqual('', self.empty_name.first())
        self.assertEqual('', self.short_name.first())
        self.assertEqual(self.first_name, self.name.first())
        self.assertEqual(self.first_name + ' ' + self.middle_name, self.long_name.first())

    def test_last(self):
        self.assertEqual('', self.empty_name.last())
        self.assertEqual(self.last_name, self.short_name.last())
        self.assertEqual(self.last_name, self.name.last())
        self.assertEqual(self.last_name, self.long_name.last())

    def test_full(self):
        self.assertEqual('', self.empty_name.full())
        self.assertEqual(self.last_name, self.short_name.full())
        self.assertEqual(self.first_name + ' ' + self.last_name, self.name.full())
        self.assertEqual(self.first_name + ' ' + self.middle_name + ' ' + self.last_name, self.long_name.full())

    def test_equality(self):
        self.assertEqual(self.empty_name, Name())
        self.assertEqual(self.short_name, Name(self.last_name))
        self.assertEqual(self.name, Name(self.first_name, self.last_name))
        self.assertEqual(self.long_name, Name(self.first_name, self.middle_name, self.last_name))

    def test_inequality(self):
        self.assertNotEqual(self.empty_name, self.short_name)
        self.assertNotEqual(self.empty_name, self.name)
        self.assertNotEqual(self.empty_name, self.long_name)
        self.assertNotEqual(self.short_name, self.name)
        self.assertNotEqual(self.short_name, self.long_name)
        self.assertNotEqual(self.name, self.long_name)

if __name__ == '__main__':
    unittest.main()
