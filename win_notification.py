# -*- coding: utf-8 -*-
from debug import debug
import os, platform, threading, ctypes

from win32api import GetSystemMetrics, GetModuleHandle, PostQuitMessage, LoadResource
from win32con import CW_USEDEFAULT, IMAGE_ICON, IMAGE_BITMAP, IDI_INFORMATION, IDI_APPLICATION, LR_DEFAULTSIZE, LR_DEFAULTCOLOR, LR_LOADFROMFILE, WM_DESTROY, WS_OVERLAPPED, WS_SYSMENU, WM_USER, RT_ICON
from win32gui import CreateWindow, DestroyWindow, LoadIcon, LoadImage, NIF_ICON, NIF_INFO, NIF_MESSAGE, NIF_TIP, NIM_ADD, NIM_DELETE, NIM_MODIFY, RegisterClass, UnregisterClass, Shell_NotifyIcon, UpdateWindow, WNDCLASS

WINVER10 = False
if "Windows-10" in platform.platform():
    WINVER10 = True

class notify:
    def __init__(self):

        message_map = { WM_DESTROY: self.send_notify_destroy }
        wc = WNDCLASS()
        self.hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = str("PythonTaskbar")
        wc.lpfnWndProc = message_map
        self.classAtom = RegisterClass(wc)

    def send_notify(self,DEBUG,DEV_DIR,text,title):
        try:
            
            while not self.isDestroyed() == True:
                wait_event = threading.Event()
                wait_event.wait(timeout=0.1)
            self.destroyed = False
            debug(222,"[win_notification.py] def send_notify: [Win10 = %s]" % (WINVER10),DEBUG,True)
            style = WS_OVERLAPPED | WS_SYSMENU
            self.hwnd = CreateWindow(self.classAtom, "Taskbar", style,0, 0, CW_USEDEFAULT,CW_USEDEFAULT,0, 0, self.hinst, None)
            UpdateWindow(self.hwnd)

            try:
                if WINVER10 == False:
                    raise Exception
                """ https://msdn.microsoft.com/en-us/library/windows/desktop/ms648060(v=vs.85).aspx """
                icon_res = LoadResource(None, RT_ICON, 13)
                hicon = ctypes.windll.user32.CreateIconFromResourceEx(icon_res, len(icon_res), True, 0x00030000, 48, 48, LR_DEFAULTCOLOR)
                debug(1,"[win_notification.py] def send_notify: CreateIconFromResource() #1",DEBUG,True)

            except Exception as e:
                debug(222,"[win_notification.py] def send_notify: CreateIconFromResource() #1 failed, exception = '%s'"%(e),DEBUG,True)

                try:
                    if WINVER10 == False:
                        raise Exception
                    icon_path = False
                    icon_path1 = "%s\\else\\app_icons\\app_icon.ico" % (DEV_DIR)
                    files = [ icon_path1 ]
                    for file in files:
                            if os.path.isfile(file):
                                icon_path = file
                                break
                    if icon_path == False:
                        raise Exception
                    icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
                    """ https://msdn.microsoft.com/en-us/library/windows/desktop/ms648045(v=vs.85).aspx """
                    hicon = LoadImage(self.hinst, icon_path,IMAGE_ICON, 48, 48, icon_flags)
                    debug(1,"[win_notification.py] def send_notify: LoadImage() #2",DEBUG,True)

                except Exception as e:
                    debug(222,"[win_notification.py] def send_notify: LoadImage() #2 failed, exception = '%s'"%(e),DEBUG,True)

                    try:
                        """ https://msdn.microsoft.com/en-us/library/windows/desktop/ms648072(v=vs.85).aspx """
                        hicon = LoadIcon(0, IDI_INFORMATION)
                        debug(1,"[win_notification.py] def send_notify: LoadIcon() #3",DEBUG,True)
                    except Exception as e:
                        debug(222,"[win_notification.py] def send_notify: LoadIcon() #3 failed, exception = '%s'"%(e),DEBUG,True)
                        return False

            flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
            nid = (self.hwnd, 0, flags, WM_USER + 20, hicon, "")
            Shell_NotifyIcon(NIM_ADD, nid)

            #0=16x16,1=blue info,2=yellow exclamation,3=red cross,4=icon from filepath
            icontype = 4
            if WINVER10 == False:
                icontype = 0

            Shell_NotifyIcon(NIM_MODIFY, (self.hwnd, 0, NIF_INFO,WM_USER + 20,hicon, "oVPN Notify", text, 200,title, icontype))

            if WINVER10 == False:
                wait_event = threading.Event()
                wait_event.wait(timeout=4)

            anyreturn = DestroyWindow(self.hwnd)
            debug(222,"[win_notification.py] def send_notify: DestroyWindow() returned = '%s'"%(anyreturn),DEBUG,True)

            debug(1,"[win_notification.py] def send_notify: [Win10 = %s] return" % (WINVER10),DEBUG,True)
            self.destroyed = True
            return None
        except Exception as e:
            debug(1,"[win_notification.py] def send_notify: failed, exception = '%s'"%(e),DEBUG,True)

    def send_notify_destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)
        debug(222,"[win_notification.py] def send_notify_destroy: return",True,True)
        return None

    def isDestroyed(self):
        try:
            return self.destroyed
        except:
            return True
