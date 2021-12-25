

from setuptools import setup

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
		install_requires = ['appscript >= 1.2.0', 'htmltemplate >= 2.2.1', 'lxml >= 4.7.1'],
)
