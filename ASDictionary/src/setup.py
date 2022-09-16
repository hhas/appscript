"""
Requirements (available from PyPI except where noted):

- htmlemplate

- py-appscript

- py-aemreceive (from appscript repository)

- py-osaterminology (from appscript repository)

- py2app

- pyobjc

--

To build, cd to this directory and run:

	python3 setup.py py2app

"""

appname='ASDictionary'

appversion='0.15.1' # update this and build.sh for new release


from setuptools import setup
import py2app
import os

setup(
	app=[appname+".py"],
	data_files=["MainMenu.xib"],
	options=dict(
		py2app=dict(
			plist=dict(
				CFBundleVersion=appversion,
				CFBundleShortVersionString=appversion,
				NSHumanReadableCopyright="",
				CFBundleIdentifier="net.sourceforge.appscript.asdictionary",
				CFBundleDocumentTypes = [
					dict(
						CFBundleTypeExtensions=["*"],
						CFBundleTypeName="public.item",
						CFBundleTypeRole="Viewer",
					),
				],
				NSAppleEventsUsageDescription="View application terminologies and object models."
			),
			resources=[appname+'.icns'],
			iconfile=appname+'.icns'
		)
	)
)
