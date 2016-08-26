"""
socman is a society membership and event management library.

It tracks members in a sqlite database to enable membership tracking
and verification. It can also track event data such as name and date,
along with event attendance statistics.

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

from collections import namedtuple
from datetime import date, datetime
import sqlite3


class Name:

    """A person's name."""

    def __init__(self, *names, sep=' '):
        """Create a name from a tuple of strings (passed as variable arguments).

        Arguments:
            names   A list of names which should be strings (or None)
            sep     The separator between names when concatenated to form strings.

        To create a name with just a first name, pass None as the last name:

        >>> my_name = Name('Ted', None)     # Ted is first name
        >>> my_name = Name('Ted')           # Ted is last name

        The full name string will be 'Ted' in both cases above.
        Similarly, to create a name with just a middle name, pass
        None as both the first and the last name:

        >>> my_name = Name(None, 'Ted', None)

        Any number of None names may be passed, as they are ignored when
        building name strings (except for place holding first/last names).
        """
        # None names in list have semantic value, but if list contains only
        # Nones then the Name constructed should be identical to the empty
        # Name constructed by Name()
        if not [name for name in names if name is not None]:
            names = ()

        self.names = list(names)
        self.sep = sep

    def __bool__(self):
        return bool(self.names)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __makestr(self, names):
        """Return arguments concatenated together separated by Name.sep.

        Arguments that equal None or are entirely whitespace are omitted.
        """
        return self.sep.join([name for name in names if name and name.strip()])

    def first(self):
        """Return first name as a string."""
        return self.__makestr(self.names[:-1][:1])

    def middle(self):
        """Return middle names concatenated as a string."""
        return self.__makestr(self.names[1:-1])

    def given(self):
        """Return first and any middle names concatenated as a string."""
        return self.__makestr(self.names[:-1])

    def last(self):
        """Return last name as a string."""
        return self.__makestr(self.names[-1:])

    def full(self):
        """Return full name as a string."""
        return self.__makestr(self.names)


Member = namedtuple('Member', 'barcode name college')
Member.__new__.__defaults__ = (None, None)
Member.__doc__ = """
                 A society member.

                 `name` and `college` default to None but `barcode` must be
                 given explicitly.
                 """


