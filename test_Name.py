#!/usr/bin/env python3
import unittest
from MemberDatabase import Name

class MemberTestCase(unittest.TestCase):

    def setUp(self):
        self.first_name = 'Ted'
        self.middle_name = 'Rogers'
        self.last_name = 'Bobson'

    def test_empty_name(self):
        name = Name()

        self.assertEqual('', name.first())
        self.assertEqual('', name.last())
        self.assertEqual('', name.full())
        self.assertFalse(name)

    def test_single_name(self):
        name = Name(self.last_name)

        self.assertEqual('', name.first())
        self.assertEqual(self.last_name, name.last())
        self.assertEqual(self.last_name, name.full())
        self.assertTrue(name)

    def test_two_name(self):
        name = Name(self.first_name, self.last_name)

        self.assertEqual(self.first_name, name.first())
        self.assertEqual(self.last_name, name.last())
        self.assertEqual(self.first_name + ' ' + self.last_name, name.full())
        self.assertTrue(name)

    def test_multiple_name(self):
        name = Name(self.first_name, self.middle_name, self.last_name)

        self.assertEqual(self.first_name + ' ' + self.middle_name, name.first())
        self.assertEqual(self.last_name, name.last())
        self.assertEqual(self.first_name + ' ' + self.middle_name + ' ' + self.last_name, name.full())
        self.assertTrue(name)

if __name__ == '__main__':
    unittest.main()
