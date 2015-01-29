"""A module for pushing blog photos out to s3."""
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from boto.s3.bucket import Bucket as S3Bucket

def upload(fnm):
    """Uploads a single file to the configured s3 bucket.

    Params:
      fnm - Absolute path to upload


    pass
