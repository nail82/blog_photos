"""A module for pushing blog photos out to s3."""
import os
import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from boto.s3.bucket import Bucket as S3Bucket
import configparser as cp
import urllib
import functools as ft

def open_s3_connection(access_key, secret):
    """Opens and returns a connection to s3

    Params:
      access_key - Access key from config.
      secret_key - Secret key from config.

    Returns:
      connection - A connection to S3
    """
    return S3Connection(access_key, secret)


def get_keys(config_fnm):
    """Parses a config file and returns s3 credentials.

    Params:
      config_fnm - Name of the config file

    Returns:
      dict - A dictionary with acces_key and secret_key
    """
    parser = cp.RawConfigParser()
    parser.read(config_fnm)
    defaults = parser.defaults()
    return {"access_key": defaults["access_key"],
            "secret_key": defaults["secret_key"]}

def get_bucket(config_fnm):
    """Get the config bucket name.

    Params:
      config_fnm - Name of the config file

    Returns:
      string - The configured bucket name
    """
    parser = cp.RawConfigParser()
    parser.read(config_fnm)
    defaults = parser.defaults()
    return defaults["bucket"]

def make_path_func(config_fnm):
    """A higher-order function to parse a bare image filename.

    Takes input from the config for the location of photos.

    Param:
      config_fnm - Name of the config file

    Returns:
      function - A unary function accepting a filename in the
        form of YYYY-MM-DD HH:MM:SS
    """
    parser = cp.RawConfigParser()
    parser.read(config_fnm)
    defaults = parser.defaults()
    local_dir = defaults["local_dir"]
    def f(fnm):
        ym = ''.join(fnm.split('-')[0:2])
        return os.sep.join([local_dir, ym, fnm])
    return f

def upload(bucket, abs_fnm, s3conn):
    """Uploads a single file to the configured s3 bucket.

    A file is stored in reduced redundancy, with
    public-read acl.

    Params:
      abs_fnm - Absolute path to our file
      bucket - Bucket name we're uploading to
      s3conn - A connection to S3

    Returns:
      link - The public link to the uploaded object, or an
      empty string if the upload didn't complete.
    """
    fnm = os.path.basename(abs_fnm)
    b = S3Bucket(connection=s3conn, name=bucket)
    k = S3Key(b)
    k.key = fnm
    local_size = os.stat(abs_fnm).st_size
    up_size = k.set_contents_from_filename(
          abs_fnm
        , reduced_redundancy=True
        , policy="public-read")
    baseurl = "https://s3.amazonaws.com"
    urlpath = "/".join([bucket, fnm])
    url = urllib.parse.urljoin(baseurl, urlpath)
    plus = urllib.parse.unquote(urllib.parse.quote_plus(url))
    return plus if local_size == up_size else ""

def bucket_upload_func(bucket):
    """Higer order that partially applies a bucket to upload.

    Params:
      bucket - A bucket name

    Returns:
      An upload function with the bucket name frozen.
    """
    return ft.partial(upload, bucket)
