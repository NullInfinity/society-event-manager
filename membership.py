"""MemberDatabase tracks and verifies society membership in a sqlite database"""

import sqlite3
from datetime import date, datetime

class Name:
    __sep = ' '

    def __init__(self, *names):
        self.names = list(names)

    def first(self):
        return Name.__sep.join(self.names[:-1])

    def last(self):
        return Name.__sep.join(self.names[-1:])

    def full(self):
        return Name.__sep.join(self.names)

    def __bool__(self):
        return bool(self.names)

class MemberDatabase:
    def __init__(self, dbFile='members.db', safe=True):
        self.__connection = sqlite3.connect(dbFile)
        self.__safe = safe

    def __del__(self):
        self.__connection.commit() # here use sql commit() directly: we want to commit regardless of safe
        self.__connection.close()

    # wrapper around sqlite3.Connection.commit():
    # commits if safe is set to True
    # this means users can optionally disable autocommiting for potentially better
    # performance at the cost of reduced data safety on crashes
    def optional_commit(self):
        if self.__safe:
            self.__connection.commit()

    def get_member(self, memberId, firstName=None, lastName=None, updateTimestamp=True, autoFix=False):
        c = self.__connection.cursor()

        # first try to find member by memberId, if available
        if memberId:
            c.execute('SELECT firstName,lastName FROM users WHERE barcode=?', (memberId,))
            users = c.fetchall()
            if users:
                # TODO dedupe if necessary

                # if necessary update last_attended date
                if (updateTimestamp):
                    c.execute('UPDATE users SET last_attended=? WHERE barcode=?', (date.today(), memberId))

                # if autoFix is set and both names are provided, correct names
                if autoFix and firstName and lastName:
                    c.execute('UPDATE users SET firstName=?, lastName=? WHERE barcode=?', (firstName, lastName, memberId))

                self.optional_commit()

                return users[0]

        # ID lookup failed; now try finding by name
        if not firstName or not lastName:
            return None

        c.execute('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (firstName, lastName))
        users = c.fetchall()

        if not users:
            return None # still nothing found

        # found them so update barcode if autoFix is set
        if autoFix and memberId:
            c.execute('UPDATE users SET barcode=? WHERE firstName=? AND lastName=?', (memberId, firstName, lastName))
            self.optional_commit()

        # TODO dedupe if necessary

        return users

    def add_member(self, memberId, firstName, lastName, college):
        if self.get_member(memberId, firstName=firstName, lastName=lastName, updateTimestamp=False, autoFix=True):
            return False

        # if member does not exist, add them
        c = self.__connection.cursor()
        c.execute('INSERT INTO users (barcode, firstName, lastName, college, datejoined, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (memberId, firstName, lastName, college, date.today(), datetime.utcnow(), datetime.utcnow()))
        self.__conn.commit() # direct commit here: don't want to lose new member data

        return True
