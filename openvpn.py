# -*- coding: utf-8 -*-
import os, time, subprocess, sys, json
from datetime import datetime
import shlex
import win32process

# .py file imports
from debug import debug
from debug import devmode
import release_version
import hashings
import signtool
import encodes


def values(DEBUG):
    debug(9,"[openvpn.py] def values()",DEBUG,True)
    try:
        ARCH = get_arch(DEBUG)
        BUILT = "Nov 3 2016"
        LATEST = "2313"
        TIMESTAMP = 1478127600
        VERSION = "2.3.13"
        BUILT_V = "I601"
        
        OPENVPN_FILEHASHS ={
                            "openvpn-install-2.3.13-I601-x86_64.exe": \
                                {"libeay32.dll": "a46d679160ecda14ecbfd90bbf756679bfa47bca3d5ff928e7fda4b480e9db9772b1340bb36540a1b5ca29d4d8aecb2630b27a8dd8cf3bc8867ef78cf56f51e1", \
                                "openvpn.exe": "8b9973b4ff571a81edf4e353f5d9cf0ab92bb37b005bc4045f9bcae9891d21c36037e5c244fe53d57d8a46d1745749bfb8dd37095fe2be3719202c966a862117", \
                                "openvpnserv.exe": "7a6b9f857f898d84051ddf8d937c327e9c694707fbd243c58e0b8fea0b076c87325c418b1f4622267b4a49e00fbd7fae94897ac58ba90f77e14e7f97e7308e44", \
                                "liblzo2-2.dll": "629636e7fe554be056e92a611242a0560ff0c6c5bdc5dfbe60b8231788a33b234ea9ce22924671ae1719cef3bbab01e83759e553cb1bc4417fe9f59af921092e", \
                                "openvpn-gui.exe": "04f79eb2154bf0f9ae90bc72f55426b7f1471f9b3b6f61fb2f98c514323dfbcab8c20a5b6e01f63180fe402635babba04263ad8b33c606da671953f6a402a4c8", \
                                "libpkcs11-helper-1.dll": "4875d42704b78e5b0e617cec8b5a861550b5fe7aafada9c311105b4a37f382fb0a10c852749e52dce90e8c30b9fe7f92b61c3bb1c190eb016ded9a3a7036fcdf", \
                                "ssleay32.dll": "e930659c42e901514022282cefc9d799e7a6f2611c3a08ea112c8f153d9da6fa3796c871af34e4caf6c7a5ddd7b229518c2f5cfc4c85422d2391959fdaef9d80", \
                                "openssl.exe": "116f972ba698bec2a4856ffc26600b323ae461bee1d1d3ca9f9afe853e74c4242ed2db7d1f30a5df2648183248a5de647a71896cff55eab98bb75294f204ea96"}, \
                            "openvpn-install-2.3.13-I601-i686.exe": \
                                {"libeay32.dll": "90a582a2c60483e41034fe482bd5af3fc7c37fba75035d94c5ed62f580e343447fd38c0888788c932f42eac7ba2de7e21cfd997485a1b5d8e369a94139fa385f", \
                                "openvpn.exe": "c922d992a5a6e1e2b112e4f4700f2ca951a642e0073b760b80264c59aa2c402ba48af2551f0f7d33be373051972458f650ae8074660f3c7d2b733978644ebd55", \
                                "openvpnserv.exe": "75fde21f6301233c8ae95746057c0a86177d28f22a1e3e906d2de8b3d14d9e0f9fb3ce233d1afa0e729da4871473d4db4dc638acb0e9eb19510432e9ea9c9c25", \
                                "liblzo2-2.dll": "b7363ccf0857f2af1c2e39baa56dfb61bda70c89c8972359ec6e20735a93dab528409fc93f5c06a831db2eb6e8b3f8f682cd11d3886bd79f627f00723a06f0ce", \
                                "openvpn-gui.exe": "8c5507c53a2b77f653b0d5b8353f235d5b8f17d2e633e0571e5fb83027bffe1f00564611c600f75bc07ee497119ea04071a7fa9613ca40039fa8cb612c35b115", \
                                "libpkcs11-helper-1.dll": "b3406f2bcc0faa7ee53e0984bfed67a70fe6fc6964b128f078f4e21476e27551e3a446db1b8d2fb5e7bc00572455a106dfb1bec4e857d9228ec9893ff223868d", \
                                "ssleay32.dll": "8b42a553e4f11a1f16548ced5c898c4c887123a774025961419ad42ecc624c772f2e3b0aa567999728c7e2b1a630f157034bf8248dd88b6d72ead6fb44ecff90", \
                                "openssl.exe": "6ef10d501fac673d33443537133c4321ef9d508f7143dd9668884d987df84ec1f0dacd08b66b1bfacc68fb6ba83b3f19efd803410d59cb31ae3059bf2b44c937"}
                            }
        
        SHA_512 = {
            "i686" : "182c7d906a9fc081080dc3b4459e3ec867681e6cb645a75d2ebe04d1d06ed14605622c4f34ef4d352bbdf68d81b06e2de634bed75cdb7d939e7f2cdd7973d986",
            "x86_64" : "9ad6cb9afc7932dc883835cf60b5efd94ee3f0914d1fb948982056abd04df9aeb8eca3554bd13acb356602ee85e202276397a3d0fab78e7f4d854406703e007e"
            }
            
        F_SIZES = {
            "i686": 1743104,
            "x86_64": 1841208
            }
            
        URLS = {
            "REM" : "https://%s/files/openvpn" % (release_version.org_data()["VCP_DOMAIN"]),
            "ALT" : "https://swupdate.openvpn.net/community/releases"
            }
        
        SETUP_FILENAME = "openvpn-install-%s-%s-%s.exe" % (VERSION,BUILT_V,ARCH)
        OPENVPN_DL_URL =  "%s/%s" % (URLS["REM"],SETUP_FILENAME)
        OPENVPN_DL_URL_ALT = "%s/%s" % (URLS["ALT"],SETUP_FILENAME)
        
        return {
                "ARCH":ARCH, "BUILT":BUILT, "LATEST":LATEST, "TIMESTAMP":TIMESTAMP, "VERSION":VERSION, "BUILT_V":BUILT_V, 
                "SHA_512":SHA_512, "F_SIZES":F_SIZES, "SETUP_FILENAME":SETUP_FILENAME,
                "URLS":URLS, "OPENVPN_DL_URL":OPENVPN_DL_URL, "OPENVPN_DL_URL_ALT":OPENVPN_DL_URL_ALT,
                "OPENVPN_FILEHASHS":OPENVPN_FILEHASHS,
                }
    except:
        debug(1,"[openvpn.py] def values: failed",DEBUG,True)
        sys.exit()

def supported_platforms(DEBUG):
    debug(9,"[openvpn.py] def supported_platforms()",DEBUG,True)
    return [ "AMD64", "x86" ]

def get_arch(DEBUG):
    debug(9,"[openvpn.py] def get_arch()",DEBUG,True)
    data = os_platform(DEBUG)
    if data == "AMD64":
        ARCH = "x86_64"
    elif data == "x86":
        ARCH = "i686"
    else:
        sys.exit()
    debug(9,"[openvpn.py] def get_arch: ARCH = '%s'" % (ARCH),DEBUG,True)
    return ARCH

def os_platform(DEBUG):
    debug(9,"[openvpn.py] def os_platform()",DEBUG,True)
    true_platform = os.environ['PROCESSOR_ARCHITECTURE']
    try:
        true_platform = os.environ["PROCESSOR_ARCHITEW6432"]
    except KeyError:
        pass
        #true_platform not assigned to if this does not exist
    if true_platform in supported_platforms(DEBUG):
        debug(9,"[openvpn.py] def os_platform: true_platform = '%s'" % (true_platform),DEBUG,True)
        return true_platform
    else:
        debug(1,"[openvpn.py] def os_platform: true_platform = '%s' NOT SUPPORTED" % (true_platform),DEBUG,True)
        sys.exit()

def win_detect_openvpn(DEBUG,OPENVPN_EXE):
    # returns [ OPENVPN_DIR, OPENVPN_EXE ]
    try:
        debug(1,"[openvpn.py] def win_detect_openvpn()",DEBUG,True)
        if OPENVPN_EXE == False:
            debug(1,"[openvpn.py] def win_detect_openvpn: check programfiles",DEBUG,True)
            programfiles = [ "PROGRAMFILES", "PROGRAMFILES(x86)", "PROGRAMW6432" ]
            for getenv in programfiles:
                programfiles_dir = os.getenv(getenv)
                file = "%s\\OpenVPN\\bin\\openvpn.exe" % (programfiles_dir)
                if os.path.isfile(file):
                    debug(1,"[openvpn.py] def win_detect_openvpn: '%s'" % (file),DEBUG,True)
                    OPENVPN_DIR = "%s\\OpenVPN\\bin" % (programfiles_dir)
                    break
        else:
            try:
                OPENVPN_DIR = OPENVPN_EXE.rsplit('\\', 1)[0]
            except:
                return False
        
        if not OPENVPN_DIR == False and os.path.isdir(OPENVPN_DIR):
            OPENVPN_EXE = "%s\\openvpn.exe" % (OPENVPN_DIR)
            if os.path.isfile(OPENVPN_EXE):
                return { "OPENVPN_DIR":OPENVPN_DIR,"OPENVPN_EXE":OPENVPN_EXE }
    except:
        debug(1,"[openvpn.py] def win_detect_openvpn: failed",DEBUG,True)
    debug(1,"[openvpn.py] def win_detect_openvpn: return False",DEBUG,True)
    return False

