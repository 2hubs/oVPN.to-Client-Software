# -*- coding: utf-8 -*-
#
# 
# OpenVPN_HashBinsToJson v0.0.1

from datetime import datetime as datetime
import os
import sys
import types
import hashlib
import random
import subprocess
import threading
import requests
import json


class OpenVPN_HashBinsToJson:
    def __init__(self):
        if self.self_vars():
            #if self.load_hash_dbf():
            if self.files_downloader():
                if self.write_hash_dbf():
                    sys.exit()
                    #print "self.HASHS_DB = '%s'" % (self.HASHS_DB)
        else:
            print "init failed"
            sys.exit()

    def self_vars(self):
    
        self.SEVENZIP = "C:\\Program Files\\7-Zip\\7z.exe"
        self.SEVENZIP_VERBOSITY = 1
        self.GNUPGBIN = "gpg.exe"
        
        self.OPENVPN_HTTP = "https://swupdate.openvpn.org/community/releases"
        self.OPENVPN_PGPG = "samuli_public_key.asc"
        self.OPENVPN_HASH = "6644a61a1bb3b796957d4add6a28a02137ec9f09c886c6a42233b0dafd9030ed3fda8ab05dcc82783223277b6e71e200dd665bac220e9ee747626c3cb1b6346d"
        self.DOWNLOAD_ASC = True
        
        self.OPENVPN_ARCHS = ["i686","x86_64"]
        self.OPENVPN_BINS = [ "2.3.12:I601","2.3.12:I602","2.3.13:I601" ]
        
        self.WORKING_DIR = "files"
        self.STORAGE_DIR = "%s/openvpn" % (self.WORKING_DIR)
        self.STORAGE_TMP = "%s/tmp" % (self.STORAGE_DIR)
        self.EXTRACT_DIR = "%s/extract" % (self.STORAGE_DIR)
        
        self.HASHS_DB = {}
        self.HASH_DBF = "%s/hashs.dbf" % (self.STORAGE_DIR)

        try:
            if not os.path.isdir(self.WORKING_DIR):
                os.mkdir(self.WORKING_DIR)

            if not os.path.isdir(self.STORAGE_DIR):
                os.mkdir(self.STORAGE_DIR)

            if not os.path.isdir(self.STORAGE_TMP):
                os.mkdir(self.STORAGE_TMP)

            if not os.path.isdir(self.EXTRACT_DIR):
                os.mkdir(self.EXTRACT_DIR)

            if not os.path.isfile(self.SEVENZIP):
                print "7-zip not found"
                sys.exit()

            if not os.path.isfile(self.GNUPGBIN):
                print "gpg not found"
                sys.exit()

        except:
            print "could not create working dirs"
            sys.exit()
        
        #print "self.self_vars loaded"
        if self.gpg_import_pubkey():
            return True

    def load_hash_dbf(self):
        if os.path.isfile(self.HASH_DBF):
            fp = open(self.HASH_DBF,"rb")
            self.HASHS_DB = json.loads(fp.read())
            fp.close()
            print "def load_hash_dbf: loaded self.HASHS_DB = '%s'" % (self.HASH_DBF)
            return True 
        else:
            #print "def load_hash_dbf: self.HASHS_DB = '%s' failed, pass" % (self.HASHS_DB)
            return True 

    def write_hash_dbf(self):
        try:
            fp = open(self.HASH_DBF, "wb")
            fp.write(json.dumps(self.HASHS_DB, ensure_ascii=False))
            fp.close()
            print "DATABASE written to: '%s'" % (self.HASH_DBF)
            return True
        except:
            print "def write_hash_dbf: failed!"
            return False

    def files_downloader(self):
        for BIN in self.OPENVPN_BINS:
            version = BIN.split(':')[0]
            built = BIN.split(':')[1]
            for arch in self.OPENVPN_ARCHS:
                filename = self.openvpn_filename_exe(version,built,arch)
                url = "%s/%s" % (self.OPENVPN_HTTP,filename)
                self.download_file(url,filename)
                
        return True

    def download_file(self,url,filename):
        try:
            savefileto = "%s/%s" % (self.STORAGE_DIR,filename)
            try:
                if not os.path.isfile(savefileto):
                    print "\nDownloading '%s'" % (filename)
                    r = requests.get(url)
                    bytes = len(r.content)
                    try:
                        if bytes < 1600000:
                            print "Downloaded '%s' (%s bytes) is too small, skipping...\n" % (filename,bytes)
                            if bytes < 256:
                                print "r.content = '%s'" % (r.content)
                            return False
                        else:
                            print "Downloaded '%s' (%s bytes)" % (filename,bytes)
                        fp = open(savefileto, "wb")
                        fp.write(r.content)
                        fp.close()
                        if os.path.isfile(savefileto):
                            localhash = self.hash_sha512_file(savefileto)
                            #print "Downloaded '%s' OK! SHA512 = '%s'" % (filename,localhash)
                            if self.DOWNLOAD_ASC:
                                try:
                                    ascfile = self.openvpn_filename_asc(filename)
                                    ascurl = "%s/%s" % (self.OPENVPN_HTTP,ascfile)
                                    saveascto = "%s/%s" % (self.STORAGE_DIR,ascfile)
                                    r = requests.get(ascurl)
                                    try:
                                        bytes = len(r.content)
                                        print "Downloaded '%s' (%s bytes)" % (ascfile,bytes)
                                        fp = open(saveascto, "wb")
                                        fp.write(r.content)
                                        fp.close()
                                        if os.path.isfile(saveascto):
                                            hashasc = self.hash_sha512_file(saveascto)
                                            #print "Downloaded '%s' OK! SHA512 = '%s'\n" % (ascfile,hashasc)
                                            if self.gpg_verify_file(saveascto):
                                                if self.extract_file(savefileto,filename):
                                                    if self.hash_files(filename):
                                                        return True
                                    except:
                                        print "def files_downloader: saving file to '%s' failed!" % (savefileto)
                                except:
                                    print "def files_downloader: downloading '%s' failed!" % (saveascto)
                            else:
                                #print "self.HASHS_DB = '%s'" % (self.HASHS_DB)
                                self.HASHS_DB[filename] = localhash
                                return True
                    except:
                        print "def files_downloader: saving file to '%s' failed!" % (savefileto)
                else:
                    print "\nFile '%s' exists, checking...\n" % (savefileto)
                    print "SHA512 = '%s'" % (self.hash_sha512_file(savefileto))
                    return self.gpg_verify_file("%s.asc"%(savefileto))
            except:
                print "def files_downloader: downloading '%s' failed!" % (filename)
                sys.exit()
            
        except:
            print "def files_downloader: failed"
            sys.exit()

    def gpg_import_pubkey(self):
        if not self.DOWNLOAD_ASC:
            return True
        if not self.hash_sha512_file(self.OPENVPN_PGPG) == self.OPENVPN_HASH:
            print "invalid filehash for key '%s'" % (self.OPENVPN_PGPG)
            return False
        string = "%s --import %s" % (self.GNUPGBIN,self.OPENVPN_PGPG)
        try: 
            with open(os.devnull, "w") as f: 
                exitcode = subprocess.call("%s" % (string),shell=True,stdout=f)
                if exitcode == 0:
                    return True
        except:
            print "def gpg_import_pubkey: failed!"
            return False

    def gpg_verify_file(self,file):
        if not self.DOWNLOAD_ASC:
            return True
        try: 
            string = "%s --verify %s" % (self.GNUPGBIN,file)
            exitcode = subprocess.call("%s" % (string),shell=True)
            print "exitcode = %s\n" % (exitcode)
            if exitcode == 0:
                return True
        except:
            print "def gpg_verify_file: '%s' failed!" % (file)
            return False

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

    def extract_file(self,file,filename):
        try:
            if os.path.isfile(file):
                extractto = "%s/%s" % (self.EXTRACT_DIR,filename)
                #print "extractto = '%s'" % (extractto)
                if not os.path.isdir(extractto):
                    os.mkdir(extractto)
                    
                string = "\"%s\" x \"%s\" -bb1 -bso0 -bse0 -bsp1 -o\"%s\" bin/" % (self.SEVENZIP,file,extractto)
                #print "def extract_file: string = '%s'" % (string)
                
                exitcode = subprocess.call("%s" % (string),shell=True)
                #print "exitcode = %s\n" % (exitcode)
                if exitcode == 0:
                    print "File '%s' extracted to '%s/'" % (filename,extractto)
                    return True
            else:
                print "Could not extract '%s' File not found!" % (file)
                return False
        except:
            print "def extract_setup(self,%s,%s) failed!" % (file,filename)
            return False

    def hash_files(self,filename):
        dir = "%s/%s/bin" % (self.EXTRACT_DIR,filename)
        #print "def hash_files: dir = '%s'" % (dir)
        if os.path.exists(dir):
            content = os.listdir(dir)
            files = {}
            #print "CONTENT = '%s'" % (content)
            for file in content:
                if file.endswith('.exe') or file.endswith('.dll'):
                    #print "FILE: '%s'" % (file)
                    filepath = "%s/%s" % (dir,file)
                    hash = self.hash_sha512_file(filepath)
                    #print "filepath = '%s' = SHA512 '%s'" % (filepath,hash)
                    files[file] = hash
            self.HASHS_DB[filename] = files
            return True

    def openvpn_filename_exe(self,version,built,arch):
        return "openvpn-install-%s-%s-%s.exe" % (version,built,arch)

    def openvpn_filename_asc(self,filename):
        return "%s.asc" % (filename)

def app():
    OpenVPN_HashBinsToJson()

if __name__ == "__main__":
    app()