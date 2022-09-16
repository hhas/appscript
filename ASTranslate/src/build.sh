#!/bin/sh

# build, sign, notarize, and zip Python3 app for distribution
#
# CODESIGN_APP_IDENTITY must be Developer ID

appname='ASTranslate'

appversion='0.7.1' # update this and setup.py for new release


set -e

python3 setup.py clean

python3 setup.py py2app

cd dist

find "${appname}.app" -iname '*.so' -or -iname '*.dylib' | while read libfile; do 
  codesign -f -s "$CODESIGN_APP_IDENTITY" --timestamp -o runtime --entitlements ../python-entitlements.plist "$libfile"
done


codesign -f -s "$CODESIGN_APP_IDENTITY" -v --deep --timestamp -o runtime --entitlements ../python-entitlements.plist "${appname}.app"

ditto -c -k --keepParent "${appname}.app" "${appname}.zip"

xcrun notarytool submit "${appname}.zip" --keychain-profile notary --wait

xcrun stapler staple "${appname}.app"

rm "${appname}.zip"

cd ..

cp ../README dist/README

appdir="${appname}-${appversion}"

mv dist "${appdir}"

ditto -c -k --keepParent "${appdir}" "${appdir}.zip"

rm -rf build
