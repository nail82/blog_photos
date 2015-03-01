#!/usr/bin/env python
"""This script is a driver to upload blog photos to S3.

Input is a simple text file of image files and output
is another file of image tags to be pasted into the blog.
"""
import sys
import os
import blog_upload as bu
import datetime as dt
from pandas import Series
import numpy as np

def main():
    if len(sys.argv) < 2:
        print("Need a filename")
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print(sys.argv[1] + " doesn't seem to exist.")
        sys.exit(1)

    cfg = "/Users/tsatcher/.s3_backup/blog_config.ini"

    OUTPUT_DIR = bu.get_temp(cfg)
    OUTPUT_FNM = os.sep.join(
        [OUTPUT_DIR,
         dt.datetime.strftime(
             dt.datetime.utcnow(),
                 '%Y-%m-%d-%H%M%S-blog.tags')])

    access, secret = bu.get_keys(cfg)
    # Make some helper functions
    link_func = bu.make_link_func(bu.get_bucket(cfg))
    path_func = bu.make_path_func(cfg)
    def caption_split_func(x):
        try:
            return x.split('|')[1].strip()
        except IndexError as e:
            return ''

    # Read the file
    lines = open(sys.argv[1]).readlines()

    # Filter empty lines
    lines = [l.strip() for l in lines if l.strip() != '']

    # Extract the file data
    image_list = [x.split('|')[0].strip() for x in lines]
    caption_list = Series([caption_split_func(x) for x in lines])

    # Resolve and validate the image files
    abs_image_list = Series([path_func(x) for x in image_list])
    valid_idx = np.array([bu.validate_file(x) for x in abs_image_list])

    # Check for valid files
    if sum(valid_idx) != len(abs_image_list):
        print("Hit " + str(len(abs_image_list) - sum(valid_idx)) + " invalid files:")
        invalid_list = abs_image_list[~valid_idx]
        for f in invalid_list:
            print(f)
        sys.exit(1)

    # Image filenames become image shapes
    image_shapes = [bu.get_image_shape(x) for x in abs_image_list]
    # Image shapes become blog shapes
    blog_shapes = [bu.image_blog_shape(x) for x in image_shapes]
    # Non-absolute image names become links
    links = [link_func(x) for x in image_list]
    # Links and blog shapes become image hrefs
    image_tags = [bu.image_tag(x) for x in zip(links, blog_shapes)]
    # Captions become tags
    captions = [bu.make_caption_tag(x) for x in caption_list]
    # Image and caption tags become blog html
    blog_html_list = [bu.wrap_image_link(x) for x in zip(image_tags, captions)]

    print("Uploading files...")

    conn = bu.open_s3_connection(access, secret)
    upload_func = bu.make_upload_func(bu.get_bucket(cfg), conn)
    uploaded = [upload_func(x) for x in abs_image_list]

    output = open(OUTPUT_FNM, 'w')
    output.write(os.linesep.join(blog_html_list))
    output.write(os.linesep)
    output.close()
    print("Tag output in " + OUTPUT_FNM)



if __name__ == "__main__":
    main()
