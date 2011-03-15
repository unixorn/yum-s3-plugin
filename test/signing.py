import sys, urllib2, time
sys.path.append('..')
sys.path.append('.')
import s3plugin
import unittest
import testvalues

class TestSigning(unittest.TestCase):
	"""You need to configure SECRET_KEY, KEY_ID, and TEST_URL with real values for your s3 store"""

	SECRET_KEY = testvalues.SECRET_KEY
	KEY_ID     = testvalues.KEY_ID
	TEST_URL   = testvalues.TEST_URL

	def setUp(self):
		print "Setup"
		self.grabber = s3plugin.createUrllibGrabber()

	def test_01_constructor(self):
		grabber = s3plugin.createUrllibGrabber()
		
	def test_03_invalidkey(self):
		req=urllib2.Request(self.TEST_URL)
		self.grabber.s3sign(req,'bogus_key', self.KEY_ID)
		self.assertRaises(urllib2.HTTPError, urllib2.urlopen, req )

	def test_02_urlopen(self):
		self.failIf(self.SECRET_KEY=='my_amazon_secret_key')
		self.failIf(len(self.KEY_ID) != len('0PN5J17HBGZHT7JJ3X82'))
		req=urllib2.Request(self.TEST_URL)
		self.grabber.s3sign(req,self.SECRET_KEY, self.KEY_ID)
		resp=urllib2.urlopen(req)
		self.assertEquals(1,1)

	def test_02_example_key(self):

		"""Validating against example data from
		http://docs.amazonwebservices.com/AmazonS3/latest/dev/index.html?RESTAuthentication.html"""

		EXAMPLE_URL='http://johnsmith.s3.amazonaws.com/photos/puppy.jpg'
		EXAMPLE_KEY_ID='0PN5J17HBGZHT7JJ3X82'
		EXAMPLE_SECRET_KEY='uV3F3YluFJax1cknvbcGwgjvx4QpvB+leU8dUj2o'
		EXAMPLE_DATE= time.strptime("2007-03-27 19:36:42", "%Y-%m-%d %H:%M:%S")

		req = urllib2.Request(EXAMPLE_URL)
		self.grabber.s3sign(req, EXAMPLE_SECRET_KEY, EXAMPLE_KEY_ID, EXAMPLE_DATE)
		desired="AWS 0PN5J17HBGZHT7JJ3X82:xXjDGYUmKxnwqr5KXNPGldn5LbA=" 
		actual=req.headers.get('Authorization')
		print "Test1 Desired: %s" % desired
		print "Test1 Actual : %s" % actual
		self.assertEqual(actual, desired)

if __name__ == '__main__':
	unittest.main()
