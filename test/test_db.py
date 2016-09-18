"""
test_db.py contains the functional tests involving a real database file.

Tests on socman should be run with `python -m pytest`. To run just these tests,
run `pytest tests/test_db.py`.


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
import datetime
import sqlite3

import pytest

import socman


@pytest.fixture
def db_file(tmpdir):
    """Create test DB file with sample entries."""
    db_path = str(tmpdir.join('test.db'))
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE users ("""
                   """id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, """
                   """firstName VARCHAR(255), """
                   """lastName VARCHAR(255), """
                   """barcode INTEGER, """
                   """datejoined DATE, """
                   """created_at DATETIME, """
                   """updated_at DATETIME, """
                   """college VARCHAR(255), """
                   """last_attended DATE)"""
                   )

    cursor.execute("""INSERT INTO users """
                   """(firstName,lastName,barcode,college,"""
                   """datejoined,created_at,updated_at,last_attended) """
                   """VALUES (?,?,?,?,?,?,?,?)""",
                   ('Ted', 'Bobson', '12341234', 'Wolfson',
                       datetime.date.min, datetime.datetime.min,
                       datetime.datetime.min, datetime.date.min))

    conn.commit()
    conn.close()

    yield db_path


@pytest.fixture
def mdb(db_file):
    return socman.MemberDatabase(db_file)


def test_get_member_bad_member_(mdb):
    with pytest.raises(socman.BadMemberError):
        mdb.get_member(None)


@pytest.mark.parametrize('member', [
    socman.Member('11111111'),
    socman.Member(None, socman.Name('Bill', 'Rogers')),
    socman.Member('11111111', socman.Name('Bill', 'Rogers'))
    ])
def test_get_member_not_present(mdb, member):
    """Test get_member against member not present in database."""
    with pytest.raises(socman.MemberNotFoundError):
        mdb.get_member(member)


@pytest.mark.parametrize('member', [
    socman.Member('12341234'),
    socman.Member(None, socman.Name('Ted', 'Bobson')),
    socman.Member('12341234', socman.Name('Ted', 'Bobson')),
    socman.Member('12341234', socman.Name('Bill', 'Rogers')),
    socman.Member('11111111', socman.Name('Ted', 'Bobson')),
    ])
@pytest.mark.parametrize('autofix', [True, False])
def test_get_member_present(mdb, member, autofix):
    assert ('Ted', 'Bobson') == mdb.get_member(member, autofix=autofix)
    if autofix and member.barcode and member.name:
        assert ((member.name.given(), member.name.last()) ==
            mdb.get_member(socman.Member(member.barcode)))

#@pytest.mark.parametrize('member', [
#    socman.Member('12341234'),
#    socman.Member(None, socman.Name('Ted', 'Bobson')),
#    socman.Member('12341234', socman.Name('Ted', 'Bobson')),
#    socman.Member('12341234', socman.Name('Bill', 'Rogers')),
#    socman.Member('11111111', socman.Name('Ted', 'Bobson')),
#    ])
#def test_add_member_already_present(mdb, member):
#    """Test that adding an already present member runs autofix."""
#    mdb.add_member(member)
#    assert ((member.name.given(), member.name.last()) ==
#        mdb.get_member(socman.Member(member.barcode)))