def win_get_openvpn_version(DEBUG,OPENVPN_DIR):
    OPENVPN_EXE = "%s\\openvpn.exe" % (OPENVPN_DIR)
    if not os.path.isfile(OPENVPN_EXE):
        debug(1,"[openvpn.py] def win_get_openvpn_version: OPENVPN_EXE not found",DEBUG,True)
        return False
    try:
        cmdstring = '"%s" --version' % (OPENVPN_EXE)
        cmdargs = shlex.split(cmdstring)
        p = subprocess.Popen(cmdargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,creationflags = win32process.CREATE_NO_WINDOW)
        output, err = p.communicate()
        rc = p.returncode
        #OVPN_VERSION = out.decode('utf-8').split('\r\n')[0].split( )[1].replace(".","")
        OVPN_VERSION = encodes.code_fiesta(DEBUG,'decode',output,'win_get_openvpn_version').splitlines()[0].split( )[1].replace(".","")
        #OVPN_BUILT = out.decode('utf-8').split('\r\n')[0].split("built on ",1)[1].split()
        OVPN_BUILT = encodes.code_fiesta(DEBUG,'decode',output,'win_get_openvpn_version').splitlines()[0].split("built on ",1)[1].split()
        debug(1,"[openvpn.py] def win_get_openvpn_version: OVPN_VERSION = '%s', OVPN_BUILT = '%s'"%(OVPN_VERSION,OVPN_BUILT),DEBUG,True)
        return [ OVPN_VERSION, OVPN_BUILT ]
    except Exception as e:
        debug(1,"[openvpn.py] def win_get_openvpn_version: failed, exception = '%s'"%(e),DEBUG,True)
    return False

def win_detect_openvpn_version(DEBUG,OPENVPN_DIR):
    try:
        debug(1,"[openvpn.py] def win_detect_openvpn_version()",DEBUG,True)
        OVPN_LATEST = values(DEBUG)["LATEST"]
        OVPN_LATEST_BUILT = values(DEBUG)["BUILT"].split()
        OVPN_LATEST_BUILT_TIMESTAMP = values(DEBUG)["TIMESTAMP"]
        DATA = win_get_openvpn_version(DEBUG,OPENVPN_DIR)
        if not DATA == False:
            OVPN_VERSION = DATA[0]
            OVPN_BUILT = DATA[1]
        else:
            debug(1,"[openvpn.py] def win_detect_openvpn_version: failed, DATA == False",DEBUG,True)
            return False
        debug(1,"OVPN_VERSION = %s, OVPN_BUILT = %s, OVPN_LATEST_BUILT = %s" % (OVPN_VERSION,OVPN_BUILT,OVPN_LATEST_BUILT),DEBUG,True)
        if OVPN_VERSION >= OVPN_LATEST:
            debug(1,"[openvpn.py] def win_detect_openvpn_version: OVPN_VERSION '%s' >= OVPN_LATEST '%s': True"%(OVPN_VERSION,OVPN_LATEST),DEBUG,True)
            if len(OVPN_BUILT) == 3 and len(OVPN_LATEST_BUILT) == 3:
                STR1 = str(OVPN_BUILT[0]+OVPN_BUILT[1]+OVPN_BUILT[2])
                STR2 = str(OVPN_LATEST_BUILT[0]+OVPN_LATEST_BUILT[1]+OVPN_LATEST_BUILT[2])
                if STR1 == STR2:
                    debug(1,"[openvpn.py] def win_detect_openvpn_version: OVPN_BUILT '%s' == OVPN_LATEST_BUILT '%s': True"%(OVPN_BUILT,OVPN_LATEST_BUILT),DEBUG,True)
                    return True
                else:
                    built_mon = OVPN_BUILT[0]
                    built_day = int(OVPN_BUILT[1])
                    built_year = int(OVPN_BUILT[2])
                    builtstr = "%s/%s/%s" % (built_mon,built_day,built_year)
                    string_built_time = time.strptime(builtstr,"%b/%d/%Y")
                    built_month_int = int(string_built_time.tm_mon)
                    built_timestamp = int(time.mktime(datetime(built_year,built_month_int,built_day,0,0).timetuple()))
                    if built_timestamp > OVPN_LATEST_BUILT_TIMESTAMP:
                        debug(1,"[openvpn.py] def win_detect_openvpn_version: built_timestamp '%s' > OVPN_LATEST_BUILT_TIMESTAMP '%s': True" % (built_timestamp,OVPN_LATEST_BUILT_TIMESTAMP),DEBUG,True)
                        return True
        else:
            debug(1,"[openvpn.py] def win_detect_openvpn_version: OVPN_VERSION '%s' too old"%(OVPN_VERSION),DEBUG,True)
    except:
        debug(1,"[openvpn.py] def win_detect_openvpn_version: failed",DEBUG,True)
    debug(1,"[openvpn.py] def win_detect_openvpn_version: return False",DEBUG,True)
    return False

