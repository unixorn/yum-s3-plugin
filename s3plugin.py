"""
Yum plugin for Amazon S3 access.

This plugin provides access to a protected Amazon S3 bucket using Amazon's special
REST authentication scheme.
"""




def createBotoGrabber():
	import boto
	from urlparse import urlparse

	class BotoGrabber:
		def __init__(self, awsAccessKey, awsSecretKey, **kwargs):
			self.s3 = boto.connect_s3(awsAccessKey, awsSecretKey)

		def _key(self, url):
			url = urlparse(url)
			bucket_name = url.netloc.split('.')[0]
			key_name = url.path[1:]
			bucket = self.s3.get_bucket(bucket_name)
			return bucket.get_key(key_name)

		def urlgrab(self, url, filename=None, **kwargs):
			"""urlgrab(url) copy the file to the local filesystem"""
			print 'urlgrab s3'
			key = self._key(url)
			if not filename: filename = key.key
			key.get_contents_to_filename(filename)
			# zzz - does this return a value or something?
	
		def urlopen(self, url, **kwargs):
			"""urlopen(url) open the remote file and return a file object"""
			return self._key(url)

		def urlread(self, url, limit=None, **kwargs):
			"""urlread(url) return the contents of the file as a string"""
			return self._key(url).read()

	return BotoGrabber



def createUrllibGrabber():

	import os
	import sys
	import urllib2
	import time, hashlib, hmac, base64

	class UrllibGrabber:
		@classmethod
		def s3sign(cls,request, secret_key, key_id, date=None):
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

		def __init__(self, awsAccessKey, awsSecretKey, **kwargs):
			self.awsAccessKey = awsAccessKey
			self.awsSecretKey = awsSecretKey

		def _request(self,url):
			req = urllib2.Request(url)
			UrllibGrabber.s3sign(req, self.awsSecretKey, self.awsAccessKey )
			return req

		def urlgrab(self, url, filename=None, **kwargs):
			"""urlgrab(url) copy the file to the local filesystem"""
			req = self._request(url)
			if not filename:
				filename = req.get_selector()
				if filename[0] == '/': filename = filename[1:]
			out = open(filename, 'w+')
			resp = urllib2.urlopen(req)
			buff = resp.read(8192)
			while buff:
				out.write(buff)
				buff = resp.read(8192)
			# zzz - does this return a value or something?
	
		def urlopen(self, url, **kwargs):
			"""urlopen(url) open the remote file and return a file object"""
			return urllib2.urlopen( self._request(url) )

		def urlread(self, url, limit=None, **kwargs):
			"""urlread(url) return the contents of the file as a string"""
			return urllib2.urlopen( self._request(url) ).read()

	return UrllibGrabber


def createGrabber():
	try: return createBotoGrabber()
	except: return createUrllibGrabber()

AmazonS3Grabber = createGrabber()

import os
import sys
import urllib
from yum.plugins import TYPE_CORE
from yum.yumRepo import YumRepository
import yum.Errors

__revision__ = "1.0.0"

requires_api_version = '2.5'
plugin_type = TYPE_CORE

def config_hook(conduit):
	config.RepoConf.s3_enabled = config.BoolOption(False)

def init_hook(conduit):
	""" 
	Plugin initialization hook. Setup the S3 repositories.
	"""
   
	repos = conduit.getRepos()
	for i in repos.repos.keys():
		rs = repos.repos[i]
		if isinstance(repo, YumRepository) and repo.s3_enabled:
			new_repo = AmazonS3Repo(idx)
			new_repo.baseurl = repo.baseurl
			new_repo.mirrorlist = repo.mirrorlist
			new_repo.basecachedir = repo.basecachedir
			new_repo.gpgcheck = repo.gpgcheck
			new_repo.proxy = repo.proxy
			new_repo.enablegroups = repo.enablegroups
																		
			del rs.repos[repo.id]
			rs.add(new_repo)


class AmazonS3Repo(YumRepository):
	"""
	Repository object for Amazon S3.
	"""
	
	def __init__(self, repoid):
		YumRepository.__init__(self, repoid)
		self.enable()

	def _setupGrab(self):
		YumRepository.setupGrab(self)
		self.grab = AmazonS3Grabber(self.grab, 'my-access-key', 'my-secret-key')

	setupGrab = _setupGrab
