"""
Grabber workalike Amazon S3 Yum plugin
"""

import os
import sys
import urllib2

from s3sign import s3sign

class AmazonS3Grabber:
    def __init__(self, grabber, awsAccessKey, awsSecretKey, **kwargs):
        print 'init s3'
        self.grabber = grabber
        self.awsAccessKey = awsAccessKey
        self.awsSecretKey = awsSecretKey

    def _request(url):
        req = urllib2.Request(args)
        s3sign(req, self.awsSecretKey, self.awsAccessKey )
        return req

    def urlgrab(self, url, filename=None, **kwargs):
        """urlgrab(url) copy the file to the local filesystem"""
        print 'urlgrab s3'
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
    
    def urlopen(self, url, **kwargs):
        """urlopen(url) open the remote file and return a file object"""
        return urllib2.urlopen( self._request(url) )

    def urlread(self, url, limit=None, **kwargs):
        """urlread(url) return the contents of the file as a string"""
        return urrlib2.urlopen( self._request(url) ).read()


