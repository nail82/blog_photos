"""A module for pushing blog photos out to s3."""
import os
import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from boto.s3.bucket import Bucket as S3Bucket
import configparser as cp
import urllib
import functools as ft
from PIL import Image
import numpy as np


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
      A tuple of access_key and secret_key.
    """
    parser = cp.RawConfigParser()
    parser.read(config_fnm)
    defaults = parser.defaults()
    return (defaults["access_key"], defaults["secret_key"])

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
    return fnm if local_size == up_size else ""

def make_upload_func(bucket):
    """Higer order that partially applies a bucket to upload.

    Params:
      bucket - A bucket name

    Returns:
      An upload function with the bucket name frozen.
    """
    return ft.partial(upload, bucket)

def image_link(bucket, fnm):
    baseurl = "https://s3.amazonaws.com"
    urlpath = "/".join([bucket, fnm])
    return urllib.parse.unquote(
        urllib.parse.quote_plus(urllib.parse.urljoin(baseurl, urlpath))) if fnm != '' else ''

def make_link_func(bucket):
    return ft.partial(image_link, bucket)

def image_tag(link_shape_tup):
    image_link, imshape = link_shape_tup
    w,h = imshape
    base_link = """<div class="separator" style="clear: both; text-align: center;"><a href="{0}" imageanchor="1" style="margin-left: 1em; margin-right: 1em;"><img border="0" height="{2}" src="{0}" width="{1}" /></a></div>"""
    return base_link.format(image_link, w, h) if image_link != '' else ''

def image_blog_shape(imshape):
    """Compute blog width and height for an image.

    Params:
      abs_fnm - Absolute path to an image file.

    Returns:
      A tuple of width, height
    """
    LANDSCAPE_WIDTH = 320
    PORTRAIT_WIDTH  = 240
    MAX_WIDTH       = 480

    w,h = imshape
    wh_ratio = float(w) / h

    def compute_scale():
        if wh_ratio < 1:
            return PORTRAIT_WIDTH / w
        if 1 <= wh_ratio < 1.5:
            return LANDSCAPE_WIDTH / w
        return LANDSCAPE_WIDTH / w

    scale = compute_scale()
    return ( int(np.ceil(w*scale)), int(np.ceil(h*scale)) )

def get_image_shape(abs_fnm):
    return Image.open(abs_fnm).size
