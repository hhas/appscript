#!/usr/bin/env python3

import unittest, subprocess
import osax, mactypes, aem

class TC_OSAX(unittest.TestCase):
	
	def test_1(self):
		sa = osax.OSAX()
		
		self.assertEqual(65, sa.ASCII_number('A'))
		
		self.assertEqual(mactypes.Alias("/Applications/"), sa.path_to(osax.k.applications_folder))
		
		self.assertEqual(mactypes.Alias("/Library/Scripts/"), 
				sa.path_to(osax.k.scripts_folder, from_=osax.k.local_domain))
		
		self.assertRaises(AttributeError, getattr, sa, 'non_existent_command')
	
	
	def test_2(self):
		sa = osax.OSAX(name='Finder')
		sa.activate()
		self.assertEqual({osax.k.button_returned: '', osax.k.gave_up: True}, sa.display_dialog('test', giving_up_after=1))
		self.assertEqual(mactypes.Alias("/System/Library/CoreServices/Finder.app/"), sa.path_to(None))	
	
	def test_4(self):
		sa = osax.OSAX(id='com.apple.finder')
		sa.activate()
		self.assertEqual({osax.k.button_returned: '', osax.k.gave_up: True}, sa.display_dialog('test', giving_up_after=1, with_icon=osax.k.stop))
		self.assertEqual(mactypes.Alias("/System/Library/CoreServices/Finder.app/"), sa.path_to(None))
	
	
	def test_5(self):
		p = subprocess.Popen("top -l1 | grep ' Finder ' | awk '{ print $1 }'", 
				shell=True, stdout=subprocess.PIPE, close_fds=True)
		out, err = p.communicate()
		pid = int(out)
		sa = osax.OSAX(pid=pid)
		self.assertEqual(mactypes.Alias("/System/Library/CoreServices/Finder.app/"), sa.path_to(None))
		sa.activate()
		self.assertEqual({osax.k.button_returned: '', osax.k.gave_up: True}, sa.display_dialog('test', giving_up_after=1))
	

	def test_6(self):
		sa = osax.OSAX(aemapp=aem.Application("/System/Library/CoreServices/Finder.app/"))
		sa.activate()
		self.assertEqual({osax.k.button_returned: '', osax.k.gave_up: True}, sa.display_dialog('test', giving_up_after=1, with_icon=osax.k.note))
		self.assertEqual(mactypes.Alias("/System/Library/CoreServices/Finder.app/"), sa.path_to(None))
	


if __name__ == '__main__':
	unittest.main()

