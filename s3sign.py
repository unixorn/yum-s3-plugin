import urllib2, time, hashlib, hmac, base64

def s3sign(request, secret_key, key_id, date=None):
	date=time.strftime("%a, %d %b %Y %H:%M:%S +0000", date or time.gmtime() )
	host = request.get_host()
	bucket = host.split('.')[0]
	request.add_header( 'Date', date)
	resource = "/%s%s" % ( bucket, request.get_selector() )
	sigstring = """%(method)s\n\n\n%(date)s\n%(canon_amzn_resource)s""" % {
                    'method':request.get_method(),
                    #'content_md5':'',
                    #'content_type':'', # only for PUT
                    'date':request.headers.get('Date'),
                    #'canon_amzn_headers':'',
                    'canon_amzn_resource':resource }
	digest = hmac.new(secret_key, sigstring, hashlib.sha1 ).digest()
	digest = base64.b64encode(digest)
	request.add_header('Authorization', "AWS %s:%s" % ( key_id,  digest ))

if __name__ == '__main__':

	SECRET_KEY = 'my_amazon_secret_key'
	KEY_ID= 'my_amazon_key_id'
	TEST_URL='http://your_bucket_name.s3.amazonws.com/yourfile.ext'

	def test3():
		req=urllib2.Request(TEST_URL)
		s3sign(req,SECRET_KEY, KEY_ID)
		try:
			resp = urllib2.urlopen(req)
			raise Exception("Invalid test - urllib2.open should raise an error")
		except:
			print "test3 success - got expected HTTP exception"

	def test2():
		req=urllib2.Request(TEST_URL)
		s3sign(req,SECRET_KEY, KEY_ID)
		resp = urllib2.urlopen(req)
		print "test2 success - able to open url"

	def test1():

		"""Validating against example data from
		http://docs.amazonwebservices.com/AmazonS3/latest/dev/index.html?RESTAuthentication.html"""

		EXAMPLE_URL='http://johnsmith.s3.amazonaws.com/photos/puppy.jpg'
		EXAMPLE_KEY_ID='0PN5J17HBGZHT7JJ3X82'
		EXAMPLE_SECRET_KEY='uV3F3YluFJax1cknvbcGwgjvx4QpvB+leU8dUj2o'
		EXAMPLE_DATE= time.strptime("2007-03-27 19:36:42", "%Y-%m-%d %H:%M:%S")
		req = urllib2.Request(EXAMPLE_URL)
		s3sign(req, EXAMPLE_SECRET_KEY, EXAMPLE_KEY_ID, EXAMPLE_DATE)
		desired="AWS 0PN5J17HBGZHT7JJ3X82:xXjDGYUmKxnwqr5KXNPGldn5LbA=" 
		actual=req.headers.get('Authorization')
		print "Test1 Desired: %s" % desired
		print "Test1 Actual : %s" % actual
		if desired != actual:
			raise Exception("Test1: Signature result invalid")
		else:
			print "Test1 Success!!!"
	
	test1()
	test2()
	test3()
#req = urllib2.Request('http://appchannel-dev.s3.amazonaws.com/nfl.xml')
#sign(req)
#resp=urllib2.urlopen(req)
#print resp.read()
#grabber = URLGrabber()
#print dir(grabber)
#as3grabber = AmazonS3Grabber( grabber, '2dvcsp7+GntMSO70AVuGtmG0ll8xSPxqpCoW5PgV', 'AKIAJWZR7LVZDR5IEGUQ')
#s=as3grabber.urlgrab('http://appchannel-dev.s3.amazonaws.com/nfl.xml')
#as3grabber.urlgrab('http://rob.dev.framechannel.com/applets/stocks/quote/IBM')
