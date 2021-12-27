""" ASTranslate -- render Apple events sent by AppleScript in appscript syntax """

from AppKit import *
import objc
from PyObjCTools import AppHelper

import aem

import _astranslate, eventformatter
from constants import *


# TO DO: `tell app "TextEdit" to count documents` -> app('TextEdit').count(None, each=k.document) but None should be `app` or omitted entirely


#######

_userDefaults = NSUserDefaults.standardUserDefaults()

if not _userDefaults.integerForKey_('defaultOutputLanguage'):
	_userDefaults.setInteger_forKey_(0, 'defaultOutputLanguage')

_standardCodecs = aem.Codecs()


#######

class ASTranslateDocument(NSDocument):
	
	codeView = objc.IBOutlet('codeView')
	resultView = objc.IBOutlet('resultView')
	
	_currentStyle = 0
	
	def setCurrentStyle_(self, v):
		self._currentStyle = v
		self.resultView.setString_('\n\n'.join(self._resultStores[v]))
		_userDefaults.setInteger_forKey_(v, 'defaultOutputLanguage')
	setCurrentStyle_ = objc.accessor(setCurrentStyle_)
	    
	def currentStyle(self):
		return self._currentStyle
	currentStyle = objc.accessor(currentStyle)
	
	def _addResult_to_(self, kind, val):
		if kind == kLangAll:
			for lang in self._resultStores:
				lang.append(val)
		else:
			self._resultStores[kind].append(val)
		if kind == self.currentStyle() or kind == kLangAll:
			self.resultView.textStorage().mutableString().appendString_(
					('%s\n\n' % self._resultStores[self.currentStyle()][-1]))
			self.resultView.setTextColor_(NSColor.textColor())
	
	
	def windowNibName(self): # a default NSWindowController is created automatically
		return "ASTranslateDocument"

	def windowControllerDidLoadNib_(self, controller):
		self._resultStores = [[] for _ in range(eventformatter.kLanguageCount)]
		self.setCurrentStyle_(_userDefaults.integerForKey_('defaultOutputLanguage'))
	
	@objc.IBAction
	def runScript_(self, sender):
		self.resultView.setString_('')
		for lang in self._resultStores:
			while lang:
				lang.pop()
		try:
			sourceDesc = _standardCodecs.pack(self.codeView.string())
			handler = eventformatter.makeCustomSendProc(
					self._addResult_to_, _userDefaults.boolForKey_('sendEvents'))
			result = _astranslate.translate(sourceDesc, handler) # returns tuple; first item indicates if ok
			if result[0]: # script result
				script, _ = (_standardCodecs.unpack(desc) for desc in result[1:])
				self.codeView.setString_(script)
				self._addResult_to_(kLangAll, 'OK')
			else: # script error info
				script, errorNum, errorMsg, pos = (_standardCodecs.unpack(desc) for desc in result[1:])
				start, end = (pos[aem.AEType(k)] for k in [b'srcs', b'srce'])
				if script:
					errorKind = 'Runtime'
					self.codeView.setString_(script)
				else:
					errorKind = 'Compilation'
				self._addResult_to_(kLangAll, 
						'%s Error:\n%s (%i)' % (errorKind, errorMsg, errorNum))
				self.codeView.setSelectedRange_((start, end - start))
		except aem.ae.MacOSError as e:
			self._addResult_to_(kLangAll, 'OS Error: %i' % e.args[0])
		except Exception as e:
			self._addResult_to_(kLangAll, 'Unexpected Error: {}'.format(e))
	
	def isDocumentEdited(self):
		return False


#######

AppHelper.runEventLoop()

