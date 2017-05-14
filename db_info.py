#!/usr/bin/env python3
from datetime import date
from sys import argv
from socman import Name, Member, MemberDatabase

if len(argv) <= 1:
    print('No database file specified.')
    exit(1)
else:
    db_file = argv[1]

db = MemberDatabase(db_file)
print('There are {} members in the database.'.format(db.member_count()))
