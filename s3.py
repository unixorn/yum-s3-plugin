"""
Yum plugin for Amazon S3 access.

This plugin provides access to a protected Amazon S3 bucket using either boto
or Amazon's REST authentication scheme.

On CentOS this file goes into /usr/lib/yum-plugins/s3.py

You will also need two configuration files.   See s3.conf and s3test.repo for
examples on how to deploy those.


"""

#   Copyright 2011, Robert Mela
#   Copyright 2011, Jens Braeuer
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

import logging
import os
import sys
import urllib

from yum.plugins import TYPE_CORE
from yum.yumRepo import YumRepository
from yum import config
from yum import logginglevels

import yum.Errors

def interactive_notify(msg):
    if sys.stdout.isatty():
        print msg

def createUrllibGrabber():
    """
    Fetch files from AWS without boto. This code has not been tested on RHEL 6 as EPEL ships with boto 2.x.
    """
    import os
    import sys
    import urllib2
    import time, sha, hmac, base64

    class UrllibGrabber:
        @classmethod

        def s3sign(cls,request, secret_key, key_id, date=None):
                date=time.strftime("%a, %d %b %Y %H:%M:%S +0000", date or time.gmtime() )
                host = request.get_host()
                bucket = host.split('.')[0]
                request.add_header('Date', date)
                resource = "/%s%s" % ( bucket, request.get_selector() )
                sigstring = """%(method)s\n\n\n%(date)s\n%(canon_amzn_resource)s""" % {
                                           'method':request.get_method(),
                                           #'content_md5':'',
                                           #'content_type':'', # only for PUT
                                           'date':request.headers.get('Date'),
                                           #'canon_amzn_headers':'',
                                           'canon_amzn_resource':resource }
                digest = hmac.new(secret_key, sigstring, sha ).digest()
                digest = base64.b64encode(digest)
                request.add_header('Authorization', "AWS %s:%s" % ( key_id,  digest ))

        def __init__(self, awsAccessKey, awsSecretKey, baseurl ):
            try: baseurl = baseurl[0]
            except: pass
            self.baseurl = baseurl
            self.awsAccessKey = awsAccessKey
            self.awsSecretKey = awsSecretKey

        def _request(self,url):
            req = urllib2.Request("%s%s" % (self.baseurl, url))
            UrllibGrabber.s3sign(req, self.awsSecretKey, self.awsAccessKey )
            return req

        def urlgrab(self, url, filename=None, **kwargs):
            """urlgrab(url) copy the file to the local filesystem"""
            self.verbose_logger.log(logginglevels.DEBUG_4, "UrlLibGrabber urlgrab url=%s filename=%s" % ( url, filename ))
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
            return filename
            # zzz - does this return a value or something?

        def urlopen(self, url, **kwargs):
            """urlopen(url) open the remote file and return a file object"""
            return urllib2.urlopen( self._request(url) )

        def urlread(self, url, limit=None, **kwargs):
            """urlread(url) return the contents of the file as a string"""
            return urllib2.urlopen( self._request(url) ).read()

    return UrllibGrabber

