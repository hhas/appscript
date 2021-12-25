
from setuptools import setup, Extension

import os, sys
import re

if sys.version_info < (3,0):
	raise RuntimeError("Python 3.x required.")

# Version Number
with open(os.path.join(os.path.dirname(__file__), 'lib', 'appscript', '__init__.py')) as f:
	version = re.compile(r".*__version__ = '(.*?)'", re.S).match(f.read()).group(1)


setup(
		name = "appscript",
		version = version,
		description = "Control AppleScriptable applications from Python.",
		url='http://appscript.sourceforge.net',
		license='Public Domain',
		platforms=['Mac OS X'],
		install_requires=['lxml >= 4.7.1'],
		ext_modules = [
			Extension('aem.ae',
				sources=['ext/ae.c'],
				extra_compile_args=[
						'-DMAC_OS_X_VERSION_MIN_REQUIRED=MAC_OS_X_VERSION_10_12', 
						'-D__LP64__', # build fails on 10.14 due to Carbon.h issues unless this is explicitly declared
				],
				extra_link_args=[
						'-framework', 'CoreFoundation', 
						'-framework', 'ApplicationServices',
						'-framework', 'Carbon'],
			),
		],
		packages = [
			'aem',
			'appscript',
		],
		py_modules=[
			'mactypes',
			'osax',
		],
		extra_path = "aeosa",
		package_dir = {'': 'lib'},
		classifiers = [
			'License :: Public Domain',
			'Development Status :: 5 - Production/Stable',
			'Operating System :: MacOS :: MacOS X',
			'Programming Language :: Python :: 3',
		],

)
