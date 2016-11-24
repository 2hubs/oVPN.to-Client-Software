# -*- coding: utf-8 -*-
import os, hashlib

# .py file imports
from debug import debug


def hash_sha512_file(DEBUG,file):
    debug(1,"[hashings.py] def hash_sha512_file()",DEBUG,True)
    if os.path.isfile(file):
        hasher = hashlib.sha512()
        fp = open(file, 'rb')
        with fp as afile:
            buf = afile.read()
            hasher.update(buf)
        fp.close()
        return hasher.hexdigest()

def hash_sha256_file(DEBUG,file):
    debug(1,"[hashings.py] def hash_sha256_file()",DEBUG,True)
    if os.path.isfile(file):
        hasher = hashlib.sha256()
        fp = open(file, 'rb')
        with fp as afile:
            buf = afile.read()
            hasher.update(buf)
        fp.close()
        return hasher.hexdigest()