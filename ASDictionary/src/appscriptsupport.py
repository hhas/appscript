"""appscriptsupport -- Provides support for py-/rb-appscript's built-in help system."""

from pprint import pprint, pformat
from io import StringIO
import textwrap

from AppKit import NSUserDefaults
import aem, appscript, aemreceive
from osaterminology.dom import aeteparser
from osaterminology.renderers import textdoc, inheritance, relationships

from rubyrenderer import RubyRenderer


__all__ = ['Help']


######################################################################
# PRIVATE
######################################################################
# Data renderers

class PythonRenderer:
	
	def rendervalue(self, value, prettyprint=False):
		return prettyprint and pformat(value) or repr(value)


############################

class HelpError(Exception):
	pass


############################

class CommandDecorator:
	"""Command decorator; allows help system to display results of individual commands, e.g.
	
		app('Finder').home.get.help('-s')()
	"""

	def __init__(self, ref, helpObj):
		self._ref = ref
		self._helpObj = helpObj
	
	def __repr__(self):
		return repr(self._ref)
	
	def __call__(self, *args, **kargs):
		print('=' * 78, '\nHelp\n\nCommand:', file=self._helpObj.output)
		print(self._ref.AS_formatCommand((args, kargs)), file=self._helpObj.output)
		try:
			res = self._ref(*args, **kargs)
		except Exception as e:
			from traceback import print_exc
			print('\nError:\n', file=self._helpObj.output)
			print_exc(file=self._helpObj.output)
			print('\n' + '=' * 78, file=self._helpObj.output)
			raise
		else:
			print('\nResult:', file=self._helpObj.output)
			pprint(res, self._helpObj.output)
			print('\n' + '=' * 78, file=self._helpObj.output)
			return res
	
	def help(self, *args):
		return self.help(*args)


############################

class ReferenceResolver:
	"""Gets dictionary objects describing the last specifier in a given reference (i.e. definitions for the property/element itself and its containing class).
	"""
	
	def __init__(self, terms):
		self._terms = terms # an osadictionary.Dictionary instance
		try:
			applicationTerms = terms.classes().byname('application')
		except:
			raise HelpError("Can't resolve this reference. " \
					"(Dictionary doesn't define an 'application' class.)")
		self.containingClass = applicationTerms.full()
		self.propertyOrElement = None
	
	def _updateContainingClass(self):
		if self.propertyOrElement:
			classes = self.propertyOrElement.type.realvalues('class')
			if classes:
				self.containingClass = classes[-1].full()
			else:
				raise HelpError("Can't resolve this reference. " \
						"(Can't get properties/elements of %r because it's not a known application class.)" % \
						self.propertyOrElement.type) # TO DO: probably don't want to display diagnostic to user as it's not very helpful to them
	
	def property(self, code):
		self._updateContainingClass()
		try:
			self.propertyOrElement = self.containingClass.properties().bycode(code)
		except KeyError:
			raise HelpError("Can't resolve this reference. " \
					"(%r property isn't listed under the %s class.)" % (code, self.containingClass.name)) # TO DO: ditto
		return self
		
	def elements(self, code):
		self._updateContainingClass()
		try:
			self.propertyOrElement = self.containingClass.elements().bycode(code)
		except KeyError:
			# where a property and element have same name and code, the property will be packed as an all-elements specifier, so if we can't find an element with the desired code in the given class, see if it has a property with that code instead:
			try:
				self.propertyOrElement = self.containingClass.properties().bycode(code)
			except KeyError:
				raise HelpError("Can't resolve this reference. " \
					"(%r element isn't listed under the %s class.)" % (code, self.containingClass.name)) # TO DO: ditto
		return self
		
	def __getattr__(self, *args): # ignore reference forms (first, last, byname, byindex, previous, etc.)
		return self
	
	def __call__(self, *args): # ignore calls to byname, byindex, previous, etc.
		return self


#######

class ReferenceStub:
	AS_aemreference = aem.app
	
	def __bool__(self):
		return False


######################################################################
# PUBLIC
######################################################################

