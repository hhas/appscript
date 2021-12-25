#!/usr/bin/env python3

# List names of playlists in Music.

from appscript import *

print(app('Music').sources[1].user_playlists.name.get())