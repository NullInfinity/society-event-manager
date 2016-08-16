#!/usr/bin/env python3
import unittest
import datetime
from datetime import date
from unittest.mock import MagicMock, patch, call
from MemberDatabase import MemberDatabase

@patch('sqlite3.connect')
class MemberDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.firstName = 'Ted'
        self.lastName = 'Bobson'
        self.memberId = '00000000'

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

    def test_getMember_noBarcode(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember(None))
        self.assertFalse(mocksql_connect().cursor().execute.called)
        self.assertFalse(mdb.optionalCommit.called)

    def test_getMember_noBarcode_noUpdateTimestamp(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember(None, updateTimestamp = False))
        self.assertFalse(mocksql_connect().cursor().execute.called)
        self.assertFalse(mdb.optionalCommit.called)

    def test_getMember_noBarcode_autoFix(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember(None, autoFix = True))
        self.assertFalse(mocksql_connect().cursor().execute.called)
        self.assertFalse(mdb.optionalCommit.called)

    def test_getMember_barcodeOnly_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember(self.memberId))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertFalse(mdb.optionalCommit.called)

    def test_getMember_barcodeAndNames_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember(self.memberId, firstName=self.firstName, lastName=self.lastName))
        mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName))])
        self.assertEqual(2, mocksql_connect().cursor().execute.call_count)
        self.assertFalse(mdb.optionalCommit.called)

    def test_getMember_namesOnly_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = None

        self.assertIsNone(mdb.getMember(memberId = None, firstName=self.firstName, lastName=self.lastName))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertFalse(mdb.optionalCommit.called)

    def test_getMember_barcodeOnly_present_unique_noUpdateTimestamp(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.getMember(self.memberId, updateTimestamp = False))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertTrue(mdb.optionalCommit.called)

    @patch('datetime.date')
    def test_getMember_barcodeOnly_present_unique_updateTimestamp(self, mock_date, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mock_date.today.return_value = date.min
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.getMember(self.memberId))
        mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('UPDATE users SET last_attended=? WHERE barcode=?', (date.min, self.memberId))])
        self.assertEqual(2, mocksql_connect().cursor().execute.call_count)
        self.assertTrue(mdb.optionalCommit.called)

    def test_getMember_barcodeOnly_present_unique_noUpdateTimestamp_autoFix_notNeeded(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.getMember(self.memberId, updateTimestamp=False, autoFix=True))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertTrue(mdb.optionalCommit.called)

    def test_getMember_barcodeAndNames_present_unique_noUpdateTimestamp_autoFix_needed(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optionalCommit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.getMember(self.memberId, firstName=self.firstName, lastName=self.lastName, updateTimestamp=False, autoFix=True))
        mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('UPDATE users SET firstName=?, lastName=? WHERE barcode=?', (self.firstName, self.lastName, self.memberId))])
        self.assertEqual(2, mocksql_connect().cursor().execute.call_count)
        self.assertTrue(mdb.optionalCommit.called)

if __name__ == '__main__':
    unittest.main()
