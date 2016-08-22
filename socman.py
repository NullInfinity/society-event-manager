#!/usr/bin/env python3
from membership import Name, Member, MemberDatabase
from datetime import date

APP_NAME = "socman.py"
APP_VERSION = "0.1"

class Event:
    def __init__(self, name):
        self.name = name
        self.date = date.today()
        self.one_time = 0
        self.sign_ups = 0
        self.members_present = 0

    def total_attendees(self):
        return self.one_time + self.sign_ups + self.members_present

    def __str__(self):
        return 'There were {0} attendees, of which {1} were existing members, {2} were newly signed up members and {3} paid a one time entry fee.'.format(self.total_attendees(), self.members_present, self.sign_ups, self.one_time)

event_name = input('Please enter event name: ')
print('The date is {0}.'.format(event_date))
print()
print('Proceed to check membership and attendance will be tracked automatically.')

DATABASE_FILE = 'members.db'
mdb = MemberDatabase(DATABASE_FILE)


def checkMember(barcode):
    # check member database for barcode
    names = mdb.getMember(barcode)

    if names == None:
        # not found so first offer to find by name
        print('Barcode not found. Try searching by name.')
        names = input('First name: '), input('Last name: ')
        member = mdb.getMember(barcode, firstName = names[0], lastName = names[1])
    else:
        # found the member in the database, great!
        print('Welcome, {0} {1}.'.format(*names))
        membersPresent = membersPresent + 1
    print()

while True:
    # read barcode from stdin
    barcode = input('Enter member ID/barcode (or <QUIT>/<NOT> a member/<HELP>): ')

    # check if user wants to quit
    if barcode == 'QUIT':
        print('quit')
        break

    if barcode == 'NOT' or not checkMember():
        # add member?
        pass
    #offer to add, make onetime sale, or cancel
        print('Not a member. You may either\n<ADD> a new member\nMake a <ONE>time sale, or\n<CANCEL>')
        response = input()
        if response == 'ADD':
            # add member!
            signUps = signUps + 1
        elif response == 'ONE':
            # track onetime attendance
            oneTime = oneTime + 1

# wrap up

# now record this information
print('This information has been recorded. Thank you for using the society event manager.')
