About appscript
===============

Appscript is a high-level, user-friendly Apple event bridge that allows 
you to control AppleScriptable Mac OS X applications from Python.


Requirements
------------

Appscript supports Python 3.7 and later.

Appscript requires macOS 10.9 or later.


Installation
------------

To download and install appscript from PyPI using pip, run:

  pip3 install appscript

To install appscript from the downloaded source files, cd to the 
appscript-1.1.0 directory and run:

  python3 setup.py install

Building appscript from source requires Apple's Xcode IDE (available
from the App Store) or Command Line Tools for Xcode (available from 
<https://developer.apple.com/download/more/>).


Notes
-----

- Python 3.x documentation and sample scripts can be found in the 
  doc and sample directories.

- Developer tools for exporting application dictionaries (ASDictionary) 
  and converting application commands from AppleScript to appscript 
  syntax (ASTranslate) are available separately:

    http://appscript.sourceforge.net/tools.html

  ASDictionary 0.13.2 or later is also required to use appscript's built-in 
  help() method. If ASDictionary isn't installed, interactive help won't be 
  available but appscript will continue to operate as normal.


Copyright
---------

Appscript is released into the public domain, except for portions of ae.c, 
which is Copyright (C) the original authors; see code for details.
