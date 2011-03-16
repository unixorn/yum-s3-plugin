"""
   unittest for signing of S3 Rest requests

"""

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

import sys, urllib2, time
sys.path.append('..')
sys.path.append('.')
import s3
import unittest
import testvalues as tv

class TestSigning(unittest.TestCase):
	"""You need to configure SECRET_KEY, KEY_ID, and TEST_URL with real values for your s3 store"""


	def setUp(self):
		print "Setup"
		self.grabber = s3.createUrllibGrabber()

	def test_01_constructor(self):
		grabber = s3.createUrllibGrabber()
		
	def test_03_invalidkey(self):
		self.failIf(tv.SECRET_KEY=='my_amazon_secret_key')
		self.failIf(len(tv.KEY_ID) != len('0PN5J17HBGZHT7JJ3X82'))
		req=urllib2.Request(tv.TEST_URL)
		self.grabber.s3sign(req,'bogus_key', tv.KEY_ID)
		self.assertRaises(urllib2.HTTPError, urllib2.urlopen, req )

	def test_02_urlopen(self):
		self.failIf(tv.SECRET_KEY=='my_amazon_secret_key')
		self.failIf(len(tv.KEY_ID) != len('0PN5J17HBGZHT7JJ3X82'))
		req=urllib2.Request(tv.TEST_URL)
		self.grabber.s3sign(req,tv.SECRET_KEY, tv.KEY_ID)
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
