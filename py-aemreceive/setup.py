
from setuptools import setup


setup(
		name = "aemreceive",
		version = "0.5.0",
		description = "Basic Apple event handling support for Python-based Mac OS X applications.",
		url='http://appscript.sourceforge.net',
		license='Public Domain',
		platforms=['Mac OS X'],
		packages = ['aemreceive'],
		extra_path = "aeosa",
		package_dir = { '': 'lib' },
		install_requires = ['appscript >= 1.2.0'],
)
