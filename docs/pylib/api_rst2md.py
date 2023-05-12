#!/usr/bin/python
"""
Remap autodoc API rst files to md files and wrap their contents.

"""

from glob import glob
from os import rename
from os.path import abspath, dirname
from os.path import join as pathjoin


def _rst2md(filename_rst):

    with open(filename_rst, "r") as fil:
        # read rst file, reformat and save
        txt = fil.read()
    with open(filename_rst, "w") as fil:
        txt = "```{eval-rst}\n" + txt + "\n```"
        fil.write(txt)

    # rename .rst file to .md file
    filename, _ = filename_rst.rsplit(".", 1)
    filename_md = f"{filename}.md"
    rename(filename_rst, filename_md)


if __name__ == "__main__":
    apidir = pathjoin(dirname(dirname(abspath(__file__))), "source", "api")
    for filename_rst in glob(pathjoin(apidir, "*.rst")):
        _rst2md(filename_rst)
    print(" Converted {apidir}/*.rst files to .md files".format(apidir=apidir))
