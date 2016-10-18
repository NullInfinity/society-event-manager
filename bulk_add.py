import sys

import socman

mdb = socman.MemberDatabase(sys.argv[1])

while True:
    first_name = input('Enter first name:')
    if not first_name:
        break
    last_name = input('Enter last name:')
    if not last_name:
        break
    barcode = input('Enter barcode number:')
    if not barcode:
        break

    mdb.add_member(socman.Member(barcode, name=socman.Name(first_name, last_name)))
