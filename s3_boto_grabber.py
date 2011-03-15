"""
Grabber workalike Amazon S3 Yum plugin
"""

import boto
from urlparse import urlparse

class AmazonS3Grabber:
    def __init__(self, awsAccessKey, awsSecretKey, **kwargs):
        print 'init s3'
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


