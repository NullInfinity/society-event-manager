#!/usr/bin/env python3
from datetime import date
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
    report_filename = argv[2]
else:
    report_filename = None
log_filename = str(date.today()) + '.log'

print('Opening {}'.format(db_file))
db = MemberDatabase(db_file)

log_file = open(log_filename, 'w')

while True:
    try:
        barcode = input('Enter barcode (or QUIT to exit): ')
    except EOFError:
        break
    if barcode == 'QUIT':
        break;
    if barcode == 'ONE':
        oneoffs += 1
        continue

    if barcode:
        barcode = barcode[:7]  # only care about first 7 digits
        member = Member(barcode=barcode)
        try:
            first_name, last_name = db.get_member(member)
        except MemberNotFoundError:
            print('Not a member. Enter name to add member.')
            print('Enter EOF or blank first and last name to cancel.')
            try:
                first_name = input('First name: ')
                last_name = input('Last name: ')
            except EOFError:
                oneoffs += 1
                print('Cancelling adding member.')
                print()
                continue
            if first_name == '' and last_name == '':
                # cancel adding member
                print('Cancelling adding member.')
                print()
                continue
            member = Member(name=Name(first_name, last_name), barcode=barcode)
            db.add_member(member)
            print('NEWMEMBER: {} ({})'.format(
                member.barcode,
                member.name.full()
                ), file=log_file)
            print(file=log_file)
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

if report_filename is not None:
    print('Writing summary to {}'.format(report_filename))
    with open(report_filename, 'a') as report_file:
        print(str(date.today()), file=report_file)
        print('----------', file=report_file)
        print(summary, file=report_file)
        print('----------', file=report_file)
        print(file=report_file)
