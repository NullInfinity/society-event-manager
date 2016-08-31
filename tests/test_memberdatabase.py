"""
test_MemberDatabase.py contains the automated tests for socman.MemberDatabase.

Tests on socman should be run with `python -m pytest`. To run just these tests,
run `pytest tests/test_MemberDatabase.py`.


The MIT License (MIT)

Copyright (c) 2016 Alexander Thorne

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import unittest
import unittest.mock
import pytest

import socman


@unittest.mock.patch('socman.sqlite3.connect')
def test_db_connect(mocksql_connect):
    """Test MemberDatabase.__init__ calls sqlite3.connect."""
    socman.MemberDatabase('test.db', safe=True)
    mocksql_connect.assert_called_with('test.db')


@unittest.mock.patch('socman.sqlite3.connect')
def test_optional_commit_on(mocksql_connect):
    """Test MemberDatabase.optional_commit commits to DB when safe=True."""
    mdb = socman.MemberDatabase('test.db', safe=True)
    mdb.optional_commit()
    assert mocksql_connect().commit.called


@unittest.mock.patch('socman.sqlite3.connect')
def test_optional_commit_off(mocksql_connect):
    """Test MemberDatabase.optional_commit does not commit to DB when safe=False."""
    mdb = socman.MemberDatabase('test.db', safe=False)
    mdb.optional_commit()
    assert not mocksql_connect().commit.called


class MemberDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.first_name = 'Ted'
        self.last_name = 'Bobson'
        self.barcode = '00000000'
        self.college = 'Wolfson'
        self.member = socman.Member(self.barcode, socman.Name(self.first_name, self.last_name), college = self.college)
        self.member_nobarcode = socman.Member(None, socman.Name(self.first_name, self.last_name), college = self.college)

        self.mocksql_connect_patcher = unittest.mock.patch('socman.sqlite3.connect')
        self.mocksql_connect = self.mocksql_connect_patcher.start()
        self.addCleanup(self.mocksql_connect_patcher.stop)

        self.mdb = socman.MemberDatabase('test.db', safe=True)


    def test_get_member_no_barcode_no_name_update_timestamp(self):
        with self.assertRaises(socman.BadMemberError):
            self.mdb.get_member(member=socman.Member(None))
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_no_barcode_no_name(self):
        with self.assertRaises(socman.BadMemberError):
            self.mdb.get_member(member=socman.Member(None), update_timestamp=False)
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_no_barcode_no_name_update_timestamp_autofix(self):
        with self.assertRaises(socman.BadMemberError):
            self.mdb.get_member(member=socman.Member(None), autofix=True)
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_no_barcode_no_name_autofix(self):
        with self.assertRaises(socman.BadMemberError):
            self.mdb.get_member(member=socman.Member(None), update_timestamp=False, autofix=True)
        self.assertFalse(self.mocksql_connect().cursor().execute.called)
        self.assertFalse(self.mocksql_connect().cursor().fetchall.called)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_not_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        with self.assertRaises(socman.MemberNotFoundError):
            self.mdb.get_member(member=socman.Member(self.barcode))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_name_not_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        with self.assertRaises(socman.MemberNotFoundError):
            self.mdb.get_member(member=self.member)
        self.mocksql_connect().cursor().execute.assert_has_calls([unittest.mock.call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,)), unittest.mock.call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name))])
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_name_not_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = []

        with self.assertRaises(socman.MemberNotFoundError):
            self.mdb.get_member(member=self.member_nobarcode)
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertFalse(self.mocksql_connect().commit.called)

    def test_get_member_barcode_present_unique(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=socman.Member(self.barcode), update_timestamp = False))
        self.mocksql_connect().cursor().execute.assert_called_once_with('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,))
        self.assertEqual(1, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    @unittest.mock.patch('socman.date')
    def test_get_member_barcode_present_unique_update_timestamp(self, mock_date):
        mock_date.today.return_value = datetime.date.min
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=socman.Member(self.barcode)))
        self.mocksql_connect().cursor().execute.assert_has_calls([unittest.mock.call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,)), unittest.mock.call('UPDATE users SET last_attended=? WHERE barcode=?', (datetime.date.min, self.barcode))])
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(1, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_get_member_barcode_present_unique_autofix(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=socman.Member(self.barcode), update_timestamp=False, autofix=True))
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
        self.mocksql_connect().cursor().execute.assert_has_calls([unittest.mock.call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode,)), unittest.mock.call('UPDATE users SET firstName=?,lastName=? WHERE barcode=?', (self.first_name, self.last_name, self.barcode))])
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
        self.mocksql_connect().cursor().execute.assert_has_calls([unittest.mock.call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode, )), unittest.mock.call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,))])
        self.assertEqual(2, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)

    @unittest.mock.patch('socman.date')
    def test_get_member_name_unique_present_barcode_update_timestamp(self, mock_date):
        self.mocksql_connect().cursor().fetchall.side_effect = [[], [(self.first_name, self.last_name)]]
        mock_date.today.return_value = datetime.date.min

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member, update_timestamp=True))
        self.mocksql_connect().cursor().execute.assert_has_calls([unittest.mock.call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode, )), unittest.mock.call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,)), unittest.mock.call('UPDATE users SET last_attended=? WHERE firstName=? AND lastName=?', (datetime.date.min, self.first_name, self.last_name))])
        self.assertEqual(3, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)

    def test_get_member_name_unique_present_barcode_autofix(self):
        self.mocksql_connect().cursor().fetchall.side_effect = [[], [(self.first_name, self.last_name)]]

        self.assertEqual((self.first_name, self.last_name), self.mdb.get_member(member=self.member, update_timestamp=False, autofix=True))
        self.mocksql_connect().cursor().execute.assert_has_calls([unittest.mock.call('SELECT firstName,lastName FROM users WHERE barcode=?', (self.barcode, )), unittest.mock.call('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (self.first_name, self.last_name,)), unittest.mock.call('UPDATE users SET barcode=? WHERE firstName=? AND lastName=?', (self.barcode, self.first_name, self.last_name))])
        self.assertEqual(3, self.mocksql_connect().cursor().execute.call_count)
        self.assertEqual(2, self.mocksql_connect().cursor().fetchall.call_count)
        self.assertTrue(self.mocksql_connect().commit.called)

    def test_add_member_none(self):
        with self.assertRaises(socman.BadMemberError):
            self.mdb.add_member(member=socman.Member(None))

    def test_add_member_present(self):
        self.mocksql_connect().cursor().fetchall.return_value = [(self.first_name, self.last_name)]
        self.mdb.add_member(self.member)
        self.assertEqual(3, self.mocksql_connect().cursor().execute.call_count)

    def test_add_member_present_by_name(self):
        self.mocksql_connect().cursor().fetchall.side_effect = [[], (self.first_name, self.last_name)]
        self.mdb.add_member(self.member)
        self.assertEqual(4, self.mocksql_connect().cursor().execute.call_count)

    @unittest.mock.patch('socman.datetime')
    @unittest.mock.patch('socman.date')
    def test_add_member_new(self, mock_date, mock_datetime):
        self.mocksql_connect().cursor().fetchall.side_effect = [[], [], [(self.first_name, self.last_name)]]
        mock_date.today.return_value = datetime.date.min
        mock_datetime.utcnow.return_value = datetime.datetime.min

        self.mdb.add_member(self.member)
        self.mocksql_connect().cursor().execute.assert_called_with('INSERT INTO users (barcode, firstName, lastName, college, datejoined, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (self.barcode, self.first_name, self.last_name, self.college, datetime.date.min, datetime.datetime.min, datetime.datetime.min))
        self.assertEqual(3, self.mocksql_connect().cursor().execute.call_count)

if __name__ == '__main__':
    unittest.main()
