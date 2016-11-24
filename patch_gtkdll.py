# -*- coding: utf-8
import os, shutil, struct, time
from winreg import *
BITS = struct.calcsize("P") * 8


def patch_gtkdll():
    unsigned_dir = "includes\\DLL\\%s\\unsigned" % (BITS)
    gtkfile = "%s\\libgtk-3-0.dll" % (unsigned_dir)
    if not os.path.exists(gtkfile):
        gtkfile = "dist%s\\libgtk-3-0.dll" % (BITS)
    gtkfile32 = "%s\\libgtk-3-0-32.dll" % (unsigned_dir)
    gtkfile32tmp = "%s.tmp" % (gtkfile32)
    if os.path.exists(gtkfile):

        if BITS == 32:
            offset = 0x3E4E2 # win32
        if BITS == 64:
            offset = 0x3D051 # win64

        pixel_16 = "\x10"
        pixel_32 = "\x20"

        if os.path.exists(gtkfile32):
            print("delete already patched file '%s' before patching" % (gtkfile32))
            return False

        try:
            with open(gtkfile,'r+b') as f1:
                f1.seek(offset)
                checkoffset = f1.read(1).decode('utf-8')
                f1.close()
                if checkoffset == pixel_16:
                    shutil.copyfile(gtkfile, gtkfile32tmp)

            if os.path.exists(gtkfile32tmp):
                with open(gtkfile32tmp,'r+b') as f2:
                    f2.seek(offset)
                    checkoffset = f2.read(1).decode('utf-8')
                    if checkoffset == pixel_16:
                        print("write pixel to file '%s'" % (gtkfile32tmp))
                        f2.seek(offset)
                        f2.write(pixel_32.encode('utf-8'))
                    f2.close()
                shutil.move(gtkfile32tmp, gtkfile32)
                print("move tmp file to '%s'"  % (gtkfile32))
                time.sleep(5)
            else:
                print("gtkfile '%s' not found" % (gtkfile32tmp))
        except Exception as e:
            print("patch_gtkdll() failed, exception = '%s'"%(e))

    else:
        print("gtkfile '%s' not found" % (gtkfile))

patch_gtkdll()
