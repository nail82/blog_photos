import PIL.Image as Image
import re
import datetime as dt
import os
import os.path

def jpeg_timestamp(tags):
    return dt.datetime.strptime(tags[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H-%M-%S')

def new_name(fnm):
    path = os.path.dirname(fnm)
    im = Image.open(fnm)
    tags = im._getexif()
    return os.sep.join([path, jpeg_timestamp(tags) + ".jpg"])

def zip_names(files):
    new_names = [new_name(x) for x in files]
    return [v for v in zip(files, new_names)]

def rename_files(zip_list):
    for v in zip_list:
        os.rename(v[0], v[1])
