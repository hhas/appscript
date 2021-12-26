"""
Requirements (available from PyPI except where noted):

- htmlemplate 2.2.1+

- py-aemreceive 0.5.0+ (from appscript repository)

- py-appscript 1.2.0+

- py-osaterminology 0.15.0+ (from appscript repository)

- py2app 0.26.1+

- pyobjc 8.1+

--

To build, cd to this directory and run:

	python setup.py py2app

"""

from setuptools import setup
import py2app
import os

name = 'ASDictionary'
version='0.14.0'


setup(
	app=[name+".py"],
	data_files=["MainMenu.xib"],
	options=dict(
		py2app=dict(
			plist=dict(
				CFBundleVersion=version,
				CFBundleShortVersionString=version,
				NSHumanReadableCopyright="",
				CFBundleIdentifier="net.sourceforge.appscript.asdictionary",
				CFBundleDocumentTypes = [
					dict(
						CFBundleTypeExtensions=["*"],
						CFBundleTypeName="public.item",
						CFBundleTypeRole="Viewer",
					),
				]
			),
			resources=[name+'.icns'],
			iconfile=name+'.icns'
		)
	)
)
