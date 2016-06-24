#!/usr/bin/python3
import membership
from datetime import date

print('Society Event Manager 0.1')

event_name = input('Please enter event name: ')
event_date = date.today()
print('The date is {0}.'.format(event_date))
print()

print('Proceed to check membership and attendance will be tracked automatically.')
mdb = membership.MemberDatabase('members.db')
oneTime = 0
signUps = 0
membersPresent = 0

def checkMember(barcode):
    # check member database for barcode
    names = mdb.getMember(barcode)

    if names == None:
        # not found so first offer to find by name
        print('Barcode not found. Try searching by name.')
        names = input('First name: '), input('Last name: ')
        member = mdb.
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

    if barcode == 'NOT' or !checkMember():
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
totalAttendees = oneTime + signUps + membersPresent
print()
print('There were {0} attendees, of which {1} were existing members, {2} were newly signed up members and {3} paid a one time entry fee.'.format(totalAttendees, membersPresent, signUps, oneTime))

# now record this information
print('This information has been recorded. Thank you for using the society event manager.')
