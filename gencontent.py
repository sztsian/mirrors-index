#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-

import os
import time
from urllib.parse import urljoin
import requests
import fnmatch

HTTPDIR = '/srv/www'

# Directories match these glob will be ignored.
EXCLUDE = ("tmpfs", ".*")

# A unreliable workaround for nested repos. See comments in main program.
def CTimeWA(dirpath):
    ctime = 0
    for subd in os.listdir(dirpath):
        subdirpath = os.path.join(dirpath, subd)
        if not os.path.isdir(subdirpath):
            continue

        _ctime = os.stat(subdirpath).st_ctime
        if _ctime > ctime:
            ctime = _ctime

    return ctime


def testHelpLink(name):
    URLBASE = "https://lug.ustc.edu.cn/wiki/mirrors/help/"
    url = urljoin(URLBASE, name)

    try:
        html = requests.get(url, timeout = 4)
    except:
        return False

    return False if "该主题尚不存在" in html.text else True

def genRepoList():
    now = time.time()
    for d in sorted(os.listdir(HTTPDIR), key = lambda s: s.lower()):
        fpath = os.path.join(HTTPDIR, d)

        if not os.path.isdir(fpath) or \
                any(fnmatch.fnmatch(d, p) for p in EXCLUDE):
            continue

        # Change time is lastsync time if sync destination is exactly the same
        # top-level dir of http. However, some repos are divided to several
        # sub-dirs which are actually sync-ed instead of top-level directory.
        # We need to check these sub-dirs to find correct lastsync time.
        ctime = os.stat(fpath).st_ctime

        # Since checking all sub-dirs wastes much time, the script just check
        # repos whose top-level dirs have a old change time.
        if time.time() - ctime > 3600*24*2:
            _ctime = CTimeWA(fpath)
            if _ctime > ctime:
                ctime = _ctime

        yield (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ctime)),
               "Help" if testHelpLink(d) else "",
               d)

if __name__ == '__main__':
    for i in genRepoList():
        print(i)