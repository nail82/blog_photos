#!/usr/bin/env python3
"""
Quickly rename jpgs from their camera assigned name
to a name like dropbox would assign.
"""
from bub_blog_upload import exif_date as ed
import argparse
import os


def main():
    usage = """%prog <xxxxx.jpg...> [--dry-run]
\nThis is a quick script to rename jpg files off the Panasonic Lumix
camera to a timestamped name to prevent name collisions.  Best to move the files
off the camera in a temp location, use this script and then move them to where
they belong.
"""
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('dir', help='file/list/dir',nargs='+')
    parser.add_argument("--dry-run",dest="dry_run",
                      help="Print what would have been done.",
                      action="store_true")
    args = parser.parse_args()

    files = assemble_files(args)

    old_new = ed.zip_old_new(files, ed.jpg_timestamp)

    if args.dry_run:
        for t in old_new:
            print(t[0], t[1])
    else:
        ed.rename_files(old_new)


def assemble_files(args):
    """Gathers a list of filenames"""
    rtn = []

    if len(args.dir) > 1:
        # This is presumed to be a list of files
        rtn.extend(args.dir)
    else:
        # check if we have a file
        if os.path.isfile(args.dir[0]):
            rtn.append(args.dir[0])
        elif os.path.isdir(args.dir[0]):
            for (path, dirs, files) in os.walk(args.dir[0]):
                rtn.extend([os.sep.join([path,f]) for f in files])
        else:
            print('Need to pass in a directory/file/list of files')
            sys.exit(1)
    return rtn


if __name__ == "__main__":
    main()