class Help:
	"""Provides built-in help for an application."""
	
	_helpManual = """Help Manual

Print requested information on application and/or current reference. 

Syntax:

    reference.help(flags)

The optional flags argument is a string containing one or more of the following:

    -h -- show this help
    -o -- overview of all suites, classes and commands
    -k -- list all built-in keywords (type names)
    -u [suite-name] -- summary of named suite or all suites
    -t [class-or-command-name] -- terminology for named class/command or current reference/command
    -i [class-name] -- inheritance tree for named class or all classes
    -r [class-name] -- one-to-one and one-to-many relationships for named class or current reference
    -s [property-or-element-name] -- values of properties and elements of object(s) currently referenced

    Values shown in brackets are optional.

Notes: 
    - If no flags argument is given, '-t' is used.

    - When the -i option is used on a specific class that has multiple inheritance, this will be represented by multiple graphs. When the -i option is used for all classes, classes with multiple inheritance will appear at multiple points in the graph. In both cases, the class's subclasses will appear once in full, then abbreviated for space thereafter.

    - The -s option may take time to process if there are many properties and/or elements to get.

    - When the -t option is used, one-to-one relationships are shown as '-NAME', one-to-many as '=NAME'; a property's class is shown in angle brackets; a trailing arrow, '->', indicates a class's relationships are already given elsewhere.

For example, to print an overview of TextEdit, a description of its make command and the inheritance tree for its document class:

    app('TextEdit.app').help('-o -t make -i document')"""
	
	# TO DO: osax support
	
	def __init__(self, appobj, style='py-appscript', out=StringIO()):
		"""
			aetes : list of AEDesc -- list of aetes
			out : anything -- any file-like object that implements a write(str) method
		"""
		aetes = appscript.terminology.aetesforapp(appobj.AS_appdata.target())
		appname = appobj.AS_appdata.identifier or 'Current Application'
		self.terms = aeteparser.parseaetes(
				aetes, appname, style)
		self.style = style
		if style == 'rb-scpt':
			self.datarenderer = RubyRenderer(appobj, aetes)
		else:
			self.datarenderer = PythonRenderer()
		self.output = out
	
	def overview(self):
		print('Overview:\n', file=self.output)
		textdoc.IndexRenderer(
				style=self.style, options=['sort', 'collapse'], out=self.output).draw(self.terms)
	
	def suite(self, suiteName=''):
		if suiteName:
			if not self.terms.suites().exists(suiteName):
				raise HelpError('No information available for suite %r.' % suiteName)
			s = 'Summary of %s'
			if not suiteName.lower().endswith('suite'):
				s += ' suite'
			terms = self.terms.suites().byname(suiteName)
			print((s + ':\n') % terms.name, file=self.output)
		else:
			print('Summary of all suites:\n', file=self.output)
			terms = self.terms
		textdoc.SummaryRenderer(
				style=self.style, out=self.output).draw(terms)
	
	def keywords(self):
		print('Built-in keywords (type names):\n', file=self.output)
		if self.style == 'applescript':
			from osaterminology.dom import applescripttypes
			typenames = list(applescripttypes.typebyname.keys())
		else:
			from osaterminology.dom import appscripttypes
			formatter = {'appscript': 'k.%s', 'py-appscript': 'k.%s', 'rb-scpt': ':%s'}[self.style]
			typenames = [formatter % name for name in list(appscripttypes.typetables(self.style).typebycode.values())]
		typenames.sort(key=lambda s: s.lower())
		for name in typenames:
			print('    %s' % name, file=self.output)
		
		
	def command(self, name):
		command = self.terms.commands().byname(name)
		s = StringIO()
		print('Terminology for %s command\n\nCommand:' % command.name, end=' ', file=s)
		textdoc.FullRenderer(
				style=self.style, options=['full'], out=s).draw(command)
		print(s.getvalue(), file=self.output)
	
	
	def klass(self, name):
		klass = self.terms.classes().byname(name).full()
		s = StringIO()
		print('Terminology for %s class\n\nClass:' % klass.name, end=' ', file=s)
		textdoc.FullRenderer(
				style=self.style, options=['full'], out=s).draw(klass)
		print(s.getvalue(), file=self.output)
	
	
	def property(self, p):
		s = StringIO()
		print('Property:', end=' ', file=s)
		textdoc.FullRenderer(
				style=self.style, options=['full'], out=s).draw(p)
		print(s.getvalue(), file=self.output)
	
	def element(self, e):
		s = StringIO()
		print('Element:', end=' ', file=s)
		textdoc.FullRenderer(
				style=self.style, options=['full'], out=s).draw(e)
		print(s.getvalue(), file=self.output)
	
	
	def inheritance(self, className=''):
		if className:
			if not self.terms.classes().exists(className):
				raise HelpError('No information available for class %r.' % className)
			print('Inheritance for %s class\n' % className, file=self.output)
		else:
			print('Inheritance for all classes:\n', file=self.output)
		inheritance.InheritanceGrapher(self.terms,
				inheritance.TextRenderer(self.output)).draw(className)
		print(file=self.output)


	def relationships(self, ref, className=''):
		if className:
			if not self.terms.classes().exists(className):
				raise HelpError('No information available for class %r.' % className)
			print('Relationships for %s class\n' % className, file=self.output)
		else:
			definition = self._resolveRef(ref).propertyOrElement
			if definition:
				print('Relationships for %s\n' % definition.name, file=self.output)
				if definition:
					value = definition.type.realvalue()
					if value.kind == 'class': # if target's value is application object, not data, print class description
						className = value.name
			else:
				print('Relationships for application class\n', file=self.output)
				className = 'application'
		relationships.RelationshipGrapher(self.terms, 
				relationships.TextRenderer(self.output)).draw(className, 2)
		print(file=self.output)

	
	#######
	
	def _resolveRef(self, ref):
		resolver = ReferenceResolver(self.terms)
		ref.AS_aemreference.AEM_resolve(resolver)
		return resolver
	
	
	def _terminologyForClassOrCommand(self, ref, name=None):
		if name:
			if self.terms.commands().exists(name):
				self.command(name)
			elif self.terms.classes().exists(name):
				self.klass(name)
			else:
				raise HelpError('No information available for class/command %r.' % name)
		else:
			print('Description of reference\n', file=self.output)
			if isinstance(ref, appscript.reference.Command):
				self.command(ref.AS_name)
			else:
				definition = self._resolveRef(ref).propertyOrElement
				if definition:
					if definition.kind == 'property': # print description of target property/element
						self.property(definition)
					else:
						self.element(definition)
					print(file=self.output)
					value = definition.type.realvalue()
					if value.kind == 'class': # if target's value is application object, not data, print class description
						self.klass(value.name)
				else: # must be top-level application object
					self.klass('application')
	
	
	##
	
	def _printRefValue(self, ref):
			try:
				print(self.datarenderer.rendervalue(ref.get(), True), file=self.output)
			except Exception as e:
				print('UNAVAILABLE', file=self.output)
	
	
	def _stateForRef(self, ref, attr=None):
		if isinstance(ref, appscript.reference.Command):
			print("Command's state will be displayed when called.", file=self.output)
			return CommandDecorator
		else: # it's a reference
			if attr: # print current state of selected property/element only
				print('Current state of selected property/element of referenced object(s)\n\n%s:' % attr, file=self.output)
				self._printRefValue(getattr(ref, attr))
			else: # print current state of all properties and elements
				resolver = self._resolveRef(ref)
				definition = resolver.propertyOrElement
				if definition is None: # help() was called on application object
					value = resolver.containingClass
				else:
					value = definition.type.realvalue()
				if value.kind == 'class':
					print('Current state of referenced object(s)', file=self.output)
					if definition:
						print('\n--- Get reference ---\n\n', self.datarenderer.rendervalue(ref.get()), file=self.output)
					for heading, attributeNames in [
							('---- Properties ----', value.full().properties().names()),
							('----- Elements -----', value.full().elements().names())]:
						print('\n%s' % heading, file=self.output)
						for name in attributeNames:
							print('\n%s:' % name, file=self.output)
							if name == 'entire_contents':
								print('UNAVAILABLE', file=self.output)
							else:
								try:
									print(self.datarenderer.rendervalue(getattr(ref, name).get(), True), file=self.output)
								except Exception as e:
									print('UNAVAILABLE', file=self.output)
				else:
					print('Current state of referenced property (or properties)\n\n%s:' % \
							definition.name, file=self.output)
					self._printRefValue(ref)
	
	
	#######
	
	def _manual(self):
		print(self._helpManual, file=self.output)

	##
	
	_handlers = {
			# (requires reference?, takes no/optional/required argument?, function)
			'h':(False, False, _manual),
			'o':(False, False, overview),
			'r':(True, True, relationships),
			'i':(False, True, inheritance),
			's':(True, True, _stateForRef),
			't':(True, True, _terminologyForClassOrCommand),
			'k':(False, False, keywords),
			'u':(False, True, suite),
			}



	def help(self, flags, ref=ReferenceStub()): # main call
		result = ref
		if not isinstance(flags, str): # assume flags arg contains file/StringIO/etc. object to write help to
			self.output = flags
		else:
			tokens = flags.split()
			print('=' * 78 + '\nHelp (%s)' % ' '.join(tokens), file=self.output)
			if ref:
				print('\nReference: %s' % self.datarenderer.rendervalue(ref), file=self.output)
			i = 0
			while i < len(tokens):
				print('\n' + '-' * 78, file=self.output)
				token = tokens[i]
				try:
					requiresRef, optArg, fn = self._handlers[token[1:]]
				except KeyError:
					print('Unknown option: %r\n' % token, file=self.output)
				else:
					args = []
					if requiresRef:
						args.append(ref)
					if optArg:
						word = []
						while i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
							i += 1
							word.append(tokens[i])
						if word:
							args.append(' '.join(word))
					try:
						wrapper = fn(self, *args)
					except HelpError as e:
						print(e, file=self.output)
					except Exception as e:
						from traceback import print_exc
						print_exc()
						print('%s: %s' % (e.__class__.__name__, e), file=self.output)
					else:
						if wrapper:
							result = wrapper(ref, self) # add wrapper
				i += 1
			print('\n' + '=' * 78, file=self.output)
		return result


