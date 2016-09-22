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

import collections
from datetime import date, datetime
import sqlite3


class Error(Exception):

    """The base class for exceptions in socman."""

    def __init__(self, *args):
        """Create an Error object."""
        Exception.__init__(self, *args)


class BadMemberError(Error):

    """Raised when a bad (typically None) member is passed.

    Attributes:
        member: the bad member object
    """

    def __init__(self, member, *args):
        """Create a BadMemberError for member object `member`."""
        Error.__init__(self, *args)
        self.member = member


class MemberNotFoundError(Error):

    """Raised when a member is not found in the database.

    Attribues:
        member: the member object
    """

    def __init__(self, member, *args):
        """Create a MemberNotFoundError for member object `member`."""
        Error.__init__(self, *args)
        self.member = member


class Name:

    """A person's name.

    Attributes:
        names:  a list of strings representing names
        sep:    the separator string to be used when concatenating names
    """

    def __init__(self, *names, sep=' '):
        """Create a name from a tuple of strings (passed as variable arguments).

        Arguments:
            names:  A list of names which should be strings (or None)
            sep:    The separator used when concatenating parts of the name.

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
        """Return arguments concatenated together separated by `self.sep`.

        Arguments that equal `None` or are entirely whitespace are omitted.
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


Member = collections.namedtuple('Member', 'barcode name college')
Member.__new__.__defaults__ = (None, None)
Member.__doc__ = """
                 A society member.

                 `name` and `college` default to None but `barcode` must be
                 given explicitly.
                 """


