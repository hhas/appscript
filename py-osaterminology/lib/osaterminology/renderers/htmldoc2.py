#!/usr/bin/env python

"""htmldoc2 - Render application terminology as multiple XHTML documents.

Performs a full analysis of class inheritance and object model relationships
so resulting documentation is more detailed than that produced by htmldoc
(and also takes longer to generate).
"""

from os import mkdir
from os.path import exists, join

from htmltemplate import Template

from aem import findapp
from osaterminology.dom import aeteparser, osadictionary
from osaterminology.renderers.typerenderers import gettyperenderer

#__all__ = ['renderdictionary', 'doc']


######################################################################
# PRIVATE - Template HTML
######################################################################

framehtml = '''<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" 
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title node="con:title">TextEdit terminology | py-appscript</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>

<frameset rows="20%, 80%">
	<frameset cols="20%, 40%, 40%">
		<frame src="html/suites.html"  name="Suites" />
		<frame src="html/classes.html"  name="Classes" />
		<frame src="html/commands.html" name="Commands" />
	</frameset>
	<frame src="html/index.html" name="main" />
</frameset>

</html>'''

######################################################################

indexhtml = '''<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" 
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title node="con:title">TextEdit</title>
	<style type="text/css" media="all"><!--@import url(main.css);--></style>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<base target="main" />
</head>
<body>

<!-- summary of application dictionary -->

<a name="home"></a>
<h1><sup>Application</sup> <span node="con:title2">Some App</span></h1>

<div id="content">

<p><code node="con:location">some app path</code></p>

<div node="-rep:suite">

	<h2>
		<a node="con:anchor" name="suite_StandardSuite"></a>
		<span node="-con:name">some suite</span>
	</h2>

	<p node="con:desc">some description</p>
	
	<div node="-rep:definitions">

		<h3 node="con:label">Classes</h3>

		<ul>
		<li node="rep:item">
			<a node="con:anchor" name="class_application__Standard_Suite"></a>
			<strong><a node="con:name" href="Standard_Suite/classes/application.html">some class</a></strong>
			<span node="-con:desc">some description</span>
		</li>
		</ul>

	</div>
</div>


</div>

</body>
</html>'''

######################################################################

suitesnavhtml = '''<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" 
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title>Suites</title>
	<style type="text/css" media="all"><!--@import url(main.css);--></style>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<base target="main" />
</head>
<body id="nav">

<h1>Suites</h1>

<table width="100%" summary="navigation">
<tr><td><a href="index.html#home"><em node="con:name">some app</em></a></td></tr>
<tr node="rep:suite">
	<td><a node="con:name" href="index.html#suite_Standard_Suite">some suite</a></td>
</tr>
</table>

</body>
</html>'''

######################################################################

classesnavhtml = '''<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" 
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title>Classes</title>
	<style type="text/css" media="all"><!--@import url(main.css);--></style>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<base target="main" />
</head>
<body id="nav">

<h1>Classes</h1>


<table width="100%" summary="navigation">
<tr node="rep:item">
	<td><a node="con:name" href="Standard_Suite/classes/application.html">some class</a></td>
	<td class="suite"><a node="con:suitename" href="index.html#class_application__Standard_Suite">some suite</a></td>
</tr>
</table>


</body>
</html>'''

######################################################################

commandsnavhtml = '''<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" 
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title node="con:title">Commands</title>
	<style type="text/css" media="all"><!--@import url(main.css);--></style>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<base target="main" />
</head>
<body id="nav">

<h1 node="con:title2">Commands</h1>


<table width="100%" summary="navigation">
<tr node="rep:item">
	<td><a node="con:name" href="Standard_Suite/commands/save.html">some command</a></td>
	<td class="suite"><a node="con:suitename" href="index.html#command_save__Standard_Suite">some suite</a></td>
</tr>
</table>


</body>
</html>'''

######################################################################