def createBotoGrabber():
    import boto
    from urlparse import urlparse
    import sys
    import re
    from urlgrabber.grabber import URLGrabber

    class BotoGrabber(URLGrabber):
        logger = logging.getLogger("yum.verbose.main")

        def __init__(self, awsAccessKey, awsSecretKey, baseurl):
            self.logger.debug("BotoGrabber init BASE_URL=%s" % baseurl)

            URLGrabber.__init__(self)
            self._handle_baseurl(baseurl)
            self._handle_s3(awsAccessKey, awsSecretKey)
            self._dump_attributes()
            interactive_notify("%s - %s" % (self.bucket_name, self.key_prefix))

        def _handle_baseurl(self, baseurl):
            if type(baseurl) == list:
                baseurl = baseurl[0]

            # self.baseurl[1] is self.baseurl.netloc; self.baseurl[2] is self.baseurl.path
            # See http://docs.python.org/library/urlparse.html
            self.baseurl = urlparse(baseurl)
            self.bucket_name = re.match('(.*)\.s3.*\.amazonaws\.com', self.baseurl[1]).group(1)
            self.key_prefix = self.baseurl[2][1:]

        def _handle_s3(self, awsAccessKey, awsSecretKey):
            self.s3 = boto.connect_s3(awsAccessKey, awsSecretKey)

        def _dump_attributes(self):
            self.logger.debug("baseurl: %s" % str(self.baseurl))
            self.logger.debug("bucket: %s" % self.bucket_name)
            self.logger.debug("key_prefix: %s" % self.key_prefix)

        def _key_name(self,url):
            self.logger.debug("_key_name url=%s, key_prefix=%s" % (url, self.key_prefix))

            if not url.startswith("http://"):
                key = "%s/%s" %  (self.key_prefix, url)
            else:
                key = urlparse(url)[2]

            self.logger.debug("_key_name(%s) -> %s" % (url, key))
            return key

        def _key(self, key_name):
            self.logger.debug("_key(%s)" % key_name)
            bucket = self.s3.get_bucket(self.bucket_name)

            return bucket.get_key(key_name)

        def urlgrab(self, url, filename=None, **kwargs):
            """urlgrab(url) copy the file to the local filesystem"""

            self.logger.debug("urlgrab(url='%s',filename='%s')" % (url, filename))

            key_name = self._key_name(url)
            key = self._key(key_name)

            if not key:
                raise Exception("Can not get key for key=%s" % key_name )
            if not filename:
                filename = key.key

            key.get_contents_to_filename(filename)
            return filename

        def urlopen(self, url, **kwargs):
            """urlopen(url) open the remote file and return a file object"""

            self.logger.debug("urlopen(%s)" % url)
            return self._key(url)

        def urlread(self, url, limit=None, **kwargs):
            """urlread(url) return the contents of the file as a string"""

            self.logger.debug("urlread(%s)" % url)
            return self._key(url).read()

    return BotoGrabber

def createGrabber():
    logger = logging.getLogger("yum.verbose.main")
    try:
        try:
            grabber = createBotoGrabber()
            logger.debug("Using BotoGrabber")
        except:
            grabber = createUrllibGrabber()
            logger.debug("Using UrllibGrabber")
    finally:
        return grabber

AmazonS3Grabber = createGrabber()

class AmazonS3Repo(YumRepository):
    """
    Repository object for Amazon S3.
    """

    def __init__(self, repoid):
        YumRepository.__init__(self, repoid)
        self.enable()
        self.grabber = None

    def setupGrab(self):
        YumRepository.setupGrab(self)
        self.grabber = AmazonS3Grabber(self.key_id, self.secret_key )

    def _getgrabfunc(self): raise Exception("get grabfunc!")
    def _getgrab(self):
        if not self.grabber:
            self.grabber = AmazonS3Grabber(self.key_id, self.secret_key, baseurl=self.baseurl )
        return self.grabber

    grabfunc = property(lambda self: self._getgrabfunc())
    grab = property(lambda self: self._getgrab())


__revision__ = "1.0.0"
requires_api_version = '2.5'
plugin_type = TYPE_CORE

def config_hook(conduit):
    logger = logging.getLogger("yum.verbose.main")
    config.RepoConf.s3_enabled = config.BoolOption(False)
    config.RepoConf.key_id = config.Option() or conduit.confString('main', 'aws_access_key_id')
    config.RepoConf.secret_key = config.Option() or conduit.confString('main', 'aws_secret_access_key')

def init_hook(conduit):
    """
    Plugin initialization hook. Setup the S3 repositories.
    """

    repos = conduit.getRepos()
    conf = conduit.getConf()
    cachedir = conduit.getConf().cachedir

    for key,repo in repos.repos.iteritems():
        if isinstance(repo, YumRepository) and repo.s3_enabled:
            new_repo = AmazonS3Repo(key)
            new_repo.name = repo.name
            new_repo.baseurl = repo.baseurl
            new_repo.mirrorlist = repo.mirrorlist
            new_repo.basecachedir = repo.basecachedir
            new_repo.gpgcheck = repo.gpgcheck
            new_repo.gpgkey = repo.gpgkey
            new_repo.proxy = repo.proxy
            new_repo.enablegroups = repo.enablegroups
            new_repo.key_id = repo.key_id
            new_repo.secret_key = repo.secret_key
            if hasattr(repo, 'priority'):
                new_repo.priority = repo.priority
            if hasattr(repo, 'base_persistdir'):
                new_repo.base_persistdir = repo.base_persistdir

            repos.delete(repo.id)
            repos.add(new_repo)
