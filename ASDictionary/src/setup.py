"""
Requirements (available from PyPI except where noted):

- HTMLTemplate 1.5.0+

- py-appscript 0.22.0+

- py-aemreceive 0.4.0+ (from appscript svn repository)

- py-osaterminology 0.14.6+ (from appscript svn repository)

- pyobjc 1.4+

- py2app 0.5.2+

--

To build, cd to this directory and run:

	python setup.py py2app

"""

from setuptools import setup
import py2app
from plistlib import Plist
import os

name = 'ASDictionary'
version='0.13.2'


setup(
	app=[name+".py"],
	data_files=["MainMenu.nib"],
	options=dict(
	

		py2app=dict(
			plist=Plist(
				NSAppleScriptEnabled=True,
				CFBundleVersion=version,
				CFBundleShortVersionString=version,
				NSHumanReadableCopyright="",
				CFBundleIdentifier="net.sourceforge.appscript.asdictionary",
				OSAScriptingDefinition=name+'.sdef',
				CFBundleDocumentTypes = [
					dict(
						CFBundleTypeExtensions=["*"],
						CFBundleTypeName="public.item",
						CFBundleTypeRole="Viewer",
					),
				]
			),
			resources=[name+'.icns', name+'.sdef'],
			iconfile=name+'.icns'
		)
	)
)
