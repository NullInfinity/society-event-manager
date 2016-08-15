"""Manage society membership by checking member IDs and adding new members"""

import sqlite3

class MemberDatabase:
    def __init__(self, dbFile = 'members.db', safe = True):
        self.__connection = sqlite3.connect(dbFile)
        self.__safe = safe

    def __del__(self):
        self.__connection.commit() # here use actual commit: we want to commit regardless of safe
        self.__connection.close()

    # wrapper around sqlite3.Connection.commit():
    # commits if safe is set to True
    # this means users can optionally disable autocommiting for potentially better
    # performance at the cost of reduced data safety on crashes
    def optionalCommit(self):
        if self.__safe:
            self.__connection.commit()

    def getMember(self, memberId, firstName=None, lastName=None, updateTimestamp = True, autoFix = False):
        c = self.__connection.cursor()

        # first try to find member by memberId, if available
        if memberId:
            c.execute('SELECT firstName,lastName FROM users WHERE barcode=?', (memberId,))
            users = c.fetchall()
            if users:
                # todo dedupe if necessary

                # if necessary update last_attended date
                if (updateTimestamp):
                    c.execute('UPDATE users SET last_attended=? WHERE barcode=?', (datetime.date.today(), memberId))

                self.optionalCommit()

                return users[0]

        # ID lookup failed; now try finding by name
        if not firstName or not lastName:
            return None

        c.execute('SELECT firstName,lastName FROM users WHERE firstName=? AND lastName=?', (firstName, lastName))
        users = c.fetchall()

        if not users:
            return None # still nothing found

        # found them so update barcode if set
        c.execute('UPDATE users SET barcode=? WHERE firstName=? AND lastName=?', (memberId, firstName, lastName))
        self.optionalCommit()

        # TODO dedupe if necessary

        return users

    def addMember(self, memberId, firstName, lastName, college):
        c = self.__connection.cursor()
        c.execute('INSERT INTO users (barcode, firstName, lastName, college, datejoined, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (memberId, firstName, lastName, college, date.today(), datetime.utcnow(), datetime.utcnow()))
        __conn.commit() # direct commit here: don't want to lose new member data

        return True
