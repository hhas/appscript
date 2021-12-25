"""defaultterminology -- translation tables between appscript-style typenames and corresponding AE codes """

def getterms(style='py-appscript'):
	if style == 'py-appscript':
		from . import pyappscript as terms
	elif style == 'rb-scpt':
		from . import rbappscript as terms
	else:
		raise KeyError('Unknown style %r' % style)
	return terms