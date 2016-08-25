#!/usr/bin/env python3
import unittest
from datetime import date, datetime
from unittest.mock import patch, call
from socman import Member
from socman import MemberDatabase
from socman import Name


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
        self.assertNotEqual(self.name, 4)
        self.assertNotEqual(self.short_name, 'test')

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
        self.assertNotEqual(Member(self.barcode, name=self.name), 4)
        self.assertNotEqual(Member(self.barcode, name=self.name, college=self.college), 'test')
        self.assertNotEqual(Member(self.barcode, name=self.name, college=self.college), Name('test'))

    def test_varargs_init(self):
        self.assertEqual(Member(None, name=self.name), Member(None, self.name.first(), self.name.last()))
        self.assertEqual(Member(self.barcode, name=Name('Ted', 'Bobson', 'Jones')), Member(self.barcode, 'Ted', 'Bobson', 'Jones'))
        self.assertEqual(Member(self.barcode, name=self.name), Member(self.barcode, 'Billy', name=self.name))

class MemberDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.first_name = 'Ted'
        self.last_name = 'Bobson'
        self.barcode = '00000000'
        self.college = 'Wolfson'
        self.member = Member(self.barcode, self.first_name, self.last_name, college = self.college)
        self.member_nobarcode = Member(None, self.first_name, self.last_name, college = self.college)

        self.mocksql_connect_patcher = patch('socman.sqlite3.connect')
        self.mocksql_connect = self.mocksql_connect_patcher.start()
        self.addCleanup(self.mocksql_connect_patcher.stop)

        self.mdb = MemberDatabase('test.db', safe=True)

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

    @patch('socman.date')
    def test_update_last_attended_query(self, mock_date):
        mock_date.today.return_value = date.min

        self.assertEqual((None, None), self.mdb.sql_update_last_attended_query(Member(None)))
        self.assertEqual(('UPDATE users SET last_attended=? WHERE barcode=?', (date.min, self.barcode)), self.mdb.sql_update_last_attended_query(Member(self.barcode)))
        self.assertEqual(('UPDATE users SET last_attended=? WHERE firstName=? AND lastName=?', (date.min, self.first_name, self.last_name)), self.mdb.sql_update_last_attended_query(Member(None, self.first_name, self.last_name)))

    def test_get_member_no_barcode_no_name_update_timestamp(self):

        self.assertIsNone(self.mdb.get_member(None))
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_no_barcode_no_name(self):
        self.assertIsNone(self.mdb.get_member(None, update_timestamp = False))
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_no_barcode_no_name_update_timestamp_autofix(self):
        self.assertIsNone(self.mdb.get_member(None, autofix = True))
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_no_barcode_no_name_autofix(self):
        self.assertIsNone(self.mdb.get_member(None, update_timestamp=False, autofix = True))
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_not_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(self.mdb.get_member(self.barcode))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_via_member(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(self.mdb.get_member(member=Member(self.barcode)))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_via_member_priority(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(self.mdb.get_member(barcode=self.barcode, member=Member('11111111')))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', ('11111111',))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_name_not_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(self.mdb.get_member(member=self.member))
        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,)), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name))])
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_name_not_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        self.assertIsNone(self.mdb.get_member(member=self.member_nobarcode))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_present_unique(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(self.barcode, update_timestamp = False))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    @patch('socman.date')
    def test_get_member_barcode_present_unique_update_timestamp(self, mock_date):
        mock_date.today.return_value = date.min
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(self.barcode))
        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,)), call('UPDATE users SET last_attended=? WHERE barcode=?', (date.min, self.barcode))])
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_get_member_barcode_present_unique_autofix(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(self.barcode, update_timestamp=False, autofix=True))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_get_member_barcode_present_unique_name(self):
        self.mocksql_connect().cursor().fetchall.side_effect = [[(self.first_name, self.last_name)], []]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member, update_timestamp=False, autofix=False))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_get_member_barcode_present_unique_name_autofix(self):
        self.mocksql_connect().cursor().fetchall.side_effect = [[(self.first_name, self.last_name)], []]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member, update_timestamp=False, autofix=True))
        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,)), call('UPDATE users SET firstName=?,lastName=? WHERE barcode=?', (self.first_name, self.last_name, self.barcode))])
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_get_member_name_present_unique(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member_nobarcode, update_timestamp=False, autofix=False))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)

    def test_get_member_name_present_unique_autofix(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member_nobarcode, update_timestamp=False, autofix=True))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)

    def test_get_member_name_unique_present_barcode(self):
        self.mocksql_connect().cursor().fetchall.side_effect = [[], [(self.first_name, self.last_name)]]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member, update_timestamp=False))
        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode, )), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,))])
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)

    @patch('socman.date')
    def test_get_member_name_unique_present_barcode_update_timestamp(self, mock_date):
        self.mocksql_connect().cursor().fetchall.side_effect = [[], [(self.first_name, self.last_name)]]
        mock_date.today.return_value = date.min

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member, update_timestamp=True))
        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode, )), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,)), call('UPDATE users SET last_attended=? WHERE firstName=? AND lastName=?', (date.min, self.first_name, self.last_name))])
        self.assertEqual(3, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)

    def test_get_member_name_unique_present_barcode_autofix(self):
        self.mocksql_connect().cursor().fetchall.side_effect = [[], [(self.first_name, self.last_name)]]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member, update_timestamp=False, autofix=True))
        self.mocksql_connect().cursor().execute.assert_has_calls([call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode, )), call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,)), call('UPDATE users SET barcode=? WHERE firstName=? AND lastName=?', (self.barcode, self.first_name, self.last_name))])
        self.assertEqual(3, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_add_member_none(self):
        self.assertFalse(self.mdb.add_member(None))

    def test_add_member_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]
        self.assertFalse(self.mdb.add_member(self.member))
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)

    @patch('socman.datetime')
    @patch('socman.date')
    def test_add_member_new(self, mock_date, mock_datetime):
        self.mocksql_connect().cursor().fetchall.return_value = []
        mock_date.today.return_value = date.min
        mock_datetime.utcnow.return_value = datetime.min

        self.assertTrue(self.mdb.add_member(self.member))
        self.mocksql_connect().cursor().execute.assert_called_with('INSERT INTO users (barcode, firstName, lastName, college, datejoined, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (self.barcode, self.first_name, self.last_name, self.college, date.min, datetime.min, datetime.min))
        self.assertEqual(3, self.mocksql_connect().cursor().execute.call_count)

if __name__ == '__main__':
    unittest.main()