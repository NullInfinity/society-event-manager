#!/usr/bin/env python3
import unittest
from datetime import date
from unittest.mock import MagicMock, patch, call
from MemberDatabase import MemberDatabase

@patch('MemberDatabase.sqlite3.connect')
class MemberDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.firstName = 'Ted'
        self.lastName = 'Bobson'
        self.memberId = '00000000'

    def test_db_connect(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mocksql_connect.assert_called_with('test.db')

    def test_optional_commit_on(self, mocksql_connect):
        mdb = MemberDatabase('test.db', safe = True)
        mdb.optional_commit()
        self.assertTrue(mocksql_connect().commit.called)

    def test_optional_commit_off(self, mocksql_connect):
        mdb = MemberDatabase('test.db', safe = False)
        mdb.optional_commit()
        self.assertFalse(mocksql_connect().commit.called)

    def test_get_member_noBarcode(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()

        self.assertIsNone(mdb.get_member(None))
        self.assertFalse(mocksql_connect().cursor().execute.called)
        self.assertFalse(mocksql_connect().cursor().fetchall.called)
        self.assertFalse(mdb.optional_commit.called)

    def test_get_member_noBarcode_noUpdateTimestamp(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()

        self.assertIsNone(mdb.get_member(None, updateTimestamp = False))
        self.assertFalse(mocksql_connect().cursor().execute.called)
        self.assertFalse(mocksql_connect().cursor().fetchall.called)
        self.assertFalse(mdb.optional_commit.called)

    def test_get_member_noBarcode_autoFix(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()

        self.assertIsNone(mdb.get_member(None, autoFix = True))
        self.assertFalse(mocksql_connect().cursor().execute.called)
        self.assertFalse(mocksql_connect().cursor().fetchall.called)
        self.assertFalse(mdb.optional_commit.called)

    def test_get_member_barcodeOnly_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(mdb.get_member(self.memberId))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(mdb.optional_commit.called)

    def test_get_member_barcodeAndNames_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(mdb.get_member(self.memberId, firstName=self.firstName, lastName=self.lastName))
        mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName))])
        self.assertEqual(2, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(mdb.optional_commit.called)

    def test_get_member_namesOnly_notPresent(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(mdb.get_member(memberId = None, firstName=self.firstName, lastName=self.lastName))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(mdb.optional_commit.called)

    def test_get_member_barcodeOnly_present_unique_noUpdateTimestamp(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, updateTimestamp = False))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(mdb.optional_commit.called)

    @patch('MemberDatabase.date')
    def test_get_member_barcodeOnly_present_unique_updateTimestamp(self, mock_date, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mock_date.today.return_value = date.min
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId))
        mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('UPDATE users SET last_attended=? WHERE barcode=?', (date.min, self.memberId))])
        self.assertEqual(2, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(mdb.optional_commit.called)

    def test_get_member_barcodeOnly_present_unique_noUpdateTimestamp_autoFix(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, updateTimestamp=False, autoFix=True))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(mdb.optional_commit.called)

    def test_get_member_barcodeAndNames_present_unique_noUpdateTimestamp(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, firstName=self.firstName, lastName=self.lastName, updateTimestamp=False, autoFix=False))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(mdb.optional_commit.called)

    def test_get_member_barcodeAndNames_present_unique_noUpdateTimestamp_autoFix(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]

        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, firstName=self.firstName, lastName=self.lastName, updateTimestamp=False, autoFix=True))
        mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('UPDATE users SET firstName=?, lastName=? WHERE barcode=?', (self.firstName, self.lastName, self.memberId))])
        self.assertEqual(2, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(mdb.optional_commit.called)

    def test_get_member_namesOnly_present_unique_noUpdateTimestamp_autoFix(self, mocksql_connect):
        mdb = MemberDatabase('test.db')
        mdb.optional_commit = MagicMock()
        mocksql_connect().cursor().fetchall.return_value = (self.firstName, self.lastName)

        self.assertEqual((self.firstName, self.lastName), mdb.get_member(None, firstName=self.firstName, lastName=self.lastName, updateTimestamp=False, autoFix=True))
        mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName,))
        self.assertEqual(1, mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, mocksql_connect().cursor().fetchall.call_count)

if __name__ == '__main__':
    unittest.main()
