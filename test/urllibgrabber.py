import sys, unittest, os, os.path
from urlparse import urlparse
sys.path.append('..')
sys.path.append('.')
from s3_urllib_grabber import AmazonS3Grabber

import testvalues

SECRET_KEY = testvalues.SECRET_KEY
KEY_ID     = testvalues.KEY_ID
TEST_URL   = testvalues.TEST_URL


class TestUrlLibGrabber(unittest.TestCase):


	TEST_PATH=urlparse(TEST_URL).path.split('/')[-1]
	@classmethod
	def removeFile(cls):
		if not cls.TEST_PATH: return
		if os.path.exists(cls.TEST_PATH): os.unlink(cls.TEST_PATH)

	def test_urlopen(self):
		grabber = AmazonS3Grabber(KEY_ID, SECRET_KEY)
		result = grabber.urlopen(TEST_URL)
		data = result.read()
		self.assertTrue(len(data)>0)

	def test_urlread(self):
		grabber = AmazonS3Grabber(KEY_ID, SECRET_KEY)
		result = grabber.urlread(TEST_URL)
		self.assertTrue( str == type(result) )

	def test_urlgrab(self):
		url = urlparse(TEST_URL)
		grabber = AmazonS3Grabber(KEY_ID, SECRET_KEY)
		result = grabber.urlgrab(TEST_URL)
		self.assertTrue(os.path.exists(self.TEST_PATH))

if __name__ == '__main__':
	unittest.main()
	try: TestUrlLibGrabber.removeFile()
	except: pass
