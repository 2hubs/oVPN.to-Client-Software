# -*- coding: utf-8 -*-
import os, subprocess

# .py file imports
from debug import debug
from debug import devmode
from debug import devdir
import hashings


def find_signtool(DEBUG):
    debug(1,"[signtool.py] def find_signtool()",DEBUG,True)
    try:
        signtoolhash = "e85d79cc617642f585cb9e4ad5dd919b8d15570a291bdd1e69fd38d4f278bc4b6f110329e8fa6948b7d516917cc2bde43532cde33e8c5e66355d0c97cfd7ebc2"
        exe = "signtool_w10sdk.exe"
        BIN_DIR = os.getcwd()
        signtool = "%s\\%s" % (BIN_DIR,exe)
        if not os.path.isfile(signtool):
            signtool = "%s\\includes\\codesign\\%s" % (devdir(),exe)
        if os.path.isfile(signtool):
            hash = hashings.hash_sha512_file(DEBUG,signtool)
            if signtoolhash == hash:
                debug(1,"[signtool.py] def find_signtool: signtool = '%s'" % (signtool),DEBUG,True)
                return signtool
            else:
                debug(1,"[signtool.py] def find_signtool: signtoolhash failed",DEBUG,True)
        else:
            debug(1,"[signtool.py] def signtool_verify_files: signtool not found",DEBUG,True)
    except:
        debug(1,"[signtool.py] def find_signtool: failed",DEBUG,True)
    return False

def signtool_verify(DEBUG,file):
    debug(1,"[signtool.py] def signtool_verify(%s)"%(file),DEBUG,True)
    signtool = find_signtool(DEBUG)
    if os.path.isfile(file):
        cscertsha1 = "21F94C255A8B20D21A323CA5ACB8EBF284E09037"
        #if devmode() == True:
        #   cscertsha1 = "1234000012340000123400001234000012340000"
        #string1 = '"%s" verify /v /a /all /pa /tw /sha1 %s "%s"' % (signtool,cscertsha1,file)
        string1 = '"%s" verify /q /a /all /pa /tw /sha1 %s "%s"' % (signtool,cscertsha1,file)
        debug(1,"[signtool.py] def signtool_verify: string1 = '%s'"%(string1),DEBUG,True)
        exitcode1 = 1
        try:
            exitcode1 = subprocess.check_call("%s" % (string1),shell=True)
        except:
            pass
        if exitcode1 == 0:
            debug(1,"[signtool.py] def signtool_verify: file = '%s' signature verified"%(file),DEBUG,True)
            return True
        else:
            debug(1,"[signtool.py] def signtool_verify: file = '%s' signature failed"%(file),DEBUG,True)
            # only check file is signed from same CA if DEVMODE is True
            if devmode() == False:
                return False
            else:
                return False
                debug(1,"[signtool.py] def signtool_verify: file = '%s' check signature CA hash"%(file),DEBUG,True)
                cacertsha1 = "92C1588E85AF2201CE7915E8538B492F605B80C6"
                string2 = '"%s" verify /v /a /all /pa /tw /ca %s "%s"' % (signtool,cacertsha1,file)
                debug(1,"[signtool.py] def signtool_verify: string2 = '%s'"%(string2),DEBUG,True)
                exitcode2 = 1
                try:
                    exitcode2 = subprocess.check_call("%s" % (string2),shell=True)
                except:
                    pass
                if exitcode2 == 0:
                    debug(1,"[signtool.py] def signtool_verify: file = '%s' signature CA verified"%(file),DEBUG,True)
                    return True
                else:
                    debug(1,"[signtool.py] def signtool_verify: file = '%s' signature CA failed"%(file),DEBUG,True)
                    return False
    else:
        debug(1,"[signtool.py] def signtool_verify(%s) not found"%(file),DEBUG,True)
        return False
