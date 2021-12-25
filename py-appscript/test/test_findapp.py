#!/usr/bin/env python3

import unittest
from aem import findapp


class TC_FindApp(unittest.TestCase):

	def test_find(self):
		for val, res in [
			['/System/Applications/Calendar.app', '/System/Applications/Calendar.app'],
			['calendar.app', '/System/Applications/Calendar.app'],
			['CALENDAR.APP', '/System/Applications/Calendar.app'],
			['CALENDAR', '/System/Applications/Calendar.app'],
		]:
			self.assertEqual(res, findapp.byname(val))
		self.assertEqual('/System/Library/CoreServices/Finder.app', findapp.byid('com.apple.finder'))
		self.assertRaises(findapp.ApplicationNotFoundError, findapp.byname, 'NON-EXISTENT-APP')

if __name__ == '__main__':
	unittest.main()