classhtml = '''<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" 
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title node="con:title">some class</title>
	<style type="text/css" media="all"><!--@import url(../../main.css);--></style>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<base target="main" />
</head>
<body>

<h1><sup>Class</sup> <span node="-con:title2">some class</span></h1>

<div id="view"><a node="con:changeview" href="../../full/classes/application.html">full</a></div>


<div id="content">

<h2>Description</h2>

<p node="con:desc">some description</p>

<ul class="desc">
	<li node="con:pluralname">Plural name:
		<ul>
			<li><strong node="con:name">some plural class</strong></li>
		</ul>
	</li>
	<li node="con:suite">Defined in:
		<ul>
			<li node="rep:item"><em><a node="con:name" href="../../index.html#Standard_Suite">some suite</a></em></li>
		</ul>
	</li>
	
	<li node="con:parents">Inherits from:
		<ul>
			<li node="rep:item">
				<span node="-rep:parent">
					<strong><a node="con:name" href="../../Standard_Suite/classes/item.html">some class</a></strong>
					(<em><a node="con:suitename" href="../../index.html#Standard_Suite">some suite</a></em>)
				</span>
				<span node="-sep:parent"> &#8594; </span>
			</li>
		</ul>
	</li>
</ul>

<div node="-con:properties">
	<h2>Properties</h2>
	<ul>
		<li node="rep:item">
			<strong node="con:name">some property</strong>
			<span node="-con:access">(r/o)</span>
			<em node="con:type">some type</em>
			<span node="-con:desc"> -- some description</span>
		</li>
	</ul>
</div>

<div node="-con:elements">
	<h2>Elements</h2>
	<ul>
		<li node="rep:item">
			<strong><a href="" node="con:name">some elements</a></strong> -- by
			<em node="con:desc">name, index, relative position, range, filter, ID</em>
		</li>
	</ul>
</div>

<div node="-con:misc">
	<h2>Notes</h2>
	
	<ul class="desc">
		<li node="rep:note"><span node="-con:label">Inherited by</span>:
			<ul>
				<li node="rep:item">
					<strong><a node="con:name" href="../../TextEdit_suite/classes/application.html">some class</a></strong>
					(<em><a node="con:suitename" href="../../index.html#Standard_Suite">some suite</a></em>)
				</li>
			</ul>
		</li>
	</ul>

</div>

</body>
</html>'''

######################################################################

commandhtml = '''<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" 
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title node="con:title">some command</title>
	<style type="text/css" media="all"><!--@import url(../../main.css);--></style>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<base target="main" />
</head>
<body>

<h1><sup>Command</sup> <span node="-con:title2">some command</span></h1>

<div id="content">

<h2>Description</h2>

<p node="con:desc">some description</p>

<ul class="desc">
	<li node="con:suite">Defined in:
		<ul>
			<li node="rep:item"><em><a node="con:name" href="../../index.html#Standard_Suite">some suite</a></em></li>
		</ul>
	</li>
</ul>


<div node="-con:parameters">

<h2>Parameters</h2>
<ul>
	<li node="con:directarg">
		<span node="-con:name">[direct param type]</span>
		<span node="-con:desc"> -- some description</span>
	</li>
	<li node="rep:arg">
		<span node="-con:name">[some param : param type]</span>
		<span node="-con:desc"> -- some description</span>
	</li>
</ul>

</div>

<div node="-con:reply">
	<h2>Result</h2>
	
	<ul>
		<li><em node="con:type">some result type</em>
		<span node="-con:desc"> -- some description</span>
		</li>
	</ul>
</div>


</div>

</body>
</html>'''

######################################################################

css = '''/* main stylesheet */

body {font-family:Verdana, sans-serif; margin:0; padding:0;}

h1 {
	font-size:1.8em; 
	color:#fff; background-color:#800; 
	margin:0; padding:0.3em 18px 0.35em; 
	border-bottom: 0.2em solid #500;
}


h2 {
	font-size:1em; 
	color:#600; background-color:transparent; 
	margin:1.5em 0 0; padding-bottom:1px; 
	border-bottom: 1px dotted #500;
}


h3 {font-size:1em; color:#600; background-color:transparent;}

h1 sup {font-size: 0.4em;}

#content {padding:0 18px 10px; font-size:0.8em;}
.desc {padding-left:0;}
.desc li {margin-bottom:1em;}
.desc li ul {padding-left:40px;}
.desc li ul li {margin-bottom:0;}

#nav h1 {padding:0.2em 3px;}
#nav h1, #nav td {font-size:0.7em;}
#nav table {border-collapse:collapse;}
#nav td {padding:0; margin:0 3px;}
#nav .suite {text-align:right; font-style:italic;}



li {list-style-type:none;}

a {color:#000; text-decoration:none;}
a {border-bottom:dotted 1px black;}
a:hover {border-bottom:solid 1px black;}

#nav a {border-bottom:none; padding:0 0.3em;}
#nav a:hover {color:#fff; background-color:#800;}

#view {
	font-size:0.7em; font-style:italic; 
	color:#fff; background-color:#800; 
	margin:0; padding:3px 18px 5px; 
	border-bottom: 1px solid #800; 
	position:absolute; right:0; top:0.5em
}

#view a {color:#fff; text-decoration:none;}
#view a {border-bottom:dotted 1px #fff;}
#view a:hover {border-bottom:solid 1px #fff;}'''


######################################################################
# PRIVATE - Helper Functions
######################################################################

def makedictionarydirectory(root, terms):
	pths = [
			'', 
			'html',
			'html/FULL',
			'html/FULL/classes']
	dirs = [join(root, pth) for pth in pths]
	for suite in terms.suites():
		suitedir = join(root, 'html', stripnonchars(suite.name))
		for pth in [suitedir, join(suitedir, 'classes'), join(suitedir, 'commands')]:
			dirs.append(pth)
	for pth in dirs:
		if not exists(pth):
			mkdir(pth)

#######

_stripnoncharscache = {}

def stripnonchars(txt):
	if txt not in _stripnoncharscache:
		_stripnoncharscache[txt] = ''.join([char for char in txt.replace(' ', '_') if char in 
				'abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789'])
	return _stripnoncharscache[txt]

def stripappsuffix(name):
	if name.lower()[-4:] == '.app':
		name = name[:-4]
	return name

def esc(str):
	return str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def formatdescription(desc): 
	return desc and ' -- ' + desc or ''

def suitefolder(klass, options):
	return 'FULL' in options and 'FULL' or stripnonchars(klass.suitename)

def formattype(types, typerenderer, options=[]):
	result = []
	for type in types:
		res = ''
		if type.islist: # render 'list of' bit outside the link
			res += 'list of '
			type = type.type
		classes = type.realvalues('class')
		if classes:
			klass = classes[-1]
			res += '<a href="../../%s/classes/%s.html">%s</a>' % (
					suitefolder(klass, options), 
					stripnonchars(klass.name), 
					esc(typerenderer.render(type)))
		else:
			enums = type.realvalues('enumeration')
			if enums:
				enum = enums[-1]
				res += esc(typerenderer.render(enum))
			else:
				res += esc(typerenderer.render(type)) # missing class/enum definition, so will be rendered as raw AE code or whatever else is left
		result.append(res)
	return ' | '.join(result)

def removeduplicatesfromsortedlist(lst):
	i = 0
	prev = None
	while i < len(lst):
		while i < len(lst) and lst[i] == prev:
			lst.pop(i)
		if i < len(lst):
			prev = lst[i]
		i += 1

##

def writefile(pth, txt):
	with open(pth, 'w', encoding='utf-8') as f:
		f.write(txt)


######################################################################
# PRIVATE - Template Controllers
######################################################################
# Frame

def render_frame(node, terms):
	node.title.text = '%s terminology for %s' % (stripappsuffix(terms.name), terms.style)


frametpl = Template(framehtml)


######################################################################
# Index
		
def render_index(node, terms):
	node.title.text = node.title2.text = stripappsuffix(terms.name)
	node.location.text = terms.path
	node.suite.repeat(render_suite, terms.suites())

def render_suite(node, suite):
	node.anchor.atts['name'] = 'suite_%s' % stripnonchars(suite.name) 
	node.name.text = suite.name
	node.desc.text = suite.description
	node.definitions.repeat(render_classesorcommands, 
			[(n, o) for n, o in [(0, suite.classes()), (1, suite.commands())] if o])

def render_classesorcommands(node, xxx_todo_changeme):
	(kind, items) = xxx_todo_changeme
	node.label.text = ['Classes', 'Commands'][kind]
	node.item.repeat(render_classorcommand, items, kind)

def render_classorcommand(node, item, kind):
	name = stripnonchars(item.name)
	suitename = stripnonchars(item.suitename)
	node.anchor.atts['name'] = '%s_%s__%s' % (['class', 'command'][kind], name, suitename)
	node.name.atts['href'] = '%s/%s/%s.html' % (suitename, ['classes', 'commands'][kind], name)
	node.name.text = item.name
	node.desc.text = formatdescription(item.description)


indextpl = Template(indexhtml)


######################################################################
# Suites navigation

def render_suitesnav(node, terms):
	node.name.text = stripappsuffix(terms.name)
	node.suite.repeat(render_suitenav, terms.suites())

def render_suitenav(node, suite):
	node.name.atts['href'] = 'index.html#suite_%s' % stripnonchars(suite.name) 
	node.name.text = suite.name


suitenavtpl = Template(suitesnavhtml)


######################################################################
# Classes and commands navigation

def sortnodes(nodes):
	nodes = list(nodes)
	nodes.sort(key=lambda s: s.name.lower())
	return nodes

#######

def render_classesnav(node, terms):
	node.item.repeat(render_classnav, sortnodes(terms.classes()), 0)

def render_commandsnav(node, terms):
	node.item.repeat(render_classorcommandnav, sortnodes(terms.commands()), 1)

def render_classnav(node, item, kind):
	name = stripnonchars(item.name)
	render_classorcommandnav(node, item, kind)

def render_classorcommandnav(node, item, kind):
	name = stripnonchars(item.name)
	suitename = stripnonchars(item.suitename)
	node.name.atts['href'] = '%s/%s/%s.html' % (suitename, ['classes', 'commands'][kind], name)
	node.name.text = item.name
	node.suitename.atts['href'] = 'index.html#suite_%s' % suitename
	node.suitename.text = item.suitename


classnavtpl = Template(classesnavhtml)
commandnavtpl = Template(commandsnavhtml)


######################################################################
# Class definition

def resolvechain(klass, chain, touched, result):
	if isinstance(klass, osadictionary.Class):
		parents = klass.parents()
	else:
		parents = [] # faulty dictionary (parent is a type instead of a class)
	if klass in touched or not parents:
		if chain:
			result.append(chain)
	else:
		touched = touched + [klass]
		for parent in parents:
			resolvechain(parent, chain + [parent], touched, result)

def analyseobjectmodel(terms): # TO DO: this should go into osadictionary
	# build table listing subclasses for each class
	parents = {}
	children = {}
	onetoone = {}
	onetomany = {}
	for klass in terms.classes():
		parents[(klass.name, klass.suitename)] = chains = []
		resolvechain(klass, [], [], chains)
		# determine subclasses of each class
		for parent in klass.parents():
			if isinstance(parent, osadictionary.Class):
				key = (parent.name, parent.suitename)
			else:
				key = parent.name # faulty dictionary (parent is a type instead of a class)
			if key not in children:
				children[key] = []
			children[key].append(klass)
		# determine containers of each object class
		# TO DO: support collapse/full
		for o in klass.properties():
			o = o.type.realvalue()
			if o.kind == 'class':
				if o.name not in onetoone:
					onetoone[o.name] = []
				if klass not in onetoone[o.name]:
					onetoone[o.name].append(klass)
		for o in klass.elements():
			o = o.type.realvalue()
			if o.kind == 'class':
				if o.name not in onetomany:
					onetomany[o.name] = []
				onetomany[o.name].append(klass)
	return parents, children, onetoone, onetomany

#######

