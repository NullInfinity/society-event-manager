#!/usr/bin/env python3
from datetime import date
from sys import argv
from socman import Name, Member, MemberDatabase

if len(argv) <= 1:
    print('No database file specified.')
    exit(1)
else:
    db_file = argv[1]

if len(argv) > 2:
    csv_filename = argv[2]
else:
    csv_filename = None

db = MemberDatabase(db_file)
print('There are {} members in the database.'.format(db.member_count()))

if csv_filename:
    print('Dumping database to {}.'.format(csv_filename))
    db.write_csv(csv_filename)
