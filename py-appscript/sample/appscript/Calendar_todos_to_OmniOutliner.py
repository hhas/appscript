#!/usr/bin/env python3

# Creates an OmniOutliner document listing all the 'To Do' items from Calendar.

from appscript import *

toprow = app('OmniOutliner').documents.end.make(new=k.document).rows[1]
toprow.properties.set({k.topic: 'Master todo list', k.expanded: True})

for cal in app('Calendar').calendars.get():
    subrow = toprow.rows.end.make(new=k.row, 
            with_properties={k.topic: cal.name.get(), k.expanded: True})
    for summary in cal.todos.summary.get():
        subrow.rows.end.make(new=k.row, 
                with_properties={k.topic: summary})