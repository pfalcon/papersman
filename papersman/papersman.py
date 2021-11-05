# papersman - Minimalist electronic documents manager
#
# Copyright (c) 2020 Paul Sokolovsky
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import ubinascii
import uhashlib
import ure
import argparse
import os
import os.path
import glob
import shutil
from collections import defaultdict
from pprint import pprint

import yaml
from utemplate.recompile import Loader


tmpl_loader = Loader(__name__.split(".", 1)[0], ".")


def replace_ext(fname, new):
    return fname.rsplit(".", 1)[0] + new


def backup_file(fname):
    try:
        os.rename(fname, fname + ".bak")
    except OSError:
        pass


def hash_file(fname):
    with open(fname, "rb") as f:
        buf = bytearray(64 * 1024)
        hsh = uhashlib.md5()
        while True:
            sz = f.readinto(buf)
            if not sz:
                break
            hsh.update(memoryview(buf)[:sz])
    return ubinascii.hexlify(hsh.digest()).decode()


# Utility functions for tags. Wrapped in a class namespace to pass to
# templates as a whole namespace, instead of one by one.
class TagFuncs:

    def tag2id(tag):
        return tag.replace(":", "_")

    def tag2url(tag):
        return "index/%s.html" % TagFuncs.tag2id(tag)

    def tag2classes(tag):
        classes = []
        while True:
            classes.append("tag-" + TagFuncs.tag2id(tag))
            super_tag = tag.rsplit(":", 1)[0]
            if super_tag == tag:
                break
            tag = super_tag
        return " ".join(classes)


def write_index(fname, doc_list, **extra):
    tmpl = tmpl_loader.load("index.tpl")
    relpath = ".." if "/" in fname else "."
    doc_list.sort(key=lambda d: d.get("pubdate", "_"))
    with open(fname, "w") as outf:
        for x in tmpl(TagFuncs, doc_list, relpath, extra):
            outf.write(x)


def cmd_add(args):
    for fname in args.file:
        if os.path.isdir(fname):
            print("Warning: '%s' is a directory, skipping" % fname)
            continue
        try:
            hsh = hash_file(fname)
        except Exception as e:
            print("Error: unable to hash '%s', skipping: %s" % (fname, e))
            continue

        meta_fname = replace_ext(fname, ".yaml")
        if fname == meta_fname:
            print("Warning: skipping '%s'" % fname)

        d = {}
        if os.path.exists(meta_fname):
            with open(meta_fname) as f:
                d = yaml.safe_load(f)
            backup_file(meta_fname)

        d["name"] = fname
        d["md5"] = hsh
        # If fname starts with date
        m = ure.match(r"[0-9]+", fname)
        if m and len(m.group(0)) in (4, 6, 8):
            s = m.group(0)
            date = s[:4]
            s = s[4:]
            if s:
                date += "-" + s[:2]
                s = s[2:]
            if s:
                date += "-" + s[:2]
                s = s[2:]
            d["pubdate"] = date

        with open(meta_fname, "w") as metaf:
            yaml.dump(d, metaf, sort=True)


def cmd_index(args):
    doc_list = []
    tagmap = defaultdict(list)
    idmap = {}

    for metaf in glob.iglob("**/*.yaml", recursive=True):
        print(metaf)
        with open(metaf) as f:
            d = yaml.safe_load(f)
        path = os.path.dirname(metaf)
        d["path"] = path + "/" + d["name"]
        for a in d.get("authors", ()):
            d.setdefault("tags", []).append("author:" + a)
        doc_list.append(d)
        for tag in d["tags"]:
            tagmap[tag].append(d)
        idmap[d["md5"]] = d
        for docid in d.get("ids", ()):
            idmap[docid] = d

    write_index("index.html", doc_list, tagmap=tagmap, idmap=idmap)

    try:
        os.makedirs("index")
    except OSError:
        pass
    for tag, doc_list in tagmap.items():
        write_index(
            TagFuncs.tag2url(tag), doc_list,
            header="Documents with '%s' tag" % tag,
            idmap=idmap
        )

    basedir = os.path.dirname(__file__)
    shutil.copyfile(basedir + "/style.css", "index/style.css")
    shutil.copyfile(basedir + "/tags.css", "index/tags.css")


def __main__():
    argp = argparse.ArgumentParser(description="Electronic document manager")
    argp.add_argument("cmd")
    argp.add_argument("file", nargs="*")
    args = argp.parse_args()

    if args.cmd == "add":
        cmd_add(args)
    elif args.cmd == "index":
        cmd_index(args)
    else:
        argp.error("Unknown command: %s" % args.cmd)


if __name__ == "__main__":
    __main__()
