#!/usr/bin/env python3

from osaterminology.dom.sdefparser import *

res = parseapp('/System/Applications/Reminders.app')

print(res)
print(res.classes())
print(res.commands())