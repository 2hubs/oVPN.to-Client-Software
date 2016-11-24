# -*- coding: utf-8 -*-
import os, sys, shutil, struct
from winreg import *
from ctypes import *
from debug import debug

BITS = struct.calcsize("P") * 8

def select_gtkdll(DEBUG):
    pixel = 16
    BIN_DIR = os.getcwd()
    gtkfile = "%s\\libgtk-3-0.dll" % (BIN_DIR)
    gtkfile16 = "%s\\libgtk-3-0-16.dll" % (BIN_DIR)
    gtkfile32 = "%s\\libgtk-3-0-32.dll" % (BIN_DIR)

    try:
        LOGPIXELSX = 88
        DC = windll.user32.GetDC(None)
        dpi = windll.gdi32.GetDeviceCaps(DC, LOGPIXELSX)
        windll.user32.ReleaseDC(None, DC)
        if dpi > 96:
            pixel = 32
        if dpi == 96:
            pixel = 16
        debug(1,"[patches.py] def select_gtkdll() Get DPI from DC: %s" % dpi,DEBUG,True)
    except:
        try:
            Registry = ConnectRegistry(None, HKEY_CURRENT_USER)
            RawKey = OpenKey(Registry, "Control Panel\Desktop")
        except:
            pass
        try:
            if not RawKey == False:
                i = 0
                while 1:
                    name, value, type = EnumValue(RawKey, i)
                    if name == "LogPixels":
                        if value > 96:
                            pixel = 32
                        if value == 96:
                            pixel = 16
                        break
                    i += 1
                debug(1,"[patches.py] def select_gtkdll() Get DPI from Reg: %s" % value,DEBUG,True)
        except:
            pass

    try:
        debug(1,"[patches.py] def select_gtkdll() Detected Pixel Size: %s" % pixel,DEBUG,True)
        if pixel == 32:
            if os.path.isfile(gtkfile32):
                debug(1,"[patches.py] def select_gtkdll() gtkfile --> gtkfile16",DEBUG,True)
                shutil.move(gtkfile, gtkfile16)
                debug(1,"[patches.py] def select_gtkdll() gtkfile32 --> gtkfile",DEBUG,True)
                shutil.move(gtkfile32, gtkfile)
            else:
                debug(1,"[patches.py] def select_gtkdll() select_gtkdll not needed: gtkfile32 not found",DEBUG,True)
            return pixel
        if pixel == 16:
            if os.path.isfile(gtkfile16):
                debug(1,"[patches.py] def select_gtkdll() gtkfile --> gtkfile32",DEBUG,True)
                shutil.move(gtkfile, gtkfile32)
                debug(1,"[patches.py] def select_gtkdll() gtkfile16 --> gtkfile",DEBUG,True)
                shutil.move(gtkfile16, gtkfile)
            else:
                debug(1,"[patches.py] def select_gtkdll() select_gtkdll not needed: gtkfile16 not found",DEBUG,True)
            return pixel
    except:
        debug(1,"[patches.py] def select_gtkdll() failed",DEBUG,True)