class MemberDatabase:

    """Interface to a SQLite3 database of members."""

    def __init__(self, db_file='members.db', safe=True):
        """Create a MemberDatabase.

        Arguments:
            db_file     Filename and path of a SQLite3 database file.
                        Passed directly to sqlite3.Connect().
            safe        Boolean that determines whether non essential
                        operations are committed immediately or not
                        Note that important operations like adding a member
                        are always committed regardless of this setting.
        """

        self.__connection = sqlite3.connect(db_file)
        self.__safe = safe

    def __del__(self):
        self.__connection.commit()  # here, commit regardless of safe
        self.__connection.close()

    # wrapper around sqlite3.Connection.commit():
    # commits if safe is set to True
    # this means users can optionally disable autocommiting for potentially
    # better performance at the cost of reduced data safety on crashes
    def optional_commit(self):
        """Commits changes to database if `safe` is set to `True`"""

        if self.__safe:
            self.__connection.commit()

    def sql_build_name_value_pairs(self, member, sep):
        if not member.name:
            return None, None
        columns = []
        values = ()
        if member.name.first():
            columns += ['firstName=?']
            values += (member.name.first(), )
        if member.name.last():
            columns += ['lastName=?']
            values += (member.name.last(), )
        if not columns:
            return None, None
        return sep.join(columns), values

    def sql_search_barcode_phrase(self, member):
        if not member.barcode:
            return None, None
        return 'barcode=?', (member.barcode, )

    def sql_search_name_phrase(self, member):
        if not member.name:
            return None, None
        return self.sql_build_name_value_pairs(member, ' AND ')

    def sql_search_phrase(self, member):
        phrase, values = self.sql_search_barcode_phrase(member)
        if not phrase:
            phrase, values = self.sql_search_name_phrase(member)
        return phrase, values

    def sql_update_barcode_phrase(self, member):
        if not member.barcode:
            return None, None
        return ('barcode=?', (member.barcode,) )

    def sql_update_name_phrase(self, member):
        return self.sql_build_name_value_pairs(member, ',')

    def sql_search_query(self, member):
        phrase, values = self.sql_search_phrase(member)
        if not phrase:
            return None, None
        return ('SELECT firstName,lastName FROM users WHERE ' + phrase, values)

    def sql_search_barcode_query(self, member):
        phrase, values = self.sql_search_barcode_phrase(member)
        if not phrase:
            return None, None
        return ('SELECT firstName,lastName FROM users WHERE ' + phrase, values)

    def sql_search_name_query(self, member):
        phrase, values = self.sql_search_name_phrase(member)
        if not phrase:
            return None, None
        return ('SELECT firstName,lastName FROM users WHERE ' + phrase, values)

    def sql_update_barcode_query(self, member):
        set_phrase, set_values = self.sql_update_barcode_phrase(member)
        search_phrase, search_values = self.sql_search_name_phrase(member)
        if not set_phrase or not search_phrase:
            return None, None
        return ('UPDATE users SET ' + set_phrase + ' WHERE ' + search_phrase, set_values + search_values)

    def sql_update_name_query(self, member):
        set_phrase, set_values = self.sql_update_name_phrase(member)
        search_phrase, search_values = self.sql_search_barcode_phrase(member)
        if not set_phrase or not search_phrase:
            return None, None
        return ('UPDATE users SET ' + set_phrase + ' WHERE ' + search_phrase, set_values + search_values)

    def sql_update_last_attended_query(self, member):
        search_phrase, search_values = self.sql_search_phrase(member)
        if not search_phrase:
            return None, None
        return ('UPDATE users SET last_attended=? WHERE ' + search_phrase, (date.today(),) + search_values)

    def get_member(self, barcode=None, *, member=None, update_timestamp=True, autofix=False):
        c = self.__connection.cursor()

        if not member:
            if not barcode:
                return None
            member = Member(barcode)

        # first try to find member by barcode, if available
        query, values = self.sql_search_barcode_query(member)
        if query:
            c.execute(query, values)
            users = c.fetchall()
            if users:
                # if necessary update last_attended date
                if update_timestamp:
                    ts_query, ts_values = self.sql_update_last_attended_query(member)
                    if ts_query:
                        c.execute(ts_query, ts_values)

                # if autofix is set and both names are provided, correct names
                if autofix:
                    af_query, af_values = self.sql_update_name_query(member)
                    if af_query:
                        c.execute(af_query, af_values)

                # in case we updated timestamp or names, commit
                self.optional_commit()

                # TODO dedupe if necessary
                return users[0]

        # barcode lookup failed; now try finding by name
        query, values = self.sql_search_name_query(member)
        if not query:
            return None

        c.execute(query, values)
        users = c.fetchall()

        if not users:
            return None  # still nothing found

        # found them so update last_attended if update_timestamp is set
        if update_timestamp:
            # todo find better way to choose search phrase (barcode/name)
            temp_member = member._replace(barcode = None)
            ts_query, ts_values = self.sql_update_last_attended_query(temp_member)
            if ts_query:
                c.execute(ts_query, ts_values)
        # and barcode if autofix is set
        if autofix and member.barcode:
            af_query, af_values = self.sql_update_barcode_query(member)
            c.execute(af_query, af_values)
            self.optional_commit()

        # TODO dedupe if necessary
        return users[0]

    def sql_add_query(self, member):
        return 'INSERT INTO users (barcode, firstName, lastName, college, datejoined, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (member.barcode, member.name.first(), member.name.last(), member.college, date.today(), datetime.utcnow(), datetime.utcnow())

    def add_member(self, member):
        if not member:
            return False

        if self.get_member(member=member, update_timestamp=False, autofix=True):
            return False

        # if member does not exist, add them
        cursor = self.__connection.cursor()
        cursor.execute(*self.sql_add_query(member))
        self.__connection.commit()  # direct commit here: don't want to lose new member data

        return True
