#!/usr/bin/env python3
import unittest
from datetime import date
from unittest.mock import patch, call
from membership import Name, Member, MemberDatabase

class MemberDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.first_name = 'Ted'
        self.last_name = 'Bobson'
        self.barcode = '00000000'

        self.mocksql_connect_patcher = patch('membership.sqlite3.connect')
        self.mocksql_connect = self.mocksql_connect_patcher.start()
        self.addCleanup(self.mocksql_connect_patcher.stop)

        self.mdb = MemberDatabase('test.db')

    def test_db_connect(self):
        self.mocksql_connect.assert_called_with('test.db')

    def test_optional_commit_on(self):
        mdb = MemberDatabase('test.db', safe = True)
        mdb.optional_commit()
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_optional_commit_off(self):
        mdb = MemberDatabase('test.db', safe = False)
        mdb.optional_commit()
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_sql_build_name_value_pairs(self):
        self.assertEqual((None,None), self.mdb.sql_build_name_value_pairs(Member(None), sep=' AND '))
        self.assertEqual(('lastName=?', (self.last_name, )), self.mdb.sql_build_name_value_pairs(Member(self.barcode, self.last_name), sep=' AND '))
        self.assertEqual(('firstName=? AND lastName=?', (self.first_name, self.last_name)), self.mdb.sql_build_name_value_pairs(Member(self.barcode, self.first_name, self.last_name), sep=' AND '))
        self.assertEqual(('firstName=?,lastName=?', (self.first_name, self.last_name)), self.mdb.sql_build_name_value_pairs(Member(self.barcode, self.first_name, self.last_name), sep=','))

    def test_sql_search_barcode_phrase(self):
        self.assertEqual((None, None), self.mdb.sql_search_barcode_phrase(Member(None)))
        self.assertEqual(('barcode=?', (self.barcode,)), self.mdb.sql_search_barcode_phrase(Member(self.barcode)))
        self.assertEqual(('barcode=?', (self.barcode,)), self.mdb.sql_search_barcode_phrase(Member(self.barcode, self.first_name, self.last_name)))

    def test_sql_search_name_phrase(self):
        self.assertEqual((None, None), self.mdb.sql_search_name_phrase(Member(None)))
        self.assertEqual(('lastName=?', (self.last_name, )), self.mdb.sql_search_name_phrase(Member(None, self.last_name)))
        self.assertEqual(('firstName=? AND lastName=?', (self.first_name, self.last_name)), self.mdb.sql_search_name_phrase(Member(None, self.first_name, self.last_name)))

    def test_sql_search_phrase_barcode(self):
        self.assertEqual(('barcode=?', (self.barcode,)), self.mdb.sql_search_phrase(Member(self.barcode)))
        self.assertEqual(('barcode=?', (self.barcode,)), self.mdb.sql_search_phrase(Member(self.barcode, self.first_name, self.last_name)))

    def test_sql_search_phrase_nobarcode(self):
        self.assertEqual((None, None), self.mdb.sql_search_phrase(Member(None)))
        self.assertEqual(('lastName=?', (self.last_name, )), self.mdb.sql_search_phrase(Member(None, self.last_name)))
        self.assertEqual(('firstName=? AND lastName=?', (self.first_name, self.last_name)), self.mdb.sql_search_phrase(Member(None, self.first_name, self.last_name)))

    def test_sql_update_barcode_phrase(self):
        self.assertEqual((None, None), self.mdb.sql_update_barcode_phrase(Member(None)))
        self.assertEqual((None, None), self.mdb.sql_update_barcode_phrase(Member(None, self.last_name)))
        self.assertEqual(('barcode=?', (self.barcode, )), self.mdb.sql_update_barcode_phrase(Member(self.barcode)))
        self.assertEqual(('barcode=?', (self.barcode, )), self.mdb.sql_update_barcode_phrase(Member(self.barcode, self.first_name, self.last_name)))

    def test_sql_update_name_phrase(self):
        self.assertEqual((None, None), self.mdb.sql_update_name_phrase(Member(self.barcode)))
        self.assertEqual(('lastName=?', (self.last_name, )), self.mdb.sql_update_name_phrase(Member(self.barcode, self.last_name)))
        self.assertEqual(('firstName=?,lastName=?', (self.first_name, self.last_name)), self.mdb.sql_update_name_phrase(Member(self.barcode, self.first_name, self.last_name)))

    def test_sql_search_query(self):
        self.assertEqual((None, None), self.mdb.sql_search_query(Member(None)))
        self.assertEqual(('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode, )), self.mdb.sql_search_query(Member(self.barcode)))

    def test_sql_update_barcode_query(self):
        self.assertEqual((None, None), self.mdb.sql_update_barcode_query(Member(None)))
        self.assertEqual(('UPDATE users SET barcode=? WHERE firstName=? AND lastName=?', (self.barcode, self.first_name, self.last_name)), self.mdb.sql_update_barcode_query(Member(self.barcode, self.first_name, self.last_name)))

    def test_sql_update_name_query(self):
        self.assertEqual((None, None), self.mdb.sql_update_name_query(Member(None)))
        self.assertEqual((None, None), self.mdb.sql_update_name_query(Member(None)))
        self.assertEqual(('UPDATE users SET firstName=?,lastName=? WHERE barcode=?', (self.first_name, self.last_name, self.barcode)), self.mdb.sql_update_name_query(Member(self.barcode, self.first_name, self.last_name)))

    @patch('membership.date')
    def test_update_last_attended_query(self, mock_date):
        mock_date.today.return_value = date.min

        self.assertEqual((None, None), self.mdb.sql_update_last_attended_query(Member(None)))
        self.assertEqual(('UPDATE users SET last_attended=? WHERE barcode=?', (date.min, self.barcode)), self.mdb.sql_update_last_attended_query(Member(self.barcode)))
        self.assertEqual(('UPDATE users SET last_attended=? WHERE firstName=? AND lastName=?', (date.min, self.first_name, self.last_name)), self.mdb.sql_update_last_attended_query(Member(None, self.first_name, self.last_name)))

#
#    def test_get_member_no_barcode(self):
#
#        self.assertIsNone(mdb.get_member(None))
#        self.assertFalse(self.mocksql_connect().cursor().execute.called)
#        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
#        self.assertFalse(mdb.optional_commit.called)
#
#    def test_get_member_no_barcode_no_update_timestamp(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#
#        self.assertIsNone(mdb.get_member(None, updateTimestamp = False))
#        self.assertFalse(self.mocksql_connect().cursor().execute.called)
#        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
#        self.assertFalse(mdb.optional_commit.called)
#
#    def test_get_member_no_barcode_autofix(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#
#        self.assertIsNone(mdb.get_member(None, autoFix = True))
#        self.assertFalse(self.mocksql_connect().cursor().execute.called)
#        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
#        self.assertFalse(mdb.optional_commit.called)
#
#    def test_get_member_barcodeOnly_notPresent(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = []
#
#        self.assertIsNone(mdb.get_member(self.memberId))
#        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
#        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertFalse(mdb.optional_commit.called)
#
#    def test_get_member_barcodeAndNames_notPresent(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = []
#
#        self.assertIsNone(mdb.get_member(self.memberId, firstName=self.firstName, lastName=self.lastName))
#        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName))])
#        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertFalse(mdb.optional_commit.called)
#
#    def test_get_member_namesOnly_notPresent(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = []
#
#        self.assertIsNone(mdb.get_member(memberId = None, firstName=self.firstName, lastName=self.lastName))
#        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName))
#        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertFalse(mdb.optional_commit.called)
#
#    def test_get_member_barcodeOnly_present_unique_noUpdateTimestamp(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]
#
#        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, updateTimestamp = False))
#        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
#        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertTrue(mdb.optional_commit.called)
#
#    @patch('membership.date')
#    def test_get_member_barcodeOnly_present_unique_updateTimestamp(self, mock_date):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        mock_date.today.return_value = date.min
#        self.mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]
#
#        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId))
#        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('UPDATE users SET last_attended=? WHERE barcode=?', (date.min, self.memberId))])
#        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertTrue(mdb.optional_commit.called)
#
#    def test_get_member_barcodeOnly_present_unique_noUpdateTimestamp_autoFix(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]
#
#        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, updateTimestamp=False, autoFix=True))
#        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
#        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertTrue(mdb.optional_commit.called)
#
#    def test_get_member_barcodeAndNames_present_unique_noUpdateTimestamp(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]
#
#        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, firstName=self.firstName, lastName=self.lastName, updateTimestamp=False, autoFix=False))
#        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,))
#        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertTrue(mdb.optional_commit.called)
#
#    def test_get_member_barcodeAndNames_present_unique_noUpdateTimestamp_autoFix(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = [(self.firstName, self.lastName)]
#
#        self.assertEqual((self.firstName, self.lastName), mdb.get_member(self.memberId, firstName=self.firstName, lastName=self.lastName, updateTimestamp=False, autoFix=True))
#        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.memberId,)), call('UPDATE users SET firstName=?, lastName=? WHERE barcode=?', (self.firstName, self.lastName, self.memberId))])
#        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
#        self.assertTrue(mdb.optional_commit.called)
#
#    def test_get_member_namesOnly_present_unique_noUpdateTimestamp_autoFix(self):
#        mdb = MemberDatabase('test.db')
#        mdb.optional_commit = MagicMock()
#        self.mocksql_connect().cursor().fetchall.return_value = (self.firstName, self.lastName)
#
#        self.assertEqual((self.firstName, self.lastName), mdb.get_member(None, firstName=self.firstName, lastName=self.lastName, updateTimestamp=False, autoFix=True))
#        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.firstName, self.lastName,))
#        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
#        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)

if __name__ == '__main__':
    unittest.main()