class MemberDatabase:

    """Interface to a SQLite3 database of members."""

    class BadSearchAuthorityError(Error):

        """Raised when a bad search authority string is passed.

        The only permissible strings are 'barcode' and 'name'.

        Attributes:
            authority: the bad authority string
        """

        def __init__(self, authority_string, *args):
            """Create a BadSearchAuthorityError for a given authority string.

            Arguments:
                authority_string: the bad authority string
            """
            Error.__init__(self, *args)
            self.authority_string = authority_string

    def __init__(self, db_file='members.db', safe=True):
        """Create a MemberDatabase.

        Arguments:
            db_file:    Filename and path of a SQLite3 database file.
                        Passed directly to sqlite3.Connect().
            safe:       Boolean that determines whether non essential
                        operations are committed immediately or not
                        Note that important operations like adding a member
                        are always committed regardless of this setting.
        """
        self.__connection = sqlite3.connect(db_file)
        self.__safe = safe

    def __del__(self):
        self.__connection.commit()  # here, commit regardless of safe
        self.__connection.close()

    def optional_commit(self):
        """Commit changes to database if `safe` is set to `True`.

        This means increased performance can be chosen over the highest level
        of write safety. For example, by default a timestamp is updated in the
        database every time a record is accessed. If a lot of members are
        checked, it may not be desirable to commit after every such change.
        """
        if self.__safe:
            self.__connection.commit()

    def __sql_build_name_value_pairs(self, member, sep):
        columns = []
        values = ()
        if member.name.first():
            columns += ['firstName=?']
            values += (member.name.first(), )
        if member.name.last():
            columns += ['lastName=?']
            values += (member.name.last(), )
        if not columns:
            # TODO remove None return or replace with exception if necessary
            return None, None
        return sep.join(columns), values

    def __sql_search_phrase(self, member, authority='barcode'):
        if authority == 'barcode':
            return self.__sql_search_barcode_phrase(member)
        elif authority == 'name':
            return self.__sql_search_name_phrase(member)
        raise MemberDatabase.BadSearchAuthorityError

    def __sql_search_barcode_phrase(self, member):
        return 'barcode=?', (member.barcode, )

    def __sql_search_name_phrase(self, member):
        return self.__sql_build_name_value_pairs(member, ' AND ')

    def __sql_update_phrase(self, member, authority):
        # authority='barcode' yields name update query and vice versa
        # if the barcode is authoritative, it is the name we should update
        if authority == 'barcode':
            return self.__sql_build_name_value_pairs(member, sep=',')
        elif authority == 'name':
            return ('barcode=?', (member.barcode,))
        raise MemberDatabase.BadSearchAuthorityError

    def __join_sql_cmds(self, *cmds):
        phrase_list, values_list = zip(*cmds)
        return (''.join(phrase_list),
                tuple(value for values in values_list for value in values))

    def __update_timestamp(self, member, authority='barcode'):
        """Update member last_attended date."""
        self.__connection.cursor().execute(*self.__join_sql_cmds(
            ('UPDATE users SET last_attended=? WHERE ', (date.today(),)),
            self.__sql_search_phrase(member, authority)
            ))

    def __autofix(self, member, authority='barcode'):
        if member.barcode and member.name:
            self.__connection.cursor().execute(*self.__join_sql_cmds(
                ('UPDATE users SET ', ()),
                self.__sql_update_phrase(member, authority),
                (' WHERE ', ()),
                self.__sql_search_phrase(member, authority)
                ))

    def get_member(self, member, update_timestamp=True, autofix=False):
        """Retrieve a member's names from the database.

        Arguments:
            member:     a member object to search for, should contain either
                        barcode, name or both
            update_timestamp:   determines whether to update the record's
                                timestamp in the database when retrieved
            autofix:    determines whether to fix broken records (see below)

        Returns:
            A tuple containing the member's first and last names as strings.

        Raises:
            MemberNotFoundError: A member was not found in a database lookup
            BadMemberError: The member passed to `get_member` has neither name
                            nor barcode.

        The Lookup
        ----------
        The barcode always takes precedence where possible. If both a name and
        barcode are supplied in `member` then the lookup will be done by
        barcode, and only if that lookup fails will the name be used.
        If only a name is provided, it will of course be used for lookup.

        Autofixing
        ----------
        If the barcode lookup succeeds and a name is also provided, the autofix
        mechanism will update the name in the database record using the name
        provided. Similarly, if barcode lookup fails but name lookup succeeds,
        then the barcode will be updated on any records found.

        Duplicate Records
        -----------------
        At this time, `get_member` does not attempt to autofix duplicate
        records. This should be implemented at a future date.
        """
        cursor = self.__connection.cursor()

        if not member or not (member.barcode or member.name):
            raise BadMemberError(member)

        search_authority = None
        # first try to find member by barcode, if possible
        if member.barcode:
            cursor.execute(*self.__join_sql_cmds(
                ('SELECT firstName,lastName FROM users WHERE ', ()),
                self.__sql_search_barcode_phrase(member)
                ))
            users = cursor.fetchall()
            if users:
                search_authority = 'barcode'

        # barcode lookup failed; now try finding by name
        if not search_authority and member.name:
            cursor.execute(*self.__join_sql_cmds(
                ('SELECT firstName,lastName FROM users WHERE ', ()),
                self.__sql_search_name_phrase(member)
                ))
            users = cursor.fetchall()
            if users:
                search_authority = 'name'

        if not search_authority:
            raise MemberNotFoundError(member)

        if update_timestamp:
            self.__update_timestamp(member, authority=search_authority)

        if autofix:
            self.__autofix(member, authority=search_authority)

        if autofix or update_timestamp:
            self.optional_commit()

        # TODO dedupe if necessary
        return users[0]

    def __sql_add_query(self, member):
        barcode = member.barcode
        if not barcode:
            barcode = ''

        name = member.name
        if not name:
            name = Name()

        college = member.college
        if not college:
            college = ''

        return ("""INSERT INTO users (barcode, firstName, """
                """lastName, college, """
                """datejoined, created_at, updated_at, last_attended) """
                """VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (barcode, name.first(), name.last(), college,
                 date.today(), datetime.utcnow(),
                 datetime.utcnow(), date.today()))

    def add_member(self, member):
        """Add a member to the database.

        First the member is looked up with `get_member`. If found, autofixing
        is applied and then the member is returned. If the member is not found,
        he/she will be added to the database.

        See `get_member` for details of the lookup and autofix mechanism.

        Arguments:
            member:     a member object to add, should contain either at least
                        one of a name and a barcode
        Returns:
            Nothing.

        Raises:
            BadMemberError: The member passed to `get_member` has neither name
                            nor barcode.
        """
        if not member or not (member.barcode or member.name):
            raise BadMemberError(member)

        try:
            self.get_member(member=member, update_timestamp=True, autofix=True)
        except MemberNotFoundError:
            pass
        else:
            return  # member already present so we are done

        # if member does not exist, add him/her
        cursor = self.__connection.cursor()
        cursor.execute(*self.__sql_add_query(member))

        # direct commit here: don't want to lose new member data
        self.__connection.commit()

    def member_count(self):
        """Return the number of members in the database.

        This is the number of rows in the `users` table.
        """
        cursor = self.__connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return int(cursor.fetchone()[0])