def render_class(node, klass, xxx_todo_changeme1, typerenderer, options):
	(parents, children, onetoone, onetomany) = xxx_todo_changeme1
	node.title.text = node.title2.text = klass.name
	if 'FULL' in options:
		node.changeview.atts['href'] = '../../%s/classes/%s.html' % (stripnonchars(klass.suitename), stripnonchars(klass.name))

		node.changeview.text = 'reduce'
	else:
		node.changeview.atts['href'] = '../../FULL/classes/%s.html' % stripnonchars(klass.name)

		node.changeview.text = 'expand'
	if klass.description:
		node.desc.text = klass.description
	else:
		node.desc.omit()
	if klass.pluralname == klass.name:
		node.pluralname.omit()
	else:
		node.pluralname.name.text = klass.pluralname
	if 'FULL' in options:
		klass = klass.full()
	elif 'collapse' in options:
		klass = klass.collapse()
	if 'FULL' in options or 'collapse' in options:
		node.suite.item.repeat(render_definedinsuite, klass.classes())
	else:
		node.suite.item.repeat(render_definedinsuite, [klass])
	properties = klass.properties()
	elements = klass.elements()
	parents = parents.get((klass.name, klass.suitename), [])
	children = children.get((klass.name, klass.suitename), [])
	containers = sortnodes(onetoone.get(klass.name, []) + onetomany.get(klass.name, []))
	removeduplicatesfromsortedlist(containers)
	if parents:
		node.parents.item.repeat(render_parents, parents, typerenderer, options)
	else:
		node.parents.omit()
	if properties:
		node.properties.item.repeat(render_property, properties, typerenderer, options)
	else:
		node.properties.omit()
	if elements:
		node.elements.item.repeat(render_element, elements, typerenderer, options)
	else:
		node.elements.omit()
	if children or containers:
		notes = [('Inherited by', children), ('Contained by', containers)]
		notes = [(label, items) for label, items in notes if items]
		node.misc.note.repeat(render_note, notes, typerenderer, options)
	else:
		node.misc.omit()

def render_definedinsuite(node, klass):
	node.name.atts['href'] = '../../index.html#suite_%s' % stripnonchars(klass.suitename)
	node.name.text = klass.suitename

def render_property(node, property, typerenderer, options):
	if property.access =='rw':
		node.access.omit()
	else:
		node.access.text = {'r': '(r/o)', 'w': '(w/o)'}[property.access]
	node.name.text = property.name
	node.type.html = formattype(property.types, typerenderer, options)
	node.desc.text = formatdescription(property.description)

def render_element(node, element, typerenderer, options):
	node.name.text = typerenderer.elementname(element.type)
	node.desc.text = ', '.join(element.accessors())
	if element.type.name:
		classes = element.type.realvalues('class')
		if classes:
			klass = classes[-1]
			node.name.atts['href'] = '../../%s/classes/%s.html' % (suitefolder(klass, options), stripnonchars(klass.name))
		else:
			node.name.omittags()
	else:# some apps, e.g. GraphicConverter, define incomplete terminology
		node.name.omittags()

def render_parents(node, parents, typerenderer, options):
	node.parent.repeat(render_classlistitem, parents, typerenderer, options)

def render_note(node, xxx_todo_changeme2, typerenderer, options):
	(label, items) = xxx_todo_changeme2
	node.label.text  = label
	node.item.repeat(render_classlistitem, items, typerenderer, options)

def render_classlistitem(node, klass, typerenderer, options):
	if klass.kind == 'class':
		node.name.atts['href'] = '../../%s/classes/%s.html' % (suitefolder(klass, options), stripnonchars(klass.name))
		node.suitename.atts['href'] = '../../index.html#suite_%s' % stripnonchars(klass.suitename)
		node.suitename.text = klass.suitename
	else:
		node.name.omittags()
		node.suitename.omittags()
		node.suitename.text = 'datatype'
	node.name.text = typerenderer.render(klass)  # TO DO: show raw form if no name
	

classtpl = Template(classhtml)


######################################################################
# Command definition

def render_command(node, command, typerenderer, options):
	directarg = command.directparameter
	node.title.text = node.title2.text = command.name
	if command.description:
		node.desc.text = command.description
	else:
		node.desc.omit()
	node.suite.item.repeat(render_definedinsuite, [command])
	if directarg or command.parameters:
		# Render direct arg, if any.
		if directarg:
			s = '<em>%s</em>' % formattype(directarg.types, typerenderer)
			if directarg.optional:
				s = '[' + s + ']'
			node.parameters.directarg.name.html = s
			node.parameters.directarg.desc.text = formatdescription(directarg.description)
		else:
			node.parameters.directarg.omit()
		# Render labelled args, if any.
		node.parameters.arg.repeat(render_parameter, command.parameters, typerenderer)
	else:
		node.parameters.omit()
	# Render reply, if any.
	reply = command.result
	if reply:
		node.reply.type.html = formattype(reply.types, typerenderer)
		node.reply.desc.text = formatdescription(reply.description)
	else:
		node.reply.omit()

def render_parameter(node, arg, typerenderer):
	s = '<strong>%s</strong> <em>%s</em>' % (esc(arg.name), formattype(arg.types, typerenderer))
	if arg.optional:
		s = '[' + s + ']'
	node.name.html = s
	node.desc.text = formatdescription(arg.description)


commandtpl = Template(commandhtml)


######################################################################
# PUBLIC
######################################################################


def renderdictionary(terms, outdir, style='py-appscript', options=[]):
	"""Render a Dictionary object's classes and commands as XHTML files.
		terms : osaterminology.dom.osadictionary.Dictionary -- pre-parsed dictionary object
		outdir : str -- the directory to write the dictionary to (will be created if it doesn't already exist)
		style : str -- keyword formatting style ('appscript' or 'applescript')
		options : list of str -- formatting options (zero or more of: 'collapse', 'showall')
		Result : bool -- False if no terminology was found and no file was written; else True
	"""
	if 'showall' in options:
		oldvis = terms.setvisibility(osadictionary.kAll)
	if terms.suites():
		terms.style = style # TO DO: this should be defined by osadictionary
		typerenderer = gettyperenderer(style)
		# make directory structure
		makedictionarydirectory(outdir, terms)
		writefile(join(outdir, 'html/main.css'), css)
		# render frames, index and nav
		for pth, tpl, renderfn in [
				('index.html', frametpl, render_frame), 
				('html/index.html', indextpl, render_index),
				('html/suites.html', suitenavtpl, render_suitesnav),
				('html/classes.html', classnavtpl, render_classesnav),
				('html/commands.html', commandnavtpl, render_commandsnav),
				]:
			writefile(join(outdir, pth), tpl.render(renderfn, terms))
		# render classes
		modelinfo = analyseobjectmodel(terms)
		for klass in terms.classes():
			suitedir = join(outdir, 'html', stripnonchars(klass.suitename))
			writefile(join(suitedir, 'classes', stripnonchars(klass.name) + '.html'),
					classtpl.render(render_class, klass, modelinfo, typerenderer, options))
		# render expanded classes
		suitedir = join(outdir, join(outdir, 'html/FULL'))
		for klass in terms.classes():
			writefile(join(suitedir, 'classes', stripnonchars(klass.name) + '.html'), 
					classtpl.render(render_class, klass, modelinfo, typerenderer, options + ['FULL']))
		# render commands
		for command in terms.commands():
			suitedir = join(outdir, 'html', stripnonchars(command.suitename))
			writefile(join(suitedir, 'commands', stripnonchars(command.name) + '.html'),
					commandtpl.render(render_command, command, typerenderer, options))
	if 'showall' in options:
		terms.setvisibility(oldvis)
	return bool(terms.suites())



def doc(apppath, outdir, style='py-appscript', options=[]):
	"""Render XHTML files listing a scriptable application/scripting addition's classes and commands.
		apppath : str -- name or path to application/path to scripting addition
		outdir : str -- the directory to write the dictionary to (will be created if it doesn't already exist)
		style : str -- keyword formatting style ('py-appscript', 'rb-scpt' or 'applescript')
		options : list of str -- formatting options (zero or more of: 'collapse', 'showall')
		Result : bool -- False if no terminology was found and no file was written; else True
	"""
	terms = aeteparser.parseapp(findapp.byname(apppath), style)
	return renderdictionary(terms, outdir, style, options)

