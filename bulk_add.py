#!/usr/bin/env python3
from sys import argv
from socman import Name, Member, MemberDatabase

# track the number of members added
count=0

if len(argv) <= 1:
    print('No database file specified.')
    exit(1)
else:
    db_file = argv[1]

print('Opening {}'.format(db_file))
db = MemberDatabase(db_file)

while True:
    try:
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')
        barcode = input('Enter barcode: ')
    except EOFError:
        break

    if first_name and last_name and barcode:
        member = Member(name=Name(first_name, last_name), barcode=barcode)
        db.add_member(member)
        count += 1

print('Done adding {} members.'.format(count))
