"""typerenderers"""

from osaterminology.dom.osadictionary import kAll, Nodes

from codecs import getencoder

strtohex = getencoder('hex_codec')


######################################################################


class TypeRendererBase:

	def __init__(self):
		self._renderedtypes = {} # cache
	
	def render(self, types, sep=' | '): # TO DO: rename (typeorenum? typename?) 
#		oldvis = types.setvisibility(kAll) # TO DO: find right place for these calls
		res = []
		if not isinstance(types, (list, Nodes)):
			types = [types]
		for otype in types:
			type = otype.realvalue() # TO DO: this might throw up weird results if there's a mix (not that there should be if the dictionary is properly designed...)
			if type.code:
				if type.code not in self._renderedtypes:
					self._renderedtypes[type.code] = self._render(type)
				s = self._renderedtypes[type.code]
			else:
				s = type.name
			if otype.islist:
				s = 'list of '+s
			res.append(s)
#		types.setvisibility(oldvis)
		return sep.join(res)


######################################################################


class AppscriptTypeRenderer(TypeRendererBase):
	
	def _render(self, type):
		if type.kind == 'enumeration':
			return ' / '.join([e.name and self._keyword % e.name or self._enum % self.escapecode(e.code) 
					for e in type.enumerators()])
		else:
			return type.name or self._type % self.escapecode(type.code)
	
	def escapecode(self, s): # TO DO: how is s arg represented?
		# format non-ASCII characters as '\x00' hex values for readability (also backslash and single and double quotes)
		if isinstance(s, bytes): s = str(s, 'macroman')
		res = ''
		for c in s:
			n = ord(c)
			if 31 < n < 128 and c not in '\\\'"':
				res += c
			else:
				res += '\\x%02x' % n
		return res
	
	def elementname(self, type): # appscript uses plural names for elements
		type = type.realvalue()
		return getattr(type, 'pluralname', type.name) or self._render(type)


class PyAppscriptTypeRenderer(AppscriptTypeRenderer):
	_type = 'AEType(%r)'
	_enum = 'AEEnum(%r)'
	_keyword = 'k.%s'


class RbAppscriptTypeRenderer(AppscriptTypeRenderer):
	_type = 'AEType.new("%s")'
	_enum = 'AEEnum.new("%s")'
	_keyword = ':%s'


class NodeAutomationTypeRenderer(TypeRendererBase):
	_type = 'k.fromTypeCode(%s)'
	_enum = 'k.fromEnumCode(%s)'
	_keyword = 'k.%s'
	
	def _render(self, type):
		if type.kind == 'enumeration':
			return ' / '.join([e.name and self._keyword % e.name or self._enum % self.escapecode(e.code) 
					for e in type.enumerators()])
		else:
			return type.name or self._type % self.escapecode(type.code)
	
	def escapecode(self, s):
		if isinstance(s, bytes): s = str(s, 'macroman')
		res = ''
		for c in s:
			n = ord(c)
			if 31 < n < 128 and c not in '\\\'"':
				res += c
			else:
				n = 0
				for c in s[::-1]:
					n *= 256
					n += ord(c)
				return '0x{:08x}'.format(n)
		return "'#{}'".format(res)
	
	def elementname(self, type): # appscript uses plural names for elements
		type = type.realvalue()
		return getattr(type, 'pluralname', type.name) or self._render(type)


######################################################################


class ApplescriptTypeRenderer(TypeRendererBase):
		
	def _render(self, type):
		if type.kind == 'enumeration':
			return ' / '.join([e.name or '<constant ****%s>' % self.escapecode(e.code) 
					for e in type.enumerators()])
		else:
			return type.name or '<class %s>' % self.escapecode(type.code)
	
	def escapecode(self, s):
		return str(s, 'macroman')
	
	def elementname(self, type): # AppleScript uses singular names for elements
		return self._render(type.realvalue())


######################################################################

typerenderers = {
	'applescript': ApplescriptTypeRenderer,
	'appscript': PyAppscriptTypeRenderer,
	'py-appscript': PyAppscriptTypeRenderer,
	'rb-scpt': RbAppscriptTypeRenderer,
	'nodeautomation': NodeAutomationTypeRenderer,
	}

######################################################################


def gettyperenderer(name):
	try:
		return typerenderers[name]()
	except KeyError:
		raise KeyError("Couldn't find a type renderer named %r." % name)

