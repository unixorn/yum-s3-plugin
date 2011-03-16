"""
   unittest for BotoGrabber

"""
#
#   Copyright 2011, Robert Mela
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import sys, unittest, os, os.path
from urlparse import urlparse
sys.path.append('..')
sys.path.append('.')
import s3

import testvalues


SECRET_KEY    = testvalues.SECRET_KEY
KEY_ID        = testvalues.KEY_ID
TEST_FILE     = testvalues.TEST_FILE
TEST_URL_BASE = testvalues.TEST_URL_BASE

class TestBotoGrabber(unittest.TestCase):


	def setUp(self):
		self.grabber = s3.createBotoGrabber()(KEY_ID, SECRET_KEY, baseurl=[TEST_URL_BASE])

	@classmethod
	def removeFile(cls):
		if not TEST_FILE: return
		if os.path.exists(TEST_FILE): os.unlink(TEST_FILE)

	def test_urlopen(self):
		result = self.grabber.urlopen(TEST_FILE)
		data = result.read()
		self.assertTrue(len(data)>0)

	def test_urlread(self):
		result = self.grabber.urlread(TEST_FILE)
		self.assertTrue( str == type(result) )

	def test_urlgrab(self):
		result = self.grabber.urlgrab(TEST_FILE, TEST_FILE)
		self.assertTrue(os.path.exists(TEST_FILE))

if __name__ == '__main__':
	unittest.main()
	try: TestBotoGrabber.removeFile()
	except: pass
