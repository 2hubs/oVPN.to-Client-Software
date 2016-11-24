# -*- coding: utf-8 -*-
#
# HASH_DLLS

import os
import sys
import time
import json
import types
import hashlib
import threading
import subprocess
import struct

SBITS = struct.calcsize("P") * 8

if not SBITS == 32 and not SBITS == 64:
    print("read bits from sys.argv[1]")
    if len(sys.argv) > 1:
        if sys.argv[1] == "32":
            BITS = 32
        elif sys.argv[1] == "64":
            BITS = 64
        else:
            print("HASH_DLLS: missing bits")
            sys.exit()
else:
    BITS = SBITS
    print("read bits %s from struct" % (BITS))

class HASH_DLLS:
    def __init__(self):
        if self.self_vars():
            if os.path.isfile(self.DLL_DBF_HASH_UNSIGNED) and os.path.isfile(self.DLL_DBF_HASH_SIGNED):
                if self.load_hash_dbf():
                    if self.verify_files():
                        pass
            else:
                if self.hash_files():
                    if self.write_hash_dbf():
                        sys.exit()
        else:
            print("init failed")
            sys.exit()

    def self_vars(self):
        self.HASHS_DB = {}
        self.DLL_DIR = "includes\\DLL\\%s" % (BITS)
        self.DLL_DIR_SIGNED = "%s\\signed" % (self.DLL_DIR)
        self.DLL_DIR_UNSIGNED = "%s\\unsigned" % (self.DLL_DIR)
        self.DLL_DBF_HASH_SIGNED = "%s\\dll_hashs_signed.json" % (self.DLL_DIR)
        self.DLL_DBF_HASH_UNSIGNED = "%s\\dll_hashs_unsigned.json" % (self.DLL_DIR)
        
        self.DLL_DIRS = { "UNSIGNED":self.DLL_DIR_UNSIGNED,"SIGNED":self.DLL_DIR_SIGNED }
        self.DLL_HASH_DBS = { "UNSIGNED":self.DLL_DBF_HASH_UNSIGNED,"SIGNED":self.DLL_DBF_HASH_SIGNED }
        try:
            if not os.path.isdir(self.DLL_DIR):
                print("please create dir '%s'" % (self.DLL_DIR))
                return False
                
            if not os.path.isdir(self.DLL_DIR_SIGNED):
                print("please create dir '%s'" % (self.DLL_DIR_SIGNED))
                return False
                
            if not os.path.isdir(self.DLL_DIR_UNSIGNED):
                print("please create dir '%s'" % (self.DLL_DIR_UNSIGNED))
                return False
        except:
            print("could not create working dirs")
            sys.exit()
        print("def self_vars: return True")
        return True

    def load_hash_dbf(self):
        for key,file in self.DLL_HASH_DBS.items():
            if os.path.isfile(file):
                fp = open(file,"rt")
                HASHS_DB = {}
                HASHS_DB[key] = json.loads(str(fp.read()))
                fp.close()
                if len(HASHS_DB[key]) > 0:
                    self.HASHS_DB[key] = HASHS_DB[key]
                    print("def load_hash_dbf: key '%s', file = '%s' len = '%s' OK" % (key,file,len(self.HASHS_DB[key])))
            else:
                print("def load_hash_dbf: key '%s', file = '%s' not found" % (key,file))
        return True

    def write_hash_dbf(self):
        for key,file in self.DLL_HASH_DBS.items():
            try:
                tmpfile = "%s.tmp" % (file)
                if len(self.HASHS_DB[key]) > 0:
                    fp = open(tmpfile, "wt")
                    fp.write(json.dumps(self.HASHS_DB[key], ensure_ascii=True))
                    fp.close()
                    with open(file, "wt") as fout:
                        with open(tmpfile, "rt") as fin:
                            for line in fin:
                                fout.write(line.replace(',', ',\n'))
                    os.remove(tmpfile)
                    print("def write_hash_dbf: write key '%s', file = '%s' OK" % (key,file))
            except:
                print("def write_hash_dbf: write key '%s', file = '%s' failed!" % (key,file))
                return False
        return True

    def hash_sha512_file(self,file):
        if os.path.isfile(file):
            hasher = hashlib.sha512()
            fp = open(file, 'rb')
            with fp as afile:
                buf = afile.read()
                hasher.update(buf)
            fp.close()
            hash = hasher.hexdigest()
            return hash

    def list_files(self,dir):
        files = []
        content = os.listdir(dir)
        for file in content:
            if file.endswith('.dll') or file.endswith('.pyd'):
                filepath = "%s\\%s" % (dir,file)
                files.append(filepath)
        return files

    def hash_files(self):
        for key,dir in sorted(self.DLL_DIRS.items()):
            if os.path.exists(dir):
                files = {}
                hash_files = self.list_files(dir)
                if len(hash_files) > 0:
                    print("def hash_files: dir = '%s'" % (dir))
                    for file in hash_files:
                        if os.path.isfile(file):
                            hash = self.hash_sha512_file(file)
                            if len(hash) == 128:
                                print("def hash_files: hashed file = '%s' hash = '%s'" % (file,hash))
                                file = file.split("\\")[-1]
                                files[file] = hash
                            else:
                                print("def hash_files: filepath '%s' failed" % (filepath))
                                sys.exit()
                self.HASHS_DB[key] = files
        return True

    def verify_files(self):
        for key,dir in self.DLL_DIRS.items():
            if os.path.exists(dir):
                notfound, verified, failed, missing  = 0, 0, 0, 0
                verify_files_indir = self.list_files(dir)
                
                try:
                    verify_files_store = self.HASHS_DB[key]
                except:
                    verify_files_store = {}
                
                if len(verify_files_indir) > 0:
                    print("\ndef verify_files: dir = '%s' vs. file '%s'" % (dir,self.DLL_HASH_DBS[key]))
                    
                    for file in verify_files_store:
                        fileshort = file.split("\\")[-1]
                        filepath = "%s\\%s" % (dir,file)
                        if not filepath in verify_files_indir:
                            notfound +=1
                            print("def verify_files: file = '%s' FILE NOTFOUND" % (filepath))
                    
                    for file in verify_files_indir:
                        fileshort = file.split("\\")[-1]
                        if fileshort in self.HASHS_DB[key]:
                            hash = self.hash_sha512_file(file)
                            if self.HASHS_DB[key][fileshort] == hash:
                                verified += 1
                                #print("def verify_files: file = '%s' hash = '%s' HASH OK" % (file,hash))
                            else:
                                failed += 1
                                print("def verify_files: file = '%s' hash = '%s' HASH FAILED" % (file,hash))
                        else:
                            missing += 1
                            print("def verify_files: file = '%s' MISSING JSON" % (file))
                print("def verify_files: key '%s' dir = '%s' filesindir = '%s' filesjson = '%s' missing = '%s' notfound = '%s' failed = '%s' verified = '%s'" % (key, dir, len(verify_files_indir), len(verify_files_store), missing, notfound, failed, verified))
        return True

def app():
    HASH_DLLS()

if __name__ == "__main__":
    app()
