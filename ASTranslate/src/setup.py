"""
Requirements (available from PyPI except where noted):

- py-appscript 1.2.0+

- py-osaterminology 0.15.0+ (from appscript repository)

- py2app 0.26.1+

- pyobjc 8.1+

--

To build, cd to this directory and run:

	python setup.py py2app

"""

from setuptools import setup, Extension
import py2app

version = '0.6.0'


setup(
	app=["ASTranslate.py"],
	data_files=["MainMenu.xib", "ASTranslateDocument.xib"],
	ext_modules = [
		Extension('_astranslate',
			sources=['_astranslate.c'],
			extra_compile_args=['-DMAC_OS_X_VERSION_MIN_REQUIRED=MAC_OS_X_VERSION_10_12'],
			extra_link_args=['-framework', 'Carbon'],
		),
	],
	options=dict(
		py2app=dict(
			plist=dict(
				NSAppleEventsUsageDescription="Optionally sends Apple events to target applications.",
				CFBundleIdentifier="net.sourceforge.appscript.astranslate",
				CFBundleVersion=version,
				CFBundleShortVersionString=version,
				NSHumanReadableCopyright="",
				CFBundleDocumentTypes = [
					dict(
						CFBundleTypeExtensions=[],
						CFBundleTypeName="Text File",
						CFBundleTypeRole="Editor",
						NSDocumentClass="ASTranslateDocument"
					)
				]
			),
			resources=['ASTranslate.icns'],
			iconfile='ASTranslate.icns'
		)
	)
)

