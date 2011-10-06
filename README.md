A yum-s3 a s3-plugin for yum.

# Motivation

It is very convenient to run a yum-repository on S3. Using createrepo
and the awesome s3cmd (https://github.com/s3tools/s3cmd), is basically
all you need. However, this only works for public repositories ...

# Public vs. protected repositories

## Public repositories

- enable "website feature" of your s3 bucket
- you dont need the s3-plugin. Everything works out of the box

## Protected repositories

This is where yum-s3 kicks in. yum-s3 uses the Boto library to fetch
objects from S3, which allows using credentials.

# Install

- run ./package to build a RPM
- install

# How to configure a S3 based repo

    [n4repoprivate-pool-noarch]
    name=repoprivate-pool-noarch
    baseurl=http://<YOURBUCKET>.s3-website-eu-west-1.amazonaws.com/<YOURPATH>
    enabled=1
    gpgcheck=0
    priority=1
    s3_enabled=1
    key_id=<YOURKEY>
    secret_key=<YOURSECRET>

# YUM edge cases (baseurl)

The is a flaw/issue/bug in yum, that stops yum-s3 from working, when
you use a createrepo with a baseurl.

## Why should I want to do this?

Suppose you have different environments (CI, testing, production). You
want to upload the RPM only once to save outgoing bandwidth. Normally
you could create symlinks on a webserver, but this is not possible
with S3. But Yum offers a dedicated feature (baseurl), what can be
used to make this possible.

## Repository layout with "pool"

    repo/
         pool/
              i386/
                   myprogram-1.0.rpm
                   myprogram-1.1.rpm
                   myprogram-1.2.rpm
         env/
             CI/
                myprogram-1.2.rpm -> ../../pool/i386/myprogram-1.2.rpm
             testing/
                myprogram-1.1.rpm -> ../../pool/i386/myprogram-1.1.rpm
             production/
                myprogram-1.0.rpm -> ../../pool/i386/myprogram-1.0.rpm
		   
So when you add a RPM to a repository, you do the following steps

- add the RPM to the /pool directory
- create a symlink in the folder (like CI, testing, production)
- run createrepo with the --baseurl option

This will create the yum xml-files based on the symlinks that are
present. So you can decide with the symlinks at createrepo-time, which
packages are "visible".

Giving the --baseurl option to yum will make yum go the /pool
directory to fetch the actual RPM.

## How do I make yum honour the baseurl?

There is a patch to yum coming soon.

Have fun,
Jens