def list_openvpn_files(DEBUG,OPENVPN_DIR,type):
    debug(1,"[openvpn.py] def list_openvpn_files()",DEBUG,True)
    try:
        dir = OPENVPN_DIR
        if os.path.exists(dir):
            content = os.listdir(dir)
            list = []
            for file in content:
                if file.endswith(type):
                    list.append(file)
            if len(list) >= 1:
                debug(1,"[openvpn.py] def list_openvpn_files: dir '%s', files = '%s', list = '%s'" % (dir,len(list),list),DEBUG,True)
                return list
        else:
            debug(1,"[openvpn.py] def list_openvpn_files: dir '%s' not found!" % (dir),DEBUG,True)
    except:
        debug(1,"[openvpn.py] def list_openvpn_files: failed",DEBUG,True)
    debug(1,"[openvpn.py] def list_openvpn_files: return False",DEBUG,True)
    return False

def check_files(DEBUG,OPENVPN_DIR):
    debug(1,"[openvpn.py] def check_files()",DEBUG,True)
    
    if check_file_hashs(DEBUG,OPENVPN_DIR,".exe") == True:
        if check_file_hashs(DEBUG,OPENVPN_DIR,".dll") == True:
            return True
    else:
        # openvpn.exe hash failed, search signtool
        if not signtool.find_signtool(DEBUG) == False:
            # check exe signatures
            files = list_openvpn_files(DEBUG,OPENVPN_DIR,".exe")
            if files == False:
                return False
            for file in files:
                filepath = "%s\\%s" % (OPENVPN_DIR,file)
                if not signtool.signtool_verify(DEBUG,filepath):
                    return False
            # check dll signatures
            files = list_openvpn_files(DEBUG,OPENVPN_DIR,".dll")
            if files == False:
                return False
            for file in files:
                filepath = "%s\\%s" % (OPENVPN_DIR,file)
                if not signtool.signtool_verify(DEBUG,filepath):
                    return False
            # all file signatures verified
            return True
    debug(1,"[openvpn.py] def check_files: failed",DEBUG,True)
    return False

def check_file_hashs(DEBUG,OPENVPN_DIR,type):
    debug(1,"[openvpn.py] def check_file_hashs(%s)"%(type),DEBUG,True)
    #if devmode() == True:
    #   debug(1,"[openvpn.py] def check_file_hashs: DEVMODE ! force signature check",DEBUG,True)
    #   return False
    types = [ ".exe", ".dll" ]
    if not type in types:
        debug(1,"[openvpn.py] def check_file_hashs: type '%s' invalid"%(type),DEBUG,True)
        return False
    try:
        content = list_openvpn_files(DEBUG,OPENVPN_DIR,type)
        if content == False:
            return False
        try:
            filename = values(DEBUG)["SETUP_FILENAME"]
            try:
                hashs = values(DEBUG)["OPENVPN_FILEHASHS"][filename]
            except:
                return False
            
        except:
            debug(2,"[openvpn.py] def check_file_hashs: filename/hashs failed",DEBUG,True)
            sys.exit()
        
        debug(2,"[openvpn.py] filename = '%s' hashs = '%s'"%(filename,hashs),DEBUG,True)
        for file in content:
            debug(2,"[openvpn.py] def check_file_hashs: file = '%s'" % (file),DEBUG,True)
            filepath = "%s\\%s" % (OPENVPN_DIR,file)
            hasha = hashings.hash_sha512_file(DEBUG,filepath)
            debug(2,"[openvpn.py] def check_file_hashs: hasha = '%s'" % (hasha),DEBUG,True)
            try:
                hashb = hashs[file]
            except:
                return False
            if hasha == hashb:
                debug(2,"[openvpn.py] def check_file_hashs: hash file = '%s' OK!" % (file),DEBUG,True)
            else:
                debug(1,"[openvpn.py] def check_file_hashs: hash file = '%s' failed" % (file),DEBUG,True)
                return False
        return True
    except:
        debug(1,"[openvpn.py] def check_file_hashs: failed",DEBUG,True)
        sys.exit()
        return False

"""
def upgrade_openvpn(DEBUG):
    pass

def load_openvpnbin_from_remote(self):
    pass

def verify_openvpnbin_dl(self):
    pass

def win_install_openvpn(self):
    pass

def extract_ovpn(self):
    pass

def win_select_openvpn(self):
    pass

def win_detect_openvpn_version(self):
    pass

def find_signtool(self):
    pass

def signtool_verify(self,file):
    pass
"""