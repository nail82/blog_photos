#!/usr/bin/env python
"""This script is a driver to upload blog photos to S3.

Input is a simple text file of image files and output
is another file of image tags to be pasted into the blog.
"""
import sys
import os
import blog_upload as bu
import datetime as dt

OUTPUT_DIR = os.getenv("HOME") + "/tmp"
OUTPUT_FNM = os.sep.join(
    [OUTPUT_DIR,
     dt.datetime.strftime(
         dt.datetime.utcnow(),
            '%Y-%m-%d-blog.tags')])

def main():
    if len(sys.argv) < 2:
        print("Need a filename")
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print(sys.argv[1] + " doesn't seem to exist.")
        sys.exit(1)

    cfg = "/Users/tsatcher/.s3_backup/blog_config.ini"
    path_func = bu.make_path_func(cfg)

    access, secret = bu.get_keys(cfg)
    link_func = bu.make_link_func(bu.get_bucket(cfg))

    image_list = open(sys.argv[1]).readlines()
    image_list = [x.strip() for x in image_list]

    abs_image_list = [path_func(x) for x in image_list]
    image_shapes = [bu.get_image_shape(x) for x in abs_image_list]
    blog_shapes = [bu.image_blog_shape(x) for x in image_shapes]
    links = [link_func(x) for x in image_list]
    link_shape_data = [v for v in zip(links, blog_shapes)]
    tags = [bu.image_tag(x) for x in link_shape_data]

    print("Uploading files...")

    conn = bu.open_s3_connection(access, secret)
    upload_func = bu.make_upload_func(bu.get_bucket(cfg), conn)
    uploaded = [upload_func(x) for x in abs_image_list]

    output = open(OUTPUT_FNM, 'w')
    output.write(os.linesep.join(tags))
    output.write(os.linesep)
    output.close()
    print("Tag output in " + OUTPUT_FNM)



if __name__ == "__main__":
    main()
