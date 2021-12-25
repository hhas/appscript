try:
	from setuptools import setup, Extension
	args = {'install_requires': ['appscript >= 1.1.0', 'htmltemplate >= 2.2.1']} # TO DO: appscript >= 1.2.0
except ImportError:
	print("Note: couldn't import setuptools so using distutils instead.")
	from distutils.core import setup, Extension
	args = {}


setup(
		name = "osaterminology",
		version = "0.15.0",
		description = "Parse and render aete/sdef resources.",
		url='http://appscript.sourceforge.net',
		license='Public Domain',
		platforms=['Mac OS X'],
		packages = [
			'osaterminology',
			'osaterminology/defaultterminology',
			'osaterminology/dom',
			'osaterminology/makeidentifier',
			'osaterminology/renderers',
			'osaterminology/sax',
			'osaterminology/tables',
		],
		extra_path = "aeosa",
		package_dir = { '': 'lib' },
		**args
)
