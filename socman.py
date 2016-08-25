"""
socman society membership library

tracks and verifies society membership in a sqlite database"""

import sqlite3
from datetime import date, datetime


class Name:
    __sep = ' '

    def __init__(self, *names):
        self.names = list(names)

    def __bool__(self):
        return bool(self.names)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    # returns first and all middle names
    def first(self):
        return Name.__sep.join(self.names[:-1])

    def last(self):
        return Name.__sep.join(self.names[-1:])

    def full(self):
        return Name.__sep.join(self.names)


class Member:
    def __init__(self, barcode, *names, name=None, college=None):
        self.barcode = barcode
        if name:
            self.name = name
        else:
            self.name = Name(*names)
        self.college = college

    def __bool__(self):
        return bool(self.barcode or self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class MemberDatabase:
    def __init__(self, dbFile='members.db', safe=True):
        self.__connection = sqlite3.connect(dbFile)
        self.__safe = safe

    def __del__(self):
        self.__connection.commit()  # here, commit regardless of safe
        self.__connection.close()

    # wrapper around sqlite3.Connection.commit():
    # commits if safe is set to True
    # this means users can optionally disable autocommiting for potentially
    # better performance at the cost of reduced data safety on crashes
    def optional_commit(self):
        if self.__safe:
            self.__connection.commit()

    def sql_build_name_value_pairs(self, member, sep):
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
            temp_member = member
            temp_member.barcode = None  # TODO find better way to choose search phrase (barcode/name)
            ts_query, ts_values = self.sql_update_last_attended_query(member)
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