#######
# Install event handler

_cache = {}

def help(constructor, identity, style, flags, aemreference, commandname=''):
	id = (constructor, identity, style)
	if id not in _cache:
		if constructor == 'path':
			appobj = appscript.app(identity)
		elif constructor == 'pid':
			appobj = appscript.app(pid=identity)
		elif constructor == 'url':
			appobj = appscript.app(url=identity)
		elif constructor == 'aemapp':
			appobj = appscript.app(aemapp=aem.Application(desc=identity))
		elif constructor == 'current':
			appobj = appscript.app()
		else:
			raise RuntimeError('Unknown constructor: %r' % constructor)
		output = StringIO()		
		helpobj = Help(appobj, style, output)
		_cache[id] = (appobj, helpobj, output)
	ref, helpobj, output = _cache[id]
	output.truncate(0)
	if aemreference is not None:
		ref = ref.AS_newreference(aemreference)
	if commandname:
		ref = getattr(ref, commandname)
	helpobj.help(flags, ref)
	s = output.getvalue()
	if NSUserDefaults.standardUserDefaults().boolForKey_('enableLineWrap'):
		res = []
		textwrapper = textwrap.TextWrapper(width=NSUserDefaults.standardUserDefaults().integerForKey_('lineWrap'), 
				subsequent_indent=' ' * 12)
		for line in s.split('\n'):
			res.append(textwrapper.fill(line))
		s = '\n'.join(res)
	return s




def init():
	if not NSUserDefaults.standardUserDefaults().integerForKey_('lineWrap'):
		NSUserDefaults.standardUserDefaults().setInteger_forKey_(78, 'lineWrap')

	aemreceive.installeventhandler(help,
			b'AppSHelp',
			(b'Cons', 'constructor', aem.kae.typeChar),
			(b'Iden', 'identity', aem.kae.typeWildCard),
			(b'Styl', 'style', aem.kae.typeChar),
			(b'Flag', 'flags', aem.kae.typeChar),
			(b'aRef', 'aemreference', aem.kae.typeWildCard),
			(b'CNam', 'commandname', aem.kae.typeChar)
			)
