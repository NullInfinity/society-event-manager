"""Manage society membership by checking member IDs and adding new members"""

import sqlite3

class MemberDatabase:
    def __init__(self, dbFile = 'members.db'):
        self.__connection = sqlite3.connect(dbFile)

    def __del__(self):
        self.__connection.commit()
        self.__connection.close()

    def getMember(self, memberId):
        c = self.__connection.cursor()
        c.execute('SELECT firstName,lastName FROM users WHERE barcode=?', (memberId,))
        return c.fetchone()
