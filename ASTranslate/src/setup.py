"""
Requirements (available from PyPI except where noted):

- py-appscript

- py-osaterminology (from appscript repository)

- py2app

- pyobjc

--

To build, cd to this directory and run:

	python3 setup.py py2app

"""


appversion='0.7.1' # update this and build.sh for new release


from setuptools import setup, Extension
import py2app

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
				CFBundleVersion=appversion,
				CFBundleShortVersionString=appversion,
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

