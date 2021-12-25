"""htmldoc - Render application terminology as a single XHTML document."""

from htmltemplate import Template

from aem import findapp
from osaterminology.dom import osadictionary
from osaterminology.dom import aeteparser
from .typerenderers import gettyperenderer

#__all__ = ['renderdictionary', 'doc']

######################################################################
# PRIVATE - Template HTML
######################################################################

_html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"><head>

<title node="con:title">Foo.app terminology</title>

<style type="text/css" media="all">
	h1 {padding-bottom:2px; border-bottom:solid 2px black; margin:0;}
	h1+p {font-weight:bold; font-size:0.8em; margin-top:1px;}
	h2 {margin-top:0;}
	#content {padding-right:8px;}
	#content > ul > li {margin-bottom:1em;}
	#sidebar h2 {font-size:1em;}
	#sidebar ul {padding-left:0; margin-left:1.2em;}
	#sidebar li {font-size:0.8em; white-space:nowrap;}
	#sidebar .box {padding-left:8px; border-left:dashed 1px black;}
	li {list-style-type:none;}
	a {color:#000; text-decoration:none;}
	a {border-bottom:dotted 1px black;}
	a:hover {border-bottom:solid 1px black;}
</style>
<style type="text/css" media="screen">
	h2 span, h3 span {font-family:Courier; font-size:12px;}
</style>
<style type="text/css" media="print">
	body {font-size:10pt;}
	h1 {font-size:24pt;}
	h2 {font-size:18pt;}
	h3 {font-size:14pt;}
	#sidebar {display:none;}
</style>

</head><body>

<h1 node="con:heading">Foo.app terminology</h1>

<p node="con:path">/Applications/Foo.app</p>

<table>
<tr>
<td id="content" valign="top" width="90%">
	<div node="-rep:suite">
		<a node="con:anchor" name="" id=""></a>
		<h2 node="con:name">Standard Suite</h2>

		<p node="con:desc">Common classes and commands for most applications.</p>
		
		
		<div node="-con:commands">
			<h3>Commands</h3>
			<ul>
				<li node="rep:command">
					<a node="con:anchor" name=""></a>
					<strong node="con:name">some command</strong>
					<span node="-con:desc"> -- some description</span>
					<ul>
						<li node="con:directarg">
							<span node="-con:name">[xxxx]</span>
							<span node="-con:desc"> -- some description</span>
						</li>
						<li node="rep:arg">
							<span node="-con:name">[some param]</span>
							<span node="-con:desc"> -- some description</span>
						</li>
						<li node="con:reply">
							Result: <em node="con:type">thing</em>
							<span node="-con:desc"> -- the reply for the command</span>
						</li>
					</ul>
				</li>
			</ul>
		</div>
		
		
		<div node="-con:classes">
			<h3>Classes</h3>
			<ul>
				<li node="rep:klass">
					<a node="con:anchor" name=""></a>
					<strong node="con:name">some class</strong>
					<span node="-con:desc"> -- See <a node="con:redirectclass">bar</a> in <a href="" node="con:redirectsuite">Foo Suite</a>.</span>
					<ul node="con:attributes">
						<li node="con:plural">Plural name:
							<ul>
								<li node="con:name"><em>plural name</em></li>
							</ul>
						</li>
						<li node="con:parent">Inherits from:
							<ul>
								<li node="rep:parentName"><em><a href="" node="con:link">some class</a></em></li>
							</ul>
						</li>
						<li node="con:children">Inherited by:
							<ul>
								<li node="rep:childName"><em><a href="" node="con:link">some class</a></em></li>
							</ul>
						</li>
						<li node="con:properties">Properties:
							<ul>
								<li node="rep:property">
									<strong node="con:name">some property</strong>
									<span node="-con:access">(r/o)</span>
									<em node="con:type">some type</em>
									<span node="-con:desc"> -- some description</span>
								</li>
							</ul>
						</li>
						<li node="con:elements">Elements:
							<ul>
								<li node="rep:element">
									<strong><a href="" node="con:name">some class</a></strong> -- by
									<em node="con:desc">name, index, relative position, range, filter, ID</em>
								</li>
							</ul>
						</li>
					</ul>
				</li>
			</ul>
		</div>
		
	</div>
</td>

<td id="sidebar" valign="top">
<div class="box">
	<h2>Suites</h2>
	<ul>
		<li node="rep:sideSuite"><a node="con:link" href="">some suite</a></li>
	</ul>
	<h2>Commands</h2>
	<ul>
		<li node="rep:sideCommand"><a node="con:link" href="">some command</a></li>
	</ul>
	<h2>Classes</h2>
	<ul>
		<li node="rep:sideClass"><a node="con:link" href="">some class</a></li>
	</ul>
</div>
</td>
</tr>
</table>
</body></html>"""


######################################################################
# PRIVATE - Template Controller
######################################################################

# Helper functions

def esc(str):
	return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def formatDescription(desc): 
	return desc and ' -- ' + desc or ''

_stripCache = {}

def stripNonChars(txt):
	if txt not in _stripCache:
		_stripCache[txt] = ''.join([char for char in txt.replace(' ', '_') if char in 
				'abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789'])
	return _stripCache[txt]

def formatType(types, typeRenderer):
	result = []
	for type in types:
		res = ''
		if type.islist: # render 'list of' bit outside the link
			res += 'list of '
			type = type.type
		classes = type.realvalues('class')
		if classes:
			klass = classes[-1]
			res += '<a href="#class_%s">%s</a>' % (stripNonChars(klass.name + '__' + klass.suitename), esc(typeRenderer.render(type)))
		else:
			enums = type.realvalues('enumeration')
			if enums:
				enum = enums[-1]
				res += esc(typeRenderer.render(enum))
			else:
				res += esc(typeRenderer.render(type)) # missing class/enum definition, so will be rendered as raw AE code or whatever else is left
		result.append(res)
	return ' | '.join(result)

#

def encodeNonASCII(txt):
	"""Convert non-ASCII characters to HTML entities"""
	res = []
	for char in txt:
		if ord(char) < 128:
			res.append(char)
		else:
			res.append('&#%i;' % ord(char))
	return ''.join(res)


#######
# Rendering callbacks

def renderTemplate(node, terms, typeRenderer, options):
	collapseClasses = 'collapse' in options
	# render heading
	node.title.text = node.heading.text = terms.name + ' terminology'
	node.path.text = terms.path
	# build table listing subclasses for each class
	children = {}
	for klass in terms.classes():
		for parent in klass.parents():
			if parent.name not in children:
				children[parent.name] = []
			children[parent.name].append(klass)
	# TO DO: contained by
	# render main content
	node.suite.repeat(renderSuite, terms.suites(), children, terms, typeRenderer, collapseClasses)
	# render side nav (items sorted by name)
	node.sideSuite.repeat(renderSideSuite, terms.suites())
	commands = [(o.name, o.suitename) for o in terms.commands()]
	classes = [(o.name, o.suitename) for o in terms.classes()]
	for lst in [commands, classes]:
		lst.sort(key=lambda s: s[0].lower())
	node.sideCommand.repeat(renderSideCommand, commands)
	node.sideClass.repeat(renderSideClass, classes)


def renderSuite(node, suite, children, terms, typeRenderer, collapseClasses):
	node.anchor.atts['name'] = node.anchor.atts['id'] = 'suite_' + stripNonChars(suite.name)
	node.name.text = suite.name
	node.desc.text = suite.description
	commands = suite.commands()
	classes = suite.classes()
	if commands:
		node.commands.command.repeat(renderCommand, commands, terms, typeRenderer)
	else:
		node.commands.omit()
	if classes:
		node.classes.klass.repeat(renderClass, classes, children, terms, typeRenderer, collapseClasses)
	else:
		node.classes.omit()

##

def renderCommand(node, command, terms, typeRenderer):
	# Render name and description.
	node.anchor.atts['name'] = 'command_' + stripNonChars(command.name + '__' + command.suitename)
	directarg = command.directparameter
	node.name.text = command.name
	node.desc.text = formatDescription(command.description)
	# Render direct arg, if any.
	if directarg:
		s = '<em>%s</em>' % formatType(directarg.types, typeRenderer)
		if directarg.optional:
			s = '[' + s + ']'
		node.directarg.name.html = s
		node.directarg.desc.text = formatDescription(directarg.description)
	else:
		node.directarg.omit()
	# Render labelled args, if any.
	node.arg.repeat(renderArg, command.parameters, terms, typeRenderer)
	# Render reply, if any.
	reply = command.result
	if reply:
		node.reply.type.html = formatType(reply.types, typeRenderer)
		node.reply.desc.text = formatDescription(reply.description)
	else:
		node.reply.omit()

def renderArg(node, arg, terms, typeRenderer):
	s = '<strong>%s</strong> <em>%s</em>' % (esc(arg.name), formatType(arg.types, typeRenderer))
	if arg.optional:
		s = '[' + s + ']'
	node.name.html = s
	node.desc.text = formatDescription(arg.description)
	
##

def renderClass(node, klass, children, terms, typeRenderer, collapseClasses):
	node.anchor.atts['name'] = 'class_' + stripNonChars(klass.name + '__' + klass.suitename)
	node.name.text = klass.name
	if collapseClasses and klass.isoverlapped(): # collapse
		actualClass = klass.classes()[-1]
		suiteName = actualClass.suitename
		node.desc.redirectclass.atts['href'] = '#class_' + stripNonChars(actualClass.name + '__' + suiteName) # extra wiggle when getting overlapping class's name in case code matches but name doesn't (e.g. Omnigraffle 4's 'attachment' + 'text attachment' classes)
		node.desc.redirectsuite.atts['href'] = '#suite_' + stripNonChars(suiteName)
	#	if not suiteName.lower().endswith('suite'):
	#		suiteName += ' suite'
		node.desc.redirectclass.text = actualClass.name
		node.desc.redirectsuite.text = suiteName
		node.attributes.omit()
	else:
		# TO DO: children info should be supplied by osadictionary
		children = children.get(klass.name)
		if children and klass in children:
			children = children[:]
			for o in klass.classes()[:klass.classes().index(klass)+1]:
				if o in children:
					children.remove(o)
		if collapseClasses:
			klass = klass.collapse()
		if klass.pluralname == klass.name:
			node.attributes.plural.omit()
		else:
			node.attributes.plural.name.text = klass.pluralname
		node.desc.text = formatDescription(klass.description)
		properties = klass.properties()
		elements = klass.elements()
		parents = klass.parents()
		if properties or elements or children or parents:
			if properties:
				node.attributes.properties.property.repeat(renderProperty, properties, terms, typeRenderer)
			else:
				node.attributes.properties.omit()
			if elements:
				node.attributes.elements.element.repeat(renderElement, elements, terms, typeRenderer)
			else:
				node.attributes.elements.omit()
			if children:
				node.attributes.children.childName.repeat(renderParentOrChild, children, terms, typeRenderer)
			else:
				node.attributes.children.omit()
			if parents:
				node.attributes.parent.parentName.repeat(renderParentOrChild, parents, terms, typeRenderer)
			else:
				node.attributes.parent.omit()
		else:
			node.attributes.omit()

def renderProperty(node, property, terms, typeRenderer):
	if property.access =='rw':
		node.access.omit()
	else:
		node.access.text = {'r': '(r/o)', 'w': '(w/o)'}[property.access]
	node.name.text = property.name
	node.type.html = formatType(property.types, typeRenderer)
	node.desc.text = formatDescription(property.description)

def renderElement(node, element, terms, typeRenderer):
	node.name.text = typeRenderer.elementname(element.type)
	node.desc.text = ', '.join(element.accessors())
	if element.type.name:
		classes = element.type.realvalues('class')
		if classes:
			klass = classes[-1]
			node.name.atts['href'] = '#class_' + stripNonChars(klass.name + '__' + klass.suitename)
		else:
			node.name.omittags()
	else:# some apps, e.g. GraphicConverter, define incomplete terminology
		node.name.omittags()


def renderParentOrChild(node, o, terms, typeRenderer):
	if o.kind == 'class':
		node.link.atts['href'] = '#class_' + stripNonChars(o.name + '__' + o.suitename)
	else:
		node.link.omittags()
	node.link.text = o.name # unfinished?

##

def renderSideSuite(node, suite):
	node.link.atts['href'] = '#suite_' + stripNonChars(suite.name)
	node.link.text = suite.name

def renderSideCommand(node, xxx_todo_changeme):
	(name, suiteName) = xxx_todo_changeme
	node.link.atts['href'] = '#command_' + stripNonChars(name + '__' + suiteName)
	node.link.text = name

def renderSideClass(node, xxx_todo_changeme1):
	(name, suiteName) = xxx_todo_changeme1
	node.link.atts['href'] = '#class_' + stripNonChars(name + '__' + suiteName)
	node.link.text = name


######################################################################
# PRIVATE - Compiled Template
######################################################################

_template = Template(_html)


######################################################################
# PUBLIC
######################################################################

def renderdictionary(terms, style='py-appscript', options=[], template=None):
	"""Render a Dictionary object's classes and commands as an XHTML string.
		terms : osaterminology.dom.osadictionary.Dictionary -- pre-parsed dictionary object
		style : str -- keyword formatting style ('appscript' or 'applescript')
		options : list of str -- formatting options (zero or more of: 'collapse', 'showall')
		template : str -- custom HTML template to use
		Result : str -- HTML data, or empty string if no terminology was found
	"""
	if 'showall' in options:
		oldvis = terms.setvisibility(osadictionary.kAll)
	if terms.suites():
		if template:
			tpl = Template(template)
		else:
			tpl = _template
		html = encodeNonASCII(tpl.render(renderTemplate, terms, gettyperenderer(style), options))
	else:
		html = ''
	if 'showall' in options:
		terms.setvisibility(oldvis)
	return html


def doc(apppath, outfile, style='py-appscript', options=[], template=None):
	"""Render an XHTML file listing a scriptable application/scripting addition's classes and commands.
		apppath : str -- name or path to application/path to scripting addition
		outfile : str -- the file to write
		style : str -- keyword formatting style ('py-appscript', 'rb-scpt' or 'applescript')
		options : list of str -- formatting options (zero or more of: 'collapse', 'showall')
		template : str -- custom HTML template to use
		Result : bool -- False if no terminology was found and no file was written; else True
	"""
	terms = aeteparser.parseapp(findapp.byname(apppath), style)
	result = renderdictionary(terms, style, options, template)
	if result:
		with open(outfile, 'w', encoding='utf-8') as f:
			f.write(str(result))
	return bool(result)

