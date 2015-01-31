"""This script is a driver to upload blog photos to S3.

Input is a simple text file of image files and output
is another file of image tags to be pasted into the blog.
"""
import sys
import os
import blog_upload as bu

def main():
    if len(sys.argv) < 2:
        print("Need a filename")
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print(sys.argv[1] + " doesn't seem to exist.")
        sys.exit(1)

    lines = open(sys.argv[1]).readlines()
    cfg = "/Users/tsatcher/.s3_backup/blog_config.ini"
    path_func = bu.make_path_func(cfg)
    upload_func = bu.make_upload_func(bu.get_bucket(cfg))
    access, secret = bu.get_keys(cfg)
    link_func = bu.make_link_func(bu.get_bucket(cfg))

if __name__ == "__main__":
    main()
