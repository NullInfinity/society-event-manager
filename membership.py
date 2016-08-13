"""Manage society membership by checking member IDs and adding new members"""

import sqlite3

class MemberDatabase:
    def __init__(self, dbFile = 'members.db', safe = True):
        self.__connection = sqlite3.connect(dbFile)
        self.__safe = safe

    def __del__(self):
        self.__connection.commit()
        self.__connection.close()

    # wrapper around sqlite3.Connection.commit():
    # commits if safe is set to True
    # this means users can optionally disable autocommiting for potentially better
    # performance at the cost of reduced data safety on crashes
    def commit(self):
        if self.__safe:
            conn.commit()

    def getMember(self, memberId, updateTimestamp = True):
        c = self.__connection.cursor()
        c.execute('SELECT firstName,lastName FROM users WHERE barcode=?', (memberId,))
        # todo: if updateTimestamp then update last_attended time
        return c.fetchone()

    def addMember(self, memberId, firstName, lastName, college):
        c = self.__connection.cursor()
        c.execute('INSERT INTO users (barcode, firstName, lastName, college, datejoined, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (memberId, firstName, lastName, college, date.today(), datetime.utcnow(), datetime.utcnow()))
