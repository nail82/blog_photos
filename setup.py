#!/usr/bin/env python
from setuptools import setup

setup(
    name         = "blog_upload",
    version      = "0.4",
    author       = "Ted Satcher",
    author_email = "ted.satcher@gmail.com",
    packages     = ['bub_blog_upload'],
    scripts      = ['blog_tags.py'],
    requires     = ['numpy','boto','PIL','pandas'],
)
