""" dictionaryexporter -- Dictionary export function and corresponding Apple event handler. """

import os

from AppKit import *

from aem import *
from aemreceive import *
from osaterminology import makeidentifier
from osaterminology.dom import aeteparser, sdefparser
from osaterminology.renderers import htmldoc, htmldoc2


######################################################################
# PRIVATE
######################################################################


kStyleToSuffix = {
		'applescript': '-AS',
		'py-appscript': '-py', 
		'rb-scpt': '-rb', 
		'nodeautomation': '-node',
}


def _makeDestinationFolder(outFolder, styleSubfolderName, formatSubfolderName, fileName):
	destFolder = os.path.join(outFolder, styleSubfolderName, formatSubfolderName or '')
	if not os.path.exists(destFolder):
		os.makedirs(destFolder)
	return os.path.join(destFolder, fileName)


######################################################################
# define handler for 'export dictionaries' events # TO DO: junk this?

kSingleHTML = b'SHTM'
kFrameHTML = b'FHTM'
kASStyle = b'AScr'
kPyStyle = b'PyAp'
kRbStyle = b'RbAp'
kNodeStyle = b'NoAp'

kAECodeToStyle = {
	kASStyle: 'applescript',
	kPyStyle: 'py-appscript',
	kRbStyle: 'rb-scpt',
	kNodeStyle: 'nodeautomation',
}

class AEProgress:

	kClassKey = AEType(b'pcls')
	kClassValue = AEType(b'ExpR')
	#kNameKey = AEType(b'pnam')
	kSuccessKey = AEType(b'Succ')
	kSourceKey = AEType(b'Sour')
	kDestKey = AEType(b'Dest')
	kErrorKey = AEType(b'ErrS')
	kMissingValue = AEType(b'msng')

	def __init__(self, itemcount, stylecount, formatcount, controller):
		self._results = []

	def shouldcontinue(self):
		return True
		
	def nextitem(self, name, inpath):
		self._results.append({
				self.kClassKey:self.kClassValue,
				#self.kNameKey:name, 
				self.kSourceKey:mactypes.File(inpath)})
	
	def nextoutput(self, outpath):
		self._results[-1][self.kDestKey] = mactypes.File(outpath)
		
	def didsucceed(self):
		self._results[-1][self.kSuccessKey] = True
		self._results[-1][self.kErrorKey] = self.kMissingValue
		
	def didfail(self, errormessage):
		self._results[-1][self.kSuccessKey] = False
		self._results[-1][self.kDestKey] = self.kMissingValue
		self._results[-1][self.kErrorKey] = errormessage
	
	def didfinish(self):
		return self._results


######################################################################
# PUBLIC
######################################################################


def export(items, styles, singleHTML, frameHTML, options, outFolder, exportToSubfolders, progress):
	styleInfo = [(style, kStyleToSuffix[style]) for style in styles]
	# process each item
	for i, item in enumerate(items):
		sdef = aetes = None
		name, path = item['name'], item['path']
		if path == NSBundle.mainBundle().bundlePath():
			continue
		progress.nextitem(name, path)
		try:
			sdef = ae.scriptingdefinitionfromurl(ae.convertpathtourl(path, 0))
		except Exception as e:
			progress.didfail("Can't get terminology for application (%r): %s" % (path, e))
			continue
		try:
			if not sdef:
				progress.didfail("No terminology found.")
				continue
			for style, suffix in styleInfo:
				styleSubfolderName = exportToSubfolders and style or ''
				if not progress.shouldcontinue():
					for item in items[i:]:
						progress.didfail("User cancelled.")
						progress.nextapp(item['name'], item['path'])
					progress.didfail("User cancelled.")
					progress.didfinish()
					return
				if singleHTML or frameHTML:
					terms = sdefparser.parsexml(sdef, path, style)
					if singleHTML:
						outputPath = _makeDestinationFolder(outFolder, styleSubfolderName, 
								exportToSubfolders and 'html', name + suffix + '.html')
						progress.nextoutput('%s' % outputPath)
						html = htmldoc.renderdictionary(terms, style, options)
						with open(outputPath, 'w', encoding='utf-8') as f:
							f.write(str(html))
					if frameHTML:
						outputPath = _makeDestinationFolder(outFolder, styleSubfolderName, 
								exportToSubfolders and 'frame-html', name + suffix)
						progress.nextoutput('%s' % outputPath)
						htmldoc2.renderdictionary(terms, outputPath, style, options)
		except Exception as err:
			from traceback import format_exc
			progress.didfail('Unexpected error:/n%s' % format_exc())
		else:
			progress.didsucceed()
	return progress.didfinish()

