#!/usr/bin/env python3

from appscript import terminology as t

from aem import Application

#app = Application(path='/System/Library/CoreServices/Finder.app')
#app = Application(path='/Applications/Adobe Photoshop 2022/Adobe Photoshop 2022.app')
#app = Application(path='/Applications/Adobe Illustrator 2022/Adobe Illustrator.app')
app = Application(path='/Applications/Microsoft Excel.app')

keys = ['TYPE', 'TYPE', 'REF', 'REF']

from pprint import pprint
sdef = t.sdefforapp(app)
tables = t.tablesforsdef(sdef)

aete = t.aetesforapp(app)
tables2 = t.tablesforaetes(aete)

print('\nSDEF only:')
for a, b, c in zip(tables, tables2, keys):
	diff = set(a) - (set(b))
	print('\n', c)
	for k in diff:
		print(k,'\t\t\t\t\t\t', a.get(k) ,'\t\t\t\t\t\t', b.get(k))

print('\nAETE only:')
for a, b, c in zip(tables, tables2, keys):
	diff = set(b) - (set(a))
	print('\n', c)
	for k in diff:
		print(k,'\t\t\t\t\t\t', a.get(k) ,'\t\t\t\t\t\t', b.get(k))



from appscript import app

ps = app(id='com.adobe.photoshop', terms='sdef')
print(ps.documents.name())

