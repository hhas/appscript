#!/usr/bin/env python3

# A simple function that gets information on every photo currently selected
# in Photos.

from appscript import *

def infoforselectedphotos():
    """Get properties of currently selected photo(s) in Photos."""
    selection = app('Photos').selection.get()
    photos = []
    if selection[0].class_.get() == k.photo:
        for photo in selection:
            photos.append(photo.properties.get())
    else:
        raise RuntimeError('No photos selected.')
    return photos

# Test
from pprint import pprint
pprint(infoforselectedphotos())