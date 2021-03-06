#!/usr/bin/env pythonw

from Carbon.Cm import OpenDefaultComponent
from CarbonX.OSA import OSAComponentInstance
from CarbonX.kAE import *
from CarbonX.AE import *
from aem import Codecs

codecs = Codecs()

osac = OSAComponentInstance(OpenDefaultComponent('osa ', 'ascr'))

scriptDesc = codecs.pack('''
tell app "finder" to home
''')



f = osac.OSAGetCreateProc()

print f


def c(*args): # (AEEventClass theAEEventClass, AEEventID theAEEventID, AEAddressDesc target, AEReturnID returnID, AETransactionID transactionID) -> (AppleEvent result)
	print args
	#raise 'test error'
	return f(*args)
	return AECreateAppleEvent(*args)


osac.OSASetCreateProc(c)


print `codecs.unpack(osac.OSADoScript(scriptDesc, 0, typeChar, 0))`


print osac.OSAGetCreateProc()

print

osac.OSASetCreateProc(f)

print `codecs.unpack(osac.OSADoScript(scriptDesc, 0, typeChar, 0))`



print osac.OSAGetCreateProc()