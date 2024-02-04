"""sdefparser -- parse an application's sdef, given an application path, file path or XML string. Returns a Dictionary object model. """

# TO DO: find app with missing savo and see how this is represented

# Note: OSACopyScriptingDefinition's aete->sdef conversion has bug where classes and commands defined in hidden 'tpnm' suite aren't included in generated sdef (though enumerations are)

# note: xml.sax bug? parser.getProperty(all_properties), getFeature(all_features) raise an error (2.4)

import  xml.sax, xml.sax.xmlreader
from xml.sax.handler import * #ContentHandler, ErrorHandler, property_xml_string
import struct
from io import BytesIO

from lxml import etree

from aem import kae
import aem.ae

from osaterminology import makeidentifier
from .osadictionary import *


from . import applescripttypes, appscripttypes

######################################################################
# PRIVATE
######################################################################


class HandlerResult:
	result = None
	def _add_(self, item):
		self.result = item


##


class Error(ErrorHandler):
	def error(self, exception): print('error:', exception)
	def fatalError(self, exception): print('fatal:', exception)
	def warning(self, exception): print('warning:', exception)


##

class Handler(ContentHandler):
	
	def __init__(self, parser, path):
		self._visibility = [kVisible] # TO DO
		self._parser = parser
		self._path = path
		self._types = {}
		self._classes = [] # used for cleanup
		self._hiddenname = '' # if dictionary element is hidden, all its sub-elements should be hidden too
		self._isvisible = True
		self._stack = [HandlerResult()]
		self._documentationdepth = 0
		self._suitename = ''
		
	#######
	
	def startElement(self, name, attrs):
		if self._isvisible and attrs.get('hidden') == 'yes': # start of hidden element; all sub-elements will be flagged as hidden too
			self._hiddenname = name # caution: this assumes <NAME> can't be nested inside another <NAME>
			self._isvisible = False
		if self._documentationdepth == 0: # not inside a documentation element, so process normally
			fn = getattr(self, 'start_'+name.replace('-', ''), None)
			if fn:
				o = fn(attrs)
				self._stack.append(o)
			else:
				self._stack.append(Ignored(name))
				
	def endElement(self, name):
		if name == self._hiddenname: # end of hidden element
			self._hiddenname = ''
			self._isvisible = True
		if self._documentationdepth > 0:
			if name == 'documentation':
				self._documentationdepth -= 1
		if self._documentationdepth == 0:
			if name == self._stack[-1].kind:
				o = self._stack.pop()
				if not isinstance(o, Ignored):
					self._stack[-1]._add_(o)
			else:
				print('mismatch on end', name , self._stack[-1].kind)

	##
	
	def start_documentation(self, d): # TO DO: documentation support
		self._documentationdepth += 1
		return Ignored('documentation')


	#######
		
	def asname(self, s):
		return s
	
	def ascode(self, s):
		if len(s) in [4, 8]:
			return s.encode('MacRoman')
		try:
			return struct.pack('L', int(s, 16))
		except:
			return b'????'
	
	def _gettype(self, name):
		name = self.asname(name)
		if name not in self._types:
			self._types[name] = Type(self._visibility, name)
		return self._types[name]
	
	##
	
	def start_dictionary(self, d):
		o = Dictionary(self._visibility, d.get('title', self._path.split('/')[-1] or self._path.split('/')[-2]), self._path) # OSAGetScriptingDefinition doesn't produce valid sdef (missing title) when converting from aete, so compensate here # TO DO: is this still an issue?
		return o
	
	def start_suite(self, d):
		self._suitename = d['name']
		o = Suite(self._visibility, d['name'], self.ascode(d['code']), d.get('description', ''), self._isvisible)
		return o
	
	##
	
	def start_class(self, d):
		t = self._gettype(d['name'])
		t.code = self.ascode(d['code'])
		o = Class(self._visibility, t.name, t.code, 
						d.get('description', ''), self._isvisible, 
						self.asname(d.get('plural', t.name+'s')), self._suitename, t)
		if 'inherits' in d:
			o._add_(self._gettype(d['inherits']))
		self._classes.append(o)
		t._add_(o)
		return o
		
	def start_classextension(self, d):
		t = self._gettype(d['extends']) # assumes class is already defined
		o = Class(self._visibility, t.name, t.code, 
						d.get('description', ''), self._isvisible, 
						self.asname(t.pluralname), self._suitename, t)
		o.kind = 'class-extension'
		o._add_(self._gettype(d['extends']))
		self._classes.append(o)
		t._add_(o)
		return o
		
	
	def start_contents(self, d):
		o = Contents(self._visibility, self.asname(d.get('name', 'contents')),
				self.ascode(d.get('code', b'pcnt')), d.get('description', ''), self._isvisible, d.get('access', 'rw'))
		if 'type' in d:
			o._add_(self._gettype(d['type']))
		return o
	
	def start_property(self, d):
		o = Property(self._visibility, self.asname(d['name']), self.ascode(d['code']),
				d.get('description', ''), self._isvisible, d.get('access', 'rw'))
		if 'type' in d:
			o._add_(self._gettype(d['type']))
		return o
	
	def start_type(self, d): # type elements = alternative to type attribute
		if 'type' in d:
			t = self._gettype(d['type'])
		else:
			t = Type(self._visibility) # kludge where <type list="yes">...</type>
		if d.get('list') == 'yes':
			t = ListOfType(self._visibility, t)
		return t
	
	def start_element(self, d):
		o = Element(self._visibility, self._gettype(d['type']), d.get('description', ''), 
				self._isvisible, d.get('access', 'rw'), self.elementnamesareplural)
		return o
	
	def start_accessor(self, d):
		o = Accessor(self._visibility, d['style'])
		return o
	
	def start_respondsto(self, d):
		o = RespondsTo(self._visibility, self.asname(d.get('command') or d['name']), self._isvisible) # TO DO: command attribute may be command name or id
		return o
	
	##
	
	def start_command(self, d):
		o = Command(self._visibility, self.asname(d['name']), self.ascode(d['code']),
				d.get('description', ''), self._isvisible, self._suitename)
		return o
	
	def start_parameter(self, d):
		o = Parameter(self._visibility, self.asname(d['name']), self.ascode(d['code']),
				 d.get('description', ''), self._isvisible, d.get('optional') == 'yes')
		if 'type' in d:
			o._add_(self._gettype(d['type']))
		return o
	
	def start_directparameter(self, d):
		o = DirectParameter(self._visibility, d.get('description', ''), self._isvisible, d.get('optional') == 'yes')
		if 'type' in d:
			o._add_(self._gettype(d['type']))
		return o
	
	def start_result(self, d):
		o = Result(self._visibility, d.get('description', ''))
		if 'type' in d:
			o._add_(self._gettype(d['type']))
		return o
	
	def start_event(self, d):
		o = Event(self._visibility, self.asname(d['name']), self.ascode(d['code']), 
				d.get('description', ''), self._isvisible)
		return o
	
	##
	
	def start_enumeration(self, d):
		if 'inline' in d:
			inline = int(d['inline'])
		else:
			inline = None
		o = Enumeration(self._visibility, self.asname(d['name']), self.ascode(d['code']),
				d.get('description', ''), self._isvisible, inline, self._suitename)
		t = self._gettype(d['name'])
		t.code = o.code
		t._add_(o)
		return o
	
	def start_enumerator(self, d):
		o = Enumerator(self._visibility, self.asname(d['name']), self.ascode(d['code']),
				d.get('description', ''), self._isvisible)
		return o
	
	def start_recordtype(self, d):
		o = RecordType(self._visibility, self.asname(d['name']), self.ascode(d['code']),
				d.get('description', ''), self._isvisible, self._suitename)
		if 'type' in d:
			o._add_(self._gettype(d['type']))
		t = self._gettype(d['name'])
		t.code = o.code
		t._add_(o)
		return o
	
	def start_valuetype(self, d):
		o = ValueType(self._visibility, self.asname(d['name']), self.ascode(d['code']),
				d.get('description', ''), self._isvisible, self._suitename)
		t = self._gettype(d['name'])
		t.code = o.code
		t._add_(o)
		return o
	
	###
	
	def result(self):	
		# TO DO: fix type names for appscript; add codes for both
		#"""
		# add codes for standard sdef-format types
		#		"""
		# Add codes, etc. for AEM-defined types and enumerations
	#	aemtypesbycode, aemenumerations = self.typemodule.typesandenums()
	#	aemtypes = dict([(v, k) for k, v in aemtypesbycode]) # TO FIX: may use undesireable codes for appscript
	#			if aemtypes.has_key(type.name): # it's an AEM-defined type
	#				type.name = aemtypes[type.code]
			#	elif aemenumerations.has_key(type.code): # it's an AEM-defined enumeration
			#		type._add_(Enumeration('', k, '', True, None))
			#		for name, code in aemenumerations[code]:
			#			type._add_(Enumerator(name, code, '', True))
				# else it's unknown, in which case leave it as-is
	#	for i in self._types.values():
	#		if i.realvalue().kind == 'aem-type':
	#			print i#,'\t\t',i.special
		while len(self._stack) > 1: # bad sdef kludge
			t = self._stack.pop()
			try:
				self._stack[-1]._add_(t)
			except:
				pass
		return self._stack[-1].result

#######
# AppleScript dictionary parser

class AppleScriptHandler(Handler):
	elementnamesareplural = False

#######
# appscript dictionary parser


class AppscriptHandler(Handler):
	elementnamesareplural = True
	applescripttypesbyname = {}
	
	sdeftypesbyname = {
			'any': kae.typeWildCard, 
			'text': kae.typeUnicodeText, 
			'integer': kae.typeInteger, 
			'real': kae.typeFloat, 
			'number': 'nmbr', 
			'boolean': kae.typeBoolean, 
			'specifier': kae.typeObjectSpecifier, 
			'location specifier': kae.typeInsertionLoc,
			'record': kae.typeAERecord, 
			'date': kae.typeLongDateTime,
			'file': b'file', 
			'point': kae.typeQDPoint, 
			'rectangle': kae.typeQDRectangle, 
			'type': kae.typeType}

	# TO DO: expand pseudo-types (start_directparameter, start_parameter, start_result, start_property; c.f. aeteparser, addtypes)
	
	def start_command(self, d):
		# escape any non-standard get/set commands (e.g. InDesign) to avoid conflicts with standard versions
		name, code = d['name'], d['code']
		if (name == 'get' and code != 'coregetd') or (name == 'set' and code != 'coresetd'):
			d = dict(d)	
			d['name'] += '_'
		return Handler.start_command(self, d)
	
	def result(self):
		# convert AppleScript type names to AE codes to appscript type names
		# (note: wouldn't need to do this if appscript used AppleScript-style type names)
		if not self.applescripttypesbyname:
			# since parser has already converted type names to appscript style, need to convert our lookup table as well
			for k, v in applescripttypes.typebyname.items():
				self.applescripttypesbyname[self.asname(k)] = v
		for type in list(self._types.values()):
			if not type.code: # not application-defined
				if type.name in self.sdeftypesbyname:
					type.code = self.sdeftypesbyname[type.name]
				elif type.name in self.applescripttypesbyname:
					type.code = self.applescripttypesbyname[type.name]
				if type.code:
					if type.code in self.appscripttypemodule.typebycode:
						type.name = self.appscripttypemodule.typebycode[type.code]
					else:
						type.name = '' # TO DO: decide
		return Handler.result(self)



class PyAppscriptHandler(AppscriptHandler):
	asname = staticmethod(makeidentifier.getconverter('py-appscript'))
	appscripttypemodule = appscripttypes.typetables('py-appscript')


class RbAppscriptHandler(AppscriptHandler):
	asname = staticmethod(makeidentifier.getconverter('rb-scpt'))
	appscripttypemodule = appscripttypes.typetables('rb-scpt')


class NodeautomationHandler(AppscriptHandler):
	asname = staticmethod(makeidentifier.getconverter('nodeautomation'))
	appscripttypemodule = appscripttypes.typetables('nodeautomation')



handlers = {
		'applescript': AppleScriptHandler,
		'appscript': PyAppscriptHandler,
		'py-appscript': PyAppscriptHandler,
		'rb-scpt': RbAppscriptHandler,
		'nodeautomation': NodeautomationHandler,
}

######################################################################
# PUBLIC
######################################################################


def parsexml(sdef, path='', style='appscript'):
	# quick-n-dirty support for XIncludes, using lxml to merge multiple XML documents into one; TO DO: should really rewite sax-style parser to walk lxml etree
	root = etree.ElementTree(etree.XML(sdef))
	root.xinclude() # resolve any XIncludes, which makes generating glue tables from SDEFs far more complicated and slower than it ought to be as otherwise we could've done it with a simple single-pass SAX parser; no need to build and walk a large DOM; alas the history of AppleScript is full of well-intentioned bad decisions that come back to bite foreverafter
	sdef = etree.tostring(root)
	parser = xml.sax.make_parser()
	handler = handlers[style](parser, path)
	parser.setContentHandler(handler)
	parser.setErrorHandler(Error()) # TO DO: better error reporting/handling
	source = xml.sax.xmlreader.InputSource()
	source.setByteStream(BytesIO(sdef))
	parser.parse(source)
	return parser.getContentHandler().result()

def parsefile(path, style='appscript'):
	with open(path, 'rb') as f:
		sdef = f.read()
	return parsexml(sdef, path, style)

def parseapp(path, style='appscript'):
	sdef = aem.ae.scriptingdefinitionfromurl(aem.ae.convertpathtourl(path, 0))
	return parsexml(sdef, path, style)



