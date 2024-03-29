#!/usr/bin/env python3

# Lists the name and email(s) of every person in Contacts
# with one or more email addresses.

from appscript import *

peopleref = app('Contacts').people[its.emails != []]
for name, emails in zip(peopleref.name.get(), peopleref.emails.value.get()):
	print(name, emails)