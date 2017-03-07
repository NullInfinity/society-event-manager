#!/usr/bin/env python3
from sys import argv
from socman import Name, Member, MemberDatabase, MemberNotFoundError

# track the number of members attending
attended = 0
newmembers = 0
oneoffs = 0

if len(argv) <= 1:
    print('No database file specified.')
    exit(1)
else:
    db_file = argv[1]

if len(argv) >= 3:
    report_file = argv[2]
else:
    report_file = None

print('Opening {}'.format(db_file))
db = MemberDatabase(db_file)

while True:
    try:
        barcode = input('Enter barcode: ')
    except EOFError:
        break

    if barcode:
        barcode = barcode[:7] # only care about first 7 digits
        member = Member(barcode=barcode)
        try:
            first_name, last_name = db.get_member(member)
        except MemberNotFoundError:
            print('Not a member. Enter name to add or EOF to cancel.')
            try:
                first_name = input('First name: ')
                last_name = input('Last name: ')
            except EOFError:
                oneoffs += 1
                continue
            member = Member(name=Name(first_name, last_name), barcode=barcode)
            db.add_member(member)
            newmembers += 1

        print(first_name, last_name)
        attended += 1

members = attended - newmembers - oneoffs
summary = """Attendance Summary
------------------
Members:        {}
New Signups:    {}
One offs:       {}
Total:          {}""".format(members, newmembers, oneoffs, attended)

print(summary)

if report_file is not None:
    print('Writing summary to {}'.format(report_file))
    fhandle = open(report_file, 'w')
    fhandle.write(summary)
