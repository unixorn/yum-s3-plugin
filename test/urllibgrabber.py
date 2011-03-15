"""
   unittest for urllib-based grabber for yum s3 plugin
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
import s3plugin

import testvalues

SECRET_KEY = testvalues.SECRET_KEY
KEY_ID     = testvalues.KEY_ID
TEST_URL   = testvalues.TEST_URL


class TestUrlLibGrabber(unittest.TestCase):


	TEST_PATH=urlparse(TEST_URL).path.split('/')[-1]

	def setUp(self):
		self.grabber = s3plugin.createUrllibGrabber()(KEY_ID,SECRET_KEY)

	@classmethod
	def removeFile(cls):
		if not cls.TEST_PATH: return
		if os.path.exists(cls.TEST_PATH): os.unlink(cls.TEST_PATH)

	def test_urlopen(self):
		result = self.grabber.urlopen(TEST_URL)
		data = result.read()
		self.assertTrue(len(data)>0)

	def test_urlread(self):
		result = self.grabber.urlread(TEST_URL)
		self.assertTrue( str == type(result) )

	def test_urlgrab(self):
		url = urlparse(TEST_URL)
		result = self.grabber.urlgrab(TEST_URL)
		self.assertTrue(os.path.exists(self.TEST_PATH))

if __name__ == '__main__':
	unittest.main()
	try: TestUrlLibGrabber.removeFile()
	except: pass
