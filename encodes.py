# -*- coding: utf-8
import sys, locale, os
# .py file imports
from debug import debug

def code_fiesta(DEBUG,type,output,srcf):
    #logencoding(DEBUG)
    pospages = list()
    debug(1,"def code_fiesta: type = '%s', sourcefunction = '%s'"%(type,srcf),DEBUG,True)
    """
    try:
        debug(1,"def code_fiesta: try codepage locale.getpreferredencoding() = '%s'"%(locale.getpreferredencoding()),DEBUG,True)
        if type == "decode":
            output0 = output.decode(locale.getpreferredencoding())
        if type == "encode":
            output0 = output.encode(locale.getpreferredencoding())
        debug(1,"def code_fiesta: return codepage = '%s'"%(locale.getpreferredencoding()),DEBUG,True)
        return output0
    except Exception as e:
        debug(1,"def code_fiesta: failed #1, exception = '%s'"%(e),DEBUG,True)
    """
    for codepage in values(DEBUG)['codepages']:
        try:
            debug(1,"def code_fiesta: try codepage = '%s'"%(codepage),DEBUG,True)
            if type == "decode":
                output0 = output.decode(codepage)
            if type == "encode":
                output0 = output.encode(codepage)
            pospages.append(codepage)
            debug(1,"def code_fiesta: return codepage = '%s'"%(codepage),DEBUG,True)
            return output0
        except Exception as e:
            debug(1,"def code_fiesta: failed #2, exception = '%s'"%(e),DEBUG,True)
    if len(pospages) > 0:
        pass

def logencoding(DEBUG):

    try:
        debug(1,"[encodes.py] def logencoding: #1 sys.stdout.encoding = %s" % (sys.stdout.encoding),DEBUG,True)
    except Exception as e:
        debug(1,"[encodes.py] def logencoding: #1 failed, exception = '%s'"%(e),DEBUG,True)

    try:
        debug(1,"[encodes.py] def logencoding: #2 sys.stdout.isatty() = %s" % sys.stdout.isatty(),DEBUG,True)
    except Exception as e:
        debug(1,"[encodes.py] def logencoding: #2 failed, exception = '%s'"%(e),DEBUG,True)

    try:
        debug(1,"[encodes.py] def logencoding: #3 locale.getpreferredencoding() = %s" % locale.getpreferredencoding(),DEBUG,True)
    except Exception as e:
        debug(1,"[encodes.py] def logencoding: #3 failed, exception = '%s'"%(e),DEBUG,True)

    try:
        debug(1,"[encodes.py] def logencoding: #4 sys.getfilesystemencoding() = %s" %sys.getfilesystemencoding(),DEBUG,True)
    except Exception as e:
        debug(1,"[encodes.py] def logencoding: #4 failed, exception = '%s'"%(e),DEBUG,True)

    try:
        debug(1,"[encodes.py] def logencoding: #5 os.environ PYTHONIOENCODING = %s" % (os.environ["PYTHONIOENCODING"]),DEBUG,True)
    except Exception as e:
        debug(1,"[encodes.py] def logencoding: #5 failed, exception = '%s'"%(e),DEBUG,True)

def values(DEBUG):
    all_codepages = [
                'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 
                'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 
                'cp1255', 'cp1256', 'cp1257', 'cp1258', 'cp65001', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 
                'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_12', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u'
                'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 
                'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig'
                ]
    codepages = [ 'cp437', 'cp850', 'cp852', 'cp855', 'cp857', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp65001', 'utf-8', 'utf-16' ]
    codepages = [ 'utf_8', 'cp850', 'cp1252' ]
    return { 'codepages':codepages }