import PIL.Image as Image
import re
import datetime as dt
import os
import os.path
import pandas as pd

def jpeg_timestamp(tags):
    return dt.datetime.strptime(tags[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H-%M-%S')

def new_name(fnm):
    path = os.path.dirname(fnm)
    im = Image.open(fnm)
    tags = im._getexif()
    return jpeg_timestamp(tags)

def zip_names(files):
    new_names = [new_name(x) for x in files]
    return [v for v in zip(files, new_names)]

def rename_files(zip_list):
    for v in zip_list:
        os.rename(v[0], v[1])


def resolve_dups(new_names, prev, suffix, resolved):
    if len(new_names) == 0:
        resolved.reverse()
        return resolved
    head, *tail = new_names
    if head != prev:
        resolved = [head] + resolved
        return resolve_dups(tail, head, 0, resolved)
    else:
        suffix = suffix+1
        dup = '-'.join([head, str(suffix)])
        resolved = [dup] + resolved
        return resolve_dups(tail, head, suffix, resolved)

def test():
    w = ["2015-03-08 10-08-51",
         "2015-03-08 10-08-51",
         "2015-03-08 10-09-32",
         "2015-03-08 10-09-37",
         "2015-03-08 10-09-44",
         "2015-03-08 10-09-49",
         "2015-03-08 10-10-03",
         "2015-03-08 10-10-25",
         "2015-03-08 10-11-57",
         "2015-03-08 10-32-11",
         "2015-03-08 10-32-11",
         "2015-03-08 10-32-11"]

    resolved = resolve_dups(w, "", 0, [])
    print(resolved)


if __name__ == "__main__":
    test()
