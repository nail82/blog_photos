import PIL.Image as Image
import re
import datetime as dt
import os
import os.path
import pandas as pd
import bub

def jpeg_timestamp(tags):
    return dt.datetime.strptime(tags[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H-%M-%S')

def timestamp_name(fnm):
    im = Image.open(fnm)
    tags = im._getexif()
    return jpeg_timestamp(tags)

def order_files(files):
    """Orders a list of file tuples based on their exif timestamp.

    Params:
      files - A list of fully qualified file names.

    Returns:
      A list of (ts_name, old_name) tuples sorted by exif timestamp."""
    ts_names = [timestamp_name(x) for x in files]
    zip_list = [v for v in zip(ts_names, files)]
    key_func = lambda x: x[0]

    # Reorder based on image timestamp
    return sorted(zip_list, key=key_func)

def unzip_files(zip_list):
    """Split an ordered list of (ts_names, old names) tuple list.

    We also fashion a list of path names from the paths on the old_name fields.

    Params:
      zip_list - A list (ts_name, old name) tuples.

    Returns:
      Returns a tuple of lists, ts_names, old_names and dir_names."""
    ts_names = [x[0] for x in zip_list]
    old_names = [x[1] for x in zip_list]
    dir_names = [os.path.dirname(x[1]) for x in zip_list]
    return (ts_names, old_names, dir_names)

def resolve_dups(ts_names, prev, suffix, resolved):
    """A recursive function to search and tag duplicates with a numbered suffix.

    Assumes ts_names are sorted in ascending order.

    Params:
      ts_names - A list of timestamp names, which are a function of the exif timestamp.
      prev - The previous timestamp name.  Set to the empty string to start the recursion.
      suffix - The current suffix value.  Set to 0 to start the recursion.
      resolved - The accumulation list.  Set to the empty list to start the recursion.

    Returns:
      A list of timestamp names with duplicates tagged with numbered suffixes.
    """
    if len(ts_names) == 0:
        resolved.reverse()
        return resolved
    head, *tail = ts_names
    if head != prev:
        resolved = [head] + resolved
        return resolve_dups(tail, head, 0, resolved)
    else:
        suffix = suffix+1
        dup = '-'.join([head, str(suffix)])
        resolved = [dup] + resolved
        return resolve_dups(tail, head, suffix, resolved)


def abs_names(dir_names, resolved):
    """Adds the jpg extension and fully qualifies new names.

    Params:
      dir_names - A list of directory names.

      resolved - A list of 'resolved' timestamp names.  Resolved, meaning
        duplicates have been tagged with a suffix value.

    Returns:
      A list of fully qualified, valid jpg filenames
    """
    new_names = []
    for i in range(len(dir_names)):
        new_names.append(os.sep.join([dir_names[i], resolved[i] + ".jpg"]))
    return new_names

def zip_old_new(files):
    """Entry function for renaming a list of jpegs

    Params:
      files - A list of absolute path jpg filenames

    Returns:
      A list of (old name, new name) tuples
    """
    ordered_list = order_files(files)
    (ts_names, old_names, dir_names) = unzip_files(ordered_list)
    resolved = resolve_dups(ts_names, "", 0, [])
    new_names = abs_names(dir_names, resolved)
    return [v for v in zip(old_names, new_names)]

def rename_files(zip_list):
    """Given a list of (old,new) tuples, rename the files.

    Params:
      zip_list - A list of (old name, new name) tuples

    Return:
      void
    """
    for v in zip_list:
        os.rename(v[0], v[1])


def test():
    pass





if __name__ == "__main__":
    test()
