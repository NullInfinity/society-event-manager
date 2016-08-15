#!/usr/bin/env python3
import unittest
from unittest.mock import patch, call
from MemberDatabase import MemberDatabase

@patch('sqlite3.connect')
class MemberDatabaseTestCase(unittest.TestCase):

    def test_dbConnect(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mocksql_connect.assert_called_with('test.db')

    def test_optionalCommitOn(self, mocksql_connect):
        mdb = MemberDatabase('test.db', safe = True)
        mdb.optionalCommit()
        self.assertTrue(mocksql_connect().commit.called)

    def test_optionalCommitOff(self, mocksql_connect):
        mdb = MemberDatabase('test.db', safe = False)
        mdb.optionalCommit()
        self.assertFalse(mocksql_connect().commit.called)

    def test_getMember_barcodeOnly_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember('00000000'))

        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', ('00000000',))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        #TODO assert that optionalCommit was not called

    def test_getMember_barcodeAndNames_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember('00000000', firstName='Ted', lastName='Bobson'))

        mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', ('00000000',)), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', ('Ted', 'Bobson'))])
        self.assertEqual(2, mocksql_connect().cursor().execute.call_count)
        #TODO assert that optionalCommit was not called

if __name__ == '__main__':
    unittest.main()
