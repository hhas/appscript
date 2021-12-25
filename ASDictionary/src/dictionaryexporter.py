""" dictionaryexporter -- Dictionary export function and corresponding Apple event handler. """

import os

from AppKit import *

from aem import *
from aemreceive import *
from osaterminology import makeidentifier
from osaterminology.dom import aeteparser, sdefparser
from osaterminology.renderers import quickdoc, htmldoc, htmldoc2


######################################################################
# PRIVATE
######################################################################


kStyleToSuffix = {
		'applescript': '-AS',
		'py-appscript': '-py', 
		'rb-scpt': '-rb', 
}


def _makeDestinationFolder(outFolder, styleSubfolderName, formatSubfolderName, fileName):
	destFolder = os.path.join(outFolder, styleSubfolderName, formatSubfolderName or '')
	if not os.path.exists(destFolder):
		os.makedirs(destFolder)
	return os.path.join(destFolder, fileName)


######################################################################
# define handler for 'export dictionaries' events # TO DO: junk this?

kPlainText = b'PTex'
kSingleHTML = b'SHTM'
kFrameHTML = b'FHTM'
kASStyle = b'AScr'
kPyStyle = b'PyAp'
kRbStyle = b'RbAp'

kAECodeToStyle = {
	kASStyle: 'applescript',
	kPyStyle: 'py-appscript',
	kRbStyle: 'rb-scpt',
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


def handle_exportdictionaries(sources, outfolder, 
		fileformats=[AEEnum(kFrameHTML)], styles=[AEEnum(kASStyle)],
		compactclasses=False, showinvisibles=False, usesubfolders=False):
	items = []
	for alias in sources:
		name = os.path.splitext(os.path.basename(alias.path.rstrip('/')))[0]
		items.append({
			'name': name, 
			'path': alias.path,
			})
	outfolder = outfolder.path
	plaintext = AEEnum(kPlainText) in fileformats
	singlehtml = AEEnum(kSingleHTML) in fileformats
	framehtml = AEEnum(kFrameHTML) in fileformats
	styles = [kAECodeToStyle[o.code] for o in styles]
	options = []
	if compactclasses:
		options.append('collapse')
	if showinvisibles:
		options.append('full')
	progressobj = AEProgress(len(items), len(styles), len(fileformats), None)
	return export(items, styles, plaintext, singlehtml, framehtml, options, outfolder, usesubfolders, progressobj)


######################################################################
# PUBLIC
######################################################################


def export(items, styles, plainText, singleHTML, frameHTML, options, outFolder, exportToSubfolders, progress):
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
				if plainText:
					raise NotImplementedError("TO DO: rework quickdoc to use SDEF")
					outputPath = _makeDestinationFolder(outFolder, styleSubfolderName, 
							exportToSubfolders and 'text', name + suffix + '.txt')
					progress.nextoutput('%s' % outputPath)
					with open(outputPath, 'w', encoding='utf-8') as f:
						f.write('\uFEFF') # UTF8 BOM
						quickdoc.renderaetes(aetes, f, makeidentifier.getconverter(style))
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


#######


def init():
	installeventhandler(handle_exportdictionaries, b'ASDiExpD',
			(b'----', 'sources', ArgListOf(kae.typeAlias)),
			(b'ToFo', 'outfolder', kae.typeAlias),
			(b'Form', 'fileformats', ArgListOf(ArgEnum(kPlainText, kSingleHTML, kFrameHTML))),
			(b'Styl', 'styles', ArgListOf(ArgEnum(kASStyle, kPyStyle, kRbStyle))),
			(b'ClaC', 'compactclasses', kae.typeBoolean),
			(b'SInv', 'showinvisibles', kae.typeBoolean),
			(b'SubF', 'usesubfolders', kae.typeBoolean))
