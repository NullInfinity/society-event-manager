"""
test_memberdatabase.py contains the automated tests for socman.MemberDatabase.

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
# pylint: disable=redefined-outer-name
import collections
import datetime
import unittest
import unittest.mock
import pytest

import socman


@pytest.fixture
def mocks():
    """Return fixture for mocked sqlite3.connect and datetime functions."""
    sql_connect_patcher = unittest.mock.patch('socman.sqlite3.connect')

    date_patcher = unittest.mock.patch('socman.date')
    date_mock = date_patcher.start()
    date_mock.today.return_value = datetime.date.min

    datetime_patcher = unittest.mock.patch('socman.datetime')
    datetime_mock = datetime_patcher.start()
    datetime_mock.utcnow.return_value = datetime.datetime.min

    # note that date and datetime mocks are never used
    # they are simply created so the values of date.min and datetime.utcnow
    # can be controlled
    yield collections.namedtuple('mock_type', 'sql_connect date datetime')(
        sql_connect_patcher.start(), date_mock, datetime_mock)

    sql_connect_patcher.stop()
    datetime_patcher.stop()
    date_patcher.stop()


@pytest.fixture
def mdb(mocks):
    """Return fixture for MemberDatabase, with mocks included.

    Returns MemberDatabase object, with added reference to mocked
    sqlite3.connect, mdb.mocksql_connect.
    """
    mdb_fixture = socman.MemberDatabase('test.db', safe=True)
    mdb_fixture.mocksql_connect = mocks.sql_connect
    yield mdb_fixture


def test_db_connect(mdb):
    """Test MemberDatabase.__init__ calls sqlite3.connect."""
    mdb.mocksql_connect.assert_called_with('test.db')


def test_optional_commit_on(mocks):
    """Test MemberDatabase.optional_commit commits when safe=True.

    Checks that sqlite3.connect().cursor().commit() is called.
    """
    mdb = socman.MemberDatabase('test.db', safe=True)
    mdb.optional_commit()
    assert mocks.sql_connect().commit.called


def test_optional_commit_off(mocks):
    """Test MemberDatabase.optional_commit does not commit when safe=False.

    Checks that sqlite3.connect().cursor().commit() is not called.
    """
    mdb = socman.MemberDatabase('test.db', safe=False)
    mdb.optional_commit()
    assert not mocks.sql_connect().commit.called


@pytest.mark.parametrize("member", [
    None,
    socman.Member(None),
    socman.Member(None, name=None, college=None)
    ])
@pytest.mark.parametrize("autofix", [True, False])
@pytest.mark.parametrize("update_timestamp", [True, False])
def test_get_member_bad_member(mdb, member, autofix, update_timestamp):
    """Test get_member when given a bad (i.e. None) member object."""
    mdb.mocksql_connect().cursor().fetchall.side_effect = [[], []]

    with pytest.raises(socman.BadMemberError):
        mdb.get_member(member=member,
                       autofix=autofix, update_timestamp=update_timestamp)
    assert mdb.mocksql_connect().cursor().execute.call_count == 0
    assert mdb.mocksql_connect().cursor().fetchall.call_count == 0
    assert mdb.mocksql_connect().commit.call_count == 0


@pytest.mark.parametrize("member,calls", [
    (   # member with name and barcode
        # not present in DB under barcode or name
        socman.Member(barcode='00000000',
                      name=socman.Name('Ted', 'Bobson'),
                      college='Wolfson'),
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 2,
                'commit': 0
                },
            }
        ),

    (   # member with barcode only
        # not present in DB
        socman.Member(barcode='00000000',
                      name=None,
                      college='Wolfson'),
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                ],
            'count': {
                'execute': 1,
                'fetchall': 1,
                'commit': 0
                },
            }
        ),

    (   # member with name only
        # not present in DB
        socman.Member(barcode=None,
                      name=socman.Name('Ted', 'Bobson'),
                      college='Wolfson'),
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 1,
                'fetchall': 1,
                'commit': 0
                },
            }
        ),
    ])
@pytest.mark.parametrize("autofix", [True, False])
@pytest.mark.parametrize("update_timestamp", [True, False])
def test_get_member_not_present(mdb, member, autofix, update_timestamp, calls):
    """Test get_member against non None Members which are not present in DB."""
    mdb.mocksql_connect().cursor().fetchall.side_effect = [[], []]

    with pytest.raises(socman.MemberNotFoundError):
        mdb.get_member(member=member,
                       autofix=autofix, update_timestamp=update_timestamp)

        mdb.mocksql_connect().cursor().execute.assert_has_calls(calls['values'])
    assert (calls['count']['execute'] ==
            mdb.mocksql_connect().cursor().execute.call_count)
    assert (calls['count']['fetchall'] ==
            mdb.mocksql_connect().cursor().fetchall.call_count)
    assert (calls['count']['commit'] ==
            mdb.mocksql_connect().commit.call_count)


# suffix on each comment description will contain either AF, TS, both or none
#   AF = autofix enabled
#   TS = update_timestamp enabled
@pytest.mark.parametrize("args,mock_returns,calls", [
    (   # member with barcode only
        # present (and unique) in DB under barcode
        {
            'member': socman.Member(barcode='00000000',
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': False,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                ],
            'count': {
                'execute': 1,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with barcode only
        # present (and unique) in DB under barcode [TS]
        {
            'member': socman.Member(barcode='00000000',
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': True,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE barcode=?""",
                    (datetime.date.min, '00000000')
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with barcode only
        # present (and unique) in DB under barcode [AF]
        {
            'member': socman.Member(barcode='00000000',
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': False,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                ],
            'count': {
                'execute': 1,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with barcode only
        # present (and unique) in DB under barcode [TSAF]
        {
            'member': socman.Member(barcode='00000000',
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': True,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE barcode=?""",
                    (datetime.date.min, '00000000')
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under barcode
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': False,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                ],
            'count': {
                'execute': 1,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under barcode [TS]
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': True,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE barcode=?""",
                    (datetime.date.min, '00000000')
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under barcode [AF]
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': False,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                unittest.mock.call(
                    """UPDATE users SET firstName=?,lastName=? """
                    """WHERE barcode=?""",
                    ('Ted', 'Bobson', '00000000')
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under barcode [TSAF]
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': True,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000',)
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE barcode=?""",
                    (datetime.date.min, '00000000')
                    ),
                unittest.mock.call(
                    """UPDATE users SET firstName=?,lastName=? """
                    """WHERE barcode=?""",
                    ('Ted', 'Bobson', '00000000')
                    ),
                ],
            'count': {
                'execute': 3,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name only
        # present (and unique) in DB under name
        {
            'member': socman.Member(barcode=None,
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': False,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 1,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name only
        # present (and unique) in DB under name [AF]
        {
            'member': socman.Member(barcode=None,
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': False,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 1,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name only
        # present (and unique) in DB under name [TS]
        {
            'member': socman.Member(barcode=None,
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': True,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE firstName=? AND lastName=?""",
                    (datetime.date.min, 'Ted', 'Bobson'),
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name only
        # present (and unique) in DB under name [TSAF]
        {
            'member': socman.Member(barcode=None,
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': True,
            },
        [
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE firstName=? AND lastName=?""",
                    (datetime.date.min, 'Ted', 'Bobson'),
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 1,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under *name*
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': False,
            },
        [
            [],
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000', )
                    ),
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 2,
                'fetchall': 2,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under *name* [TS]
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': False,
            'update_timestamp': True,
            },
        [
            [],
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000', )
                    ),
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE firstName=? AND lastName=?""",
                    (datetime.date.min, 'Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 3,
                'fetchall': 2,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under *name* [AF]
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': False,
            },
        [
            [],
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000', )
                    ),
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                unittest.mock.call(
                    """UPDATE users SET barcode=? """
                    """WHERE firstName=? AND lastName=?""",
                    ('00000000', 'Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 3,
                'fetchall': 2,
                'commit': 1
                },
            }
        ),

    (   # member with name and barcode
        # present (and unique) in DB under *name* [TSAF]
        {
            'member': socman.Member(barcode='00000000',
                                    name=socman.Name('Ted', 'Bobson'),
                                    college='Wolfson'),
            'autofix': True,
            'update_timestamp': True,
            },
        [
            [],
            [('Ted', 'Bobson')],
            ],
        {
            'values': [
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE barcode=?""",
                    ('00000000', )
                    ),
                unittest.mock.call(
                    """SELECT firstName,lastName FROM users """
                    """WHERE firstName=? AND lastName=?""",
                    ('Ted', 'Bobson')
                    ),
                unittest.mock.call(
                    """UPDATE users SET last_attended=? """
                    """WHERE firstName=? AND lastName=?""",
                    (datetime.date.min, 'Ted', 'Bobson')
                    ),
                unittest.mock.call(
                    """UPDATE users SET barcode=? """
                    """WHERE firstName=? AND lastName=?""",
                    ('00000000', 'Ted', 'Bobson')
                    ),
                ],
            'count': {
                'execute': 4,
                'fetchall': 2,
                'commit': 1
                },
            }
        ),
    ])
def test_get_member(mdb, args, mock_returns, calls):
    """Test get_member with a member object present in the database.

    Tests with various values of `autofix` and `update_timestamp`.
    Tests various possibilities, e.g. member with barcode, name or both, and
    whether member is found in database under barcode or name.
    """
    mdb.mocksql_connect().cursor().fetchall.side_effect = mock_returns

    assert ('Ted', 'Bobson') == mdb.get_member(**args)

    mdb.mocksql_connect().cursor().execute.assert_has_calls(calls['values'])
    assert (calls['count']['execute'] ==
            mdb.mocksql_connect().cursor().execute.call_count)
    assert (calls['count']['fetchall'] ==
            mdb.mocksql_connect().cursor().fetchall.call_count)
    assert (calls['count']['commit'] ==
            mdb.mocksql_connect().commit.call_count)


@pytest.mark.parametrize("member", [
    # None passed as member
    None,
    # None member
    socman.Member(None),
    ])
def test_add_member_none_member(mdb, member):
    """Test add member with a bad (i.e. None) member object."""
    mdb.mocksql_connect().cursor().fetchall.side_effect = []

    with pytest.raises(socman.BadMemberError):
        mdb.add_member(member)

    assert mdb.mocksql_connect().cursor().execute.call_count == 0


@pytest.mark.parametrize("member,mock_returns,execute_call_count", [
    (   # member with name and barcode
        # already present under barcode
        socman.Member(barcode='00000000',
                      name=socman.Name('Ted', 'Bobson'),
                      college='Wolfson'),
        [
            [('Ted', 'Bobson')],
            ],
        3,  # 1 for barcode lookup, 2 for autofix and update_timestamp
        ),
    (   # member with name and barcode
        # already present under name
        socman.Member(barcode='00000000',
                      name=socman.Name('Ted', 'Bobson'),
                      college='Wolfson'),
        [
            [],
            [('Ted', 'Bobson')],
            ],
        4,  # 2 for barcode then name lookup
            # 2 for autofix and update_timestamp
        ),
    ])
def test_add_member_already_present(mdb, member, mock_returns,
                                    execute_call_count):
    """Test add_member with a member already present in the database.

    In this case, no actual UPDATE operation is expected on the database, but
    during the lookup, the timestamp should be updated and the database entry
    autofixed.
    """
    mdb.mocksql_connect().cursor().fetchall.side_effect = mock_returns

    mdb.add_member(member)

    assert (execute_call_count ==
            mdb.mocksql_connect().cursor().execute.call_count)


@pytest.mark.parametrize("member,mock_returns,execute_call,execute_call_count", [
    (   # member with name and barcode
        socman.Member(barcode='00000000',
                      name=socman.Name('Ted', 'Bobson'),
                      college='Wolfson'),
        [
            [],
            [],
            ],
        (
            """INSERT INTO users (barcode, firstName, lastName, """
            """college, datejoined, created_at, updated_at, last_attended) """
            """VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ('00000000', 'Ted', 'Bobson', 'Wolfson',
             datetime.date.min, datetime.datetime.min,
             datetime.datetime.min, datetime.date.min)
            ),
        3  # 2 lookups (name and barcode) + 1 update query
        ),
    ])
def test_add_member_not_yet_present(mdb, member, mock_returns,
                                    execute_call, execute_call_count):
    """Test add_member with a member not yet present in the database.

    This is the case where the actual UPDATE operation should be performed.
    """
    mdb.mocksql_connect().cursor().fetchall.side_effect = mock_returns

    mdb.add_member(member)

    mdb.mocksql_connect().cursor().execute.assert_called_with(*execute_call)
    assert (execute_call_count ==
            mdb.mocksql_connect().cursor().execute.call_count)
