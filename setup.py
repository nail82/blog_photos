#!/usr/bin/env python
from setuptools import setup

setup(
    name         = "blog_upload",
    version      = "0.3",
    author       = "Ted Satcher",
    author_email = "ted.satcher@gmail.com",
    packages     = ['blog_upload'],
    scripts      = ['blog_tags.py'],
    requires     = ['numpy','boto','PIL','pandas'],
)
