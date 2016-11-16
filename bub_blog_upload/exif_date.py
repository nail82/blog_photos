import PIL.Image as Image
import re
import datetime as dt
import os
import os.path
import pandas as pd
import pytz

"""
Rename a list of jpgs or other files based on a function of the file.

Example:
  # files is a list of absolute filenames.
  import exif_date as ed
  old_new = ed.zip_old_new(files, ed.stat_timestamp)
  ed.rename_files(old_new)
"""

NAME_RE = re.compile("^complete name", re.IGNORECASE)
DATE_RE = re.compile("^recorded date", re.IGNORECASE)
AUCK_TZ = pytz.timezone("Pacific/Auckland")

def mov_timestamp(fnm):
    """Not working as of yet"""
    assert(False)
    lines = open(fnm,'r').readlines()

    name_filt = lambda x: NAME_RE.search(x) is not None
    date_filt = lambda x: DATE_RE.search(x) is not None

    name_field = [v for v in filter(name_filt, lines)][0].split(':')[1].strip()
    date_list = [v for v in filter(date_filt, lines)][0].split(':')[1:]
    date_field = ':'.join(date_list).strip()
    ts = pd.to_datetime(date_field, utc=True, infer_datetime_format=True).tz_convert(AUCK_TZ)

    return None


    """Return a timestamp as a function of the exif date in on the file."""
    im = Image.open(fnm)
    tags = im._getexif()
    return dt.datetime.strptime(
        tags[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H.%M.%S')

def jpg_timestamp(fnm):
    im = Image.open(fnm)
    tags = im._getexif()
    try:
        return dt.datetime.strptime(
            tags[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H.%M.%S')
    except KeyError as e:
        return "1400-01-01 00.00.00"

def stat_timestamp(fnm):
    """Returns a timestamp as a function of the file mtime."""
    return dt.datetime.fromtimestamp(
        os.stat(fnm).st_mtime).strftime('%Y-%m-%d %H:%M:%S')

def order_files(files, ts_func):
    """Orders a list of file tuples based on their exif timestamp.

    Params:
      files - A list of fully qualified file names.

    Returns:
      A list of (ts_name, old_name) tuples sorted by exif timestamp."""
    ts_names = [ts_func(x) for x in files]
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

def resolve_dups_old(ts_names, prev, suffix, resolved):
    """A recursive function to search and tag duplicates with a numbered suffix.

    Assumes ts_names are sorted in ascending order.

    Params:
      ts_names - An ordered list of timestamp names, which are a function of the
        exif timestamp, file mtimes, or some other function of the file.
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

def resolve_dups(ts_names):
    """An iterative version for resolving dups."""
    suffix = 0
    resolved = ts_names.copy()

    def myjoin(name, suffix):
        if suffix == 0:
            return name
        else:
            return "-".join([name, str(suffix)])

    for i in range(1, len(ts_names)):
        suffix = suffix + 1 if ts_names[i] == ts_names[i-1] else 0
        resolved[i] = myjoin(ts_names[i], suffix)

    return resolved


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

def id(x):
    return x

def strip_log(x):
    pass

def zip_old_new(files, name_func):
    """Entry function for renaming a list of jpgs.

    Params:
      files - A list of absolute path jpg filenames

    Returns:
      A list of (old name, new name) tuples
    """
    ordered_list = order_files(files, name_func)
    (ts_names, old_names, dir_names) = unzip_files(ordered_list)
    resolved = resolve_dups(ts_names)
    new_names = abs_names(dir_names, resolved)

    date_flag_re = re.compile("1400-01-01 00\\.00\\.00")

    def check_date_flag(tup):
        """Check for a year 1400 flag, which signals an inability to
        extract the date from exif data."""
        mo = date_flag_re.search(tup[1])
        return tup if mo is None else (tup[0], tup[0])

    return [check_date_flag(v) for v in zip(old_names, new_names)]

def rename_files(zip_list):
    """Given a list of (old,new) tuples, rename the files.

    Params:
      zip_list - A list of (old name, new name) tuples

    Return:
      void
    """
    for v in zip_list:
        os.rename(v[0], v[1])





def mov_zip_old_new(log_files):
    """Entry function for renaming a list of iphone movs.

    Note, to generate the log files, do something like:

    for f in *.MOV; do mediainfo $f -f --LogFile=$f.log; done

    The log files are key-value pairs, one per line, delimited
    by a colon.  There are some blank lines and some header-ish
    lines in the log file as well.

    The fields we're interested in are "Complete Name" and "Recorded Date"


    Params:
      files - A list of log files generated by mediainfo

    Returns:
      A list of (old name, new name) tuples."""


def test():
    pass



if __name__ == "__main__":
    test()
