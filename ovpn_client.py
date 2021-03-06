# -*- coding: utf-8 -*-
decoding = 'utf_8'
import debug
DEBUG = debug.getmode("DEBUG")
DEVMODE = debug.getmode("DEVMODE")
TESTENCODING = debug.getmode("TESTENCODING")
D0WNDNS = debug.getmode("D0WNDNS")
DEV_DIR=debug.devdir()
if DEVMODE == True:
    DEBUG = True

import sys
try:
    import patches
    TRAYSIZE = patches.select_gtkdll(DEBUG)
except Exception as e:
    print("traysize failed, exception = '%s'" % (e))
    sys.exit()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GObject, Gio
from datetime import datetime as datetime
import os, base64, gettext, locale, types, platform, hashlib, random, time, zipfile, subprocess, threading, socket, requests, json, struct, string, re, shlex
import configparser
from collections import OrderedDict

# .py files imports
import winregs
import icons_b64
import schedule_task
import release_version
import openvpn
import signtool
import hashings
import request_api
import encodes
import flags_b64
try:
    import win_notification
    WIN_NOTIFY = True
except Exception as e:
    print("import win_notification failed, exception = '%s'"%(e))
    sys.exit()
    WIN_NOTIFY = False

def CDEBUG(level,text,istrue,bindir):
    debug.debug(level,text,istrue,bindir)

try:
    
    CLIENTVERSION = "%s" % (release_version.version_data()["VERSION"])
    CLIENT_STRING = "%s %s" % (release_version.version_data()["NAME"],CLIENTVERSION)
    VCP_DOMAIN = release_version.org_data()["VCP_DOMAIN"]
    API_DOMAIN = release_version.org_data()["API_DOMAIN"]
    API_URL = "https://%s:%s/%s" % (API_DOMAIN,release_version.org_data()["API_PORT"],release_version.org_data()["API_POST"])

    try:
        BITS = struct.calcsize("P") * 8
        if BITS == 32:
            import release_hard32
            BUILT_STRING = release_hard32.builtdate()
        elif BITS == 64:
            import release_hard64
            BUILT_STRING = release_hard64.builtdate()
        else:
            sys.exit()
    except Exception as e: 
        BUILT_STRING = "(UNDEFINED)"
    print(BUILT_STRING)

except Exception as e:
    print("import release_version failed")
    sys.exit()


ABOUT_TEXT = """Credits and Cookies go to...
+ ... all our customers! We can not exist without you!
+ ... d0wn for hosting DNS on dns.d0wn.biz!
+ ... bauerj for code submits!
+ ... semool for gtk3 fork!
+ ... dogpellet for DNStest() ideas!
+ ... ungefiltert-surfen.de for WorldWide DNS!
+ ... famfamfam.com for flag and silk icons!

Need Help?

Join https://webirc.ovpn.to into Channel #help !
"""

class Systray:
    def __init__(self):
        if WIN_NOTIFY == True:
            self.notification = win_notification.notify()
        self.self_vars()
        self.tray = Gtk.StatusIcon()
        self.tray.is_embedded()
        self.debug(1,"TrayIcon Output Size: %s pixel" % (TRAYSIZE))
        self.tray.set_from_stock(Gtk.STOCK_EXECUTE)
        self.tray.set_tooltip_markup(CLIENT_STRING)
        self.tray.connect('popup-menu', self.on_right_click)
        self.tray.connect('activate', self.on_left_click)
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.connect("delete-event", Gtk.main_quit)
        self.init_localization(None)
        if self.preboot():
            self.init_theme()
            if self.UPDATEOVPNONSTART == True:
                if self.check_inet_connection() == True:
                    if self.APIKEY == False:
                        self.request_UPDATE = True
                        GLib.idle_add(self.dialog_apikey)
                    else:
                        self.check_remote_update("config")
                else:
                    self.msgwarn(_("Could not connect to %s") % (API_DOMAIN),_("Error"))
            GLib.timeout_add(1000,self.systray_timer)
            self.win_firewall_analyze()
        else:
            sys.exit()
    
    def dummy_func(self,srcf):
        self.debug(1,"def dummy_func(), srcf = '%s'"%(srcf))

    def self_vars(self):
        self.VAR = dict()
        self.DEBUG = DEBUG
        self.DEBUGWINDOW_OPEN = False
        self.DEBUGCACHESIZE = 0
        print("self.DEBUG = %s"%(self.DEBUG))
        self.DEVMODE = DEVMODE
        self.OS = sys.platform
        self.ARCH = openvpn.values(self.DEBUG)["ARCH"]
        self.APIURL = API_URL
        self.INIT_FIRST_UPDATE = True

        
        # MAINWINDOW vars
        self.VAR["MAIN"] = dict()
        self.VAR['MAIN']['OPEN'] = False
        self.VAR['MAIN']['HIDE'] = False
        self.VAR['MAIN']['ALLOWCELLHIDE'] = [ 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26 ]
        self.VAR['MAIN']['SHOWCELLS'] = [ 6, 7, 9, 24, 23, 25, 26, 16, 10, 8, 5, 4, 3 ]
        self.VAR['MAIN']['CELLINDEX'] = { 2:"Server", 3:"IPv4", 4:"IPv6", 5:"Port", 6:"Proto", 7:"MTU", 8:"Cipher", 9:"Live", 10:"Link", 11:"VLAN IPv4", 12:"VLAN IPv6", 13:"CPU", 14:"RAM", 15:"HDD", 16:"Traffic", 17:"Load", 18:"oVPN %", 19:"oSSH %", 20:"SOCK %", 21:"HTTP %", 22:"TINC %", 23:"PING4", 24:"PING6", 25:"SVR", 26:"Right Flag" }
        
        self.APP_FONT_SIZE_AVAIABLE = [ "6", "7", "8", "9", "10", "11", "12", "13" ]
        self.INSTALLED_THEMES = [ "ms-windows", "Adwaita", "Adwaita-dark", "Greybird", "Flat-Remix-OS" ]
        self.INSTALLED_ICONS = [ "standard", "classic", "classic2", "shield_bluesync", "experimental", "private" ]
        self.INSTALLED_LANGUAGES = [ "en", "de", "es" ]
        
        self.VAR['OVPN'] = dict()
        self.OVPN_ACC_DATA = {}
        self.VAR['OVPN']['STOP'] = False
        self.VAR['OVPN']['SERVERLIST'] = list()
        self.VAR['OVPN']['CONFIGDATA'] = {}
        self.VAR['OVPN']['SERVERDATA'] = {}
        self.VAR['OVPN']['FAVSRV'] = False
        self.VAR['OVPN']['AUTOCONNECT'] = False
        self.VAR['OVPN']['CALL_SRV'] = False
        self.VAR['OVPN']['LOGFILE'] = False
        self.VAR['OVPN']['THREADID'] = False
        
        self.VAR['OVPN']['PINGS'] = list()
        self.VAR['OVPN']['PING_LAST'] = -1
        self.VAR['OVPN']['PING_STAT'] = 0
        self.VAR['OVPN']['PING_DEAD'] = 0
        self.VAR['OVPN']['CFGTYPE'] = "23x"
        
        self.VAR['OVPN']['CONN'] = dict()
        self.VAR['OVPN']['CONN']['OK'] = False
        self.VAR['OVPN']['CONN']['SERVER'] = False
        self.VAR['OVPN']['CONN']['IP'] = False
        self.VAR['OVPN']['CONN']['PORT'] = False
        self.VAR['OVPN']['CONN']['PROTO'] = False
        self.VAR['OVPN']['CONN']['START'] = 0
        self.VAR['OVPN']['CONN']['SECONDS'] = 0
        self.VAR['OVPN']['CONN']['FAILEDTIME'] = 0
        self.VAR['OVPN']['CONN']['TESTING'] = False

        self.VAR['OVPN']['GW'] = dict()
        self.VAR['OVPN']['GW']['IP4A'] = "172.16.32.1"
        self.VAR['OVPN']['GW']['IP4B'] = "172.16.48.1"
        self.VAR['OVPN']['GW']['IP4'] = self.VAR['OVPN']['GW']['IP4A']
        
        self.VAR["RELEASE"] = int(BUILT_STRING.split()[6].split('(')[1].split(')')[0])
        
        self.VAR["UPDATE"] = dict()
        self.VAR["UPDATE"]["FILE"] = False
        self.VAR["UPDATE"]["HASH"] = False
        self.VAR["UPDATE"]["SIZE"] = False
        self.VAR["UPDATE"]["URL"] = False
        
        self.d0wns_DNS = {'ns1.es.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': 'EB09:E854:AEDA:9705:CB47:ED69:EADD:4156:3653:82C5:C88D:A2E3:6917:3B54:4774:7505', 'countrycode': 'es', 'dnscryptcertname': '2.dnscrypt-cert.es.d0wn.biz', 'country': 'Spain', 'ip4': '91.142.220.29', 'dnscryptpubkey': 'pubkey.es.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns2.lv.dns.d0wn.biz': {'ip6': '2a02:7aa0:1201::f60e:2719', 'dnscryptfingerprint': 'B111:F80C:E3E0:1C36:CC73:0995:009E:6351:EF08:0503:309D:9417:7AA3:8C67:916D:0CDF', 'countrycode': 'lv', 'dnscryptcertname': '2.dnscrypt-cert.lv2.d0wn.biz', 'country': 'Latvia', 'ip4': '185.86.151.28', 'dnscryptpubkey': 'pubkey.lv.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.random.dns.d0wn.biz': {'ip6': '2a00:1dc0:cafe::c6af:c19d', 'dnscryptfingerprint': 'A420:867F:ED5C:024C:C86A:EECE:AA05:194B:017F:D2FF:9E72:385A:874F:8CE5:6832:ED2E', 'countrycode': 'random', 'dnscryptcertname': '2.dnscrypt-cert.random.d0wn.biz', 'country': 'Moldova', 'ip4': '178.17.170.133', 'dnscryptpubkey': 'pubkey.random.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns1.lv.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '1B70:FB6F:2E47:1753:91EF:1084:ECD2:983A:9018:F3E3:DDF1:E563:E528:156A:664A:1AE8', 'countrycode': 'lv', 'dnscryptcertname': '2.dnscrypt-cert.lv.d0wn.biz', 'country': 'Latvia', 'ip4': '89.111.13.60', 'dnscryptpubkey': 'pubkey.lv.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns1.cz.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': 'EE21:5055:4DA0:1367:BAC3:768A:7C1E:24BF:D777:ACD5:77A4:44F8:BDF3:84E0:5966:D855', 'countrycode': 'cz', 'dnscryptcertname': '2.dnscrypt-cert.cz.d0wn.biz', 'country': 'Czech Republic', 'ip4': '81.2.237.32', 'dnscryptpubkey': 'pubkey.cz.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns2.us.dns.d0wn.biz': {'ip6': '2605:6400:20:7d7:1:5ee:bad:c0de', 'dnscryptfingerprint': 'A22D:99C4:E2E9:CB94:67F0:E36A:619F:418B:466C:5786:C0B8:ACAA:B716:71F7:1F81:F5F8', 'countrycode': 'us', 'dnscryptcertname': '2.dnscrypt-cert.us2.d0wn.biz', 'country': 'United States of America', 'ip4': '209.141.53.57', 'dnscryptpubkey': 'pubkey.us.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.hk.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '84ED:0DFF:7967:5DBD:2D93:65A2:A6AB:7F90:146F:A50B:048C:8C75:651B:AA55:7129:6740', 'countrycode': 'hk', 'dnscryptcertname': '2.dnscrypt-cert.hk.d0wn.biz', 'country': 'Hong Kong', 'ip4': '45.124.66.200', 'dnscryptpubkey': 'pubkey.hk.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.nl.dns.d0wn.biz': {'ip6': '2a03:b0c0:0:1010::62:f001', 'dnscryptfingerprint': '7BE6:68FE:A505:FFA7:4C27:C2CA:F881:59DA:038C:5741:13AA:2556:A4D2:2D0B:B6F0:009E', 'countrycode': 'nl', 'dnscryptcertname': '2.dnscrypt-cert.nl.d0wn.biz', 'country': 'Netherlands', 'ip4': '95.85.9.86', 'dnscryptpubkey': 'pubkey.nl.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 1053 5353 27015'}, 'ns1.md.dns.d0wn.biz': {'ip6': '2a00:1dc0:cafe::ad86:fa7e', 'dnscryptfingerprint': '3DB2:C4CB:39E2:6B82:FDDF:6D91:1A65:D164:F4F0:D237:8CDD:0C37:469F:24BA:B9A0:F9FF', 'countrycode': 'md', 'dnscryptcertname': '2.dnscrypt-cert.md.d0wn.biz', 'country': 'Moldova', 'ip4': '178.17.170.67', 'dnscryptpubkey': 'pubkey.md.dnscrypt.d0wn.biz', 'dnscryptports': '54 1053 5353 27015'}, 'ns1.ru.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '0ECA:BC40:E0A1:335F:0221:4240:AB86:2919:D16A:2393:CCEB:4B40:9EB9:4F24:3077:ED99', 'countrycode': 'ru', 'dnscryptcertname': '2.dnscrypt-cert.ru.d0wn.biz', 'country': 'Russia', 'ip4': '91.214.71.181', 'dnscryptpubkey': 'pubkey.ru.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.bg.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '423C:D823:B3EA:2015:F027:ECF1:5704:3EB7:764A:D02D:9447:56E6:51FD:D06F:E571:2FCC', 'countrycode': 'bg', 'dnscryptcertname': '2.dnscrypt-cert.bg.d0wn.biz', 'country': 'Bulgaria', 'ip4': '217.12.203.133', 'dnscryptpubkey': 'pubkey.bg.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.us.dns.d0wn.biz': {'ip6': '2605:6400:10:59:0:b19:b00b:babe', 'dnscryptfingerprint': '6741:6E7F:4744:194E:D725:91A2:1A62:A715:78F9:62CD:5263:84FC:DAA8:6C7E:4D9F:438B', 'countrycode': 'us', 'dnscryptcertname': '2.dnscrypt-cert.us.d0wn.biz', 'country': 'United States of America', 'ip4': '199.195.249.174', 'dnscryptpubkey': 'pubkey.us.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns3.nl.dns.d0wn.biz': {'ip6': '2a06:7240:5:601:dead:beef:e3e7:7a9d', 'dnscryptfingerprint': '01FC:1AA9:F71F:F09E:55CE:0D04:9ACA:2B11:9536:319E:04A9:C3AE:77CB:127D:4C53:0651', 'countrycode': 'nl', 'dnscryptcertname': '2.dnscrypt-cert.nl3.d0wn.biz', 'country': 'Netherlands', 'ip4': '185.133.72.116', 'dnscryptpubkey': 'pubkey.nl3.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.cy.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '2144:4FE7:59C3:13B9:FABB:FC2A:F975:9F9C:CD9A:2ED7:0978:3A25:7347:4B83:8F86:EA2B', 'countrycode': 'cy', 'dnscryptcertname': '2.dnscrypt-cert.cy.d0wn.biz', 'country': 'Cyprus', 'ip4': '213.169.148.11', 'dnscryptpubkey': 'pubkey.cy.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.gr.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': 'D056:D3A4:9568:5AFE:4B0D:C688:7A75:41B2:7217:F0C9:75A5:A6C0:142D:363B:F992:9867', 'countrycode': 'gr', 'dnscryptcertname': '2.dnscrypt-cert.gr.d0wn.biz', 'country': 'Greece', 'ip4': '85.25.105.193', 'dnscryptpubkey': 'pubkey.gr.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns1.au.dns.d0wn.biz': {'ip6': '2402:9e80:1::1:e554', 'dnscryptfingerprint': 'A7D9:0F8E:9A98:1381:176A:3D25:36DE:E865:8538:9CD8:78BC:C3B5:A146:23F1:C2EF:58D8', 'countrycode': 'au', 'dnscryptcertname': '2.dnscrypt-cert.au.d0wn.biz', 'country': 'Australia', 'ip4': '27.100.36.191', 'dnscryptpubkey': 'pubkey.au.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.sg.dns.d0wn.biz': {'ip6': '2400:6180:0:d0::38:d001', 'dnscryptfingerprint': 'D82B:2B76:1DA0:8470:B55B:820C:FAAB:9F32:D632:E9E0:5616:2CE7:7D21:E970:98FF:4A34', 'countrycode': 'sg', 'dnscryptcertname': '2.dnscrypt-cert.sg.d0wn.biz', 'country': 'Singapore', 'ip4': '128.199.248.105', 'dnscryptpubkey': 'pubkey.sg.dnscrypt.d0wn.biz', 'dnscryptports': '54 443 1053 5353 27015'}, 'ns2.de.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '8C62:691A:A7EA:69D3:8A25:86AA:2715:87F0:9B11:9159:0663:55FC:1CD0:61C5:C863:1940', 'countrycode': 'de', 'dnscryptcertname': '2.dnscrypt-cert.de2.d0wn.biz', 'country': 'Germany', 'ip4': '185.137.15.105', 'dnscryptpubkey': 'pubkey.de2.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.ro.dns.d0wn.biz': {'ip6': '2a04:9dc0:c1:7::cb9:f785', 'dnscryptfingerprint': 'DA9E:6882:B0F8:335E:B5F4:A059:1B7D:EE6F:BD55:4451:93B4:13BF:AFFC:7D26:4527:CE1A', 'countrycode': 'ro', 'dnscryptcertname': '2.dnscrypt-cert.ro.d0wn.biz', 'country': 'Romania', 'ip4': '77.81.104.121', 'dnscryptpubkey': 'pubkey.ro.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns2.nl.dns.d0wn.biz': {'ip6': '2a02:2ca0:64:22::2', 'dnscryptfingerprint': 'DFAA:B7D8:29E6:1F34:4FED:2610:4221:70C9:ADC7:7E9F:A65F:4A46:0BAE:A735:3186:3B99', 'countrycode': 'nl', 'dnscryptcertname': '2.dnscrypt-cert.nl2.d0wn.biz', 'country': 'Netherlands', 'ip4': '185.83.217.248', 'dnscryptpubkey': 'pubkey.nl2.dnscrypt.d0wn.biz', 'dnscryptports': '54 1053 5353 27015'}, 'ns1.ua.dns.d0wn.biz': {'ip6': '2a02:27a8:0:2::556', 'dnscryptfingerprint': '3B1E:D468:FFD3:F261:20DE:E7F1:6A74:E1D5:D59E:B40D:F3EA:99BC:0B05:70CC:292D:99BA', 'countrycode': 'ua', 'dnscryptcertname': '2.dnscrypt-cert.ua.d0wn.biz', 'country': 'Ukraine', 'ip4': '217.12.210.54', 'dnscryptpubkey': 'pubkey.ua.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.de.dns.d0wn.biz': {'ip6': '2001:1608:10:195:3:dead:beef:cafe', 'dnscryptfingerprint': 'B040:19F8:8D49:4682:41E3:EB58:5F61:173F:EF8E:55DA:0597:2DB7:27BB:C153:1DD8:D109', 'countrycode': 'de', 'dnscryptcertname': '2.dnscrypt-cert.de.d0wn.biz', 'country': 'Germany', 'ip4': '82.211.31.248', 'dnscryptpubkey': 'pubkey.de.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.it.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '2DEC:CEF8:A4D0:57DE:0D1A:CE8E:0A3C:BEB8:2135:61A8:BF0E:7373:0BA0:EC38:C876:3B50', 'countrycode': 'it', 'dnscryptcertname': '2.dnscrypt-cert.it.d0wn.biz', 'country': 'Italy', 'ip4': '31.14.133.188', 'dnscryptpubkey': 'pubkey.it.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns2.fr.dns.d0wn.biz': {'ip6': '2001:41D0:A:0028::1', 'dnscryptfingerprint': '25A7:DB7B:7835:55D5:7DA4:7C0C:57F8:9C5F:0220:3D09:67E3:585A:723E:E0D1:CB38:F767', 'countrycode': 'fr', 'dnscryptcertname': '2.dnscrypt-cert.fr2.d0wn.biz', 'country': 'France', 'ip4': '37.187.0.40', 'dnscryptpubkey': 'pubkey.fr2.dnscrypt.d0wn.biz', 'dnscryptports': '54 443 1053 5353 27015'}, 'ns1.lu.dns.d0wn.biz': {'ip6': '2605:6400:30:fbb5:0:1ce:1ce:babe', 'dnscryptfingerprint': '737B:B68B:7D3C:896F:260D:91C3:60A6:AD64:8CD3:1B22:4D5F:7089:490C:539F:2EC6:C309', 'countrycode': 'lu', 'dnscryptcertname': '2.dnscrypt-cert.lu.d0wn.biz', 'country': 'Luxembourg', 'ip4': '104.244.72.13', 'dnscryptpubkey': 'pubkey.lu.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.tz.dns.d0wn.biz': {'ip6': '2c0f:fda8:5::2ed1:d2ec', 'dnscryptfingerprint': 'B79F:A025:1AF6:2125:DF3E:3B03:856D:4CB7:704E:45EB:B850:3A7B:C6AA:5510:D87D:087D', 'countrycode': 'tz', 'dnscryptcertname': '2.dnscrypt-cert.tz.d0wn.biz', 'country': 'Tanzania', 'ip4': '41.79.69.13', 'dnscryptpubkey': 'pubkey.tz.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns2.random.dns.d0wn.biz': {'ip6': '2a00:1ca8:a7::1e9', 'dnscryptfingerprint': '9112:338E:7D0B:5E78:B792:9BB6:1B75:4888:AC94:65B5:B86B:B5DE:CCF3:E5B9:15A5:DC54', 'countrycode': 'random', 'dnscryptcertname': '2.dnscrypt-cert.random2.d0wn.biz', 'country': 'Netherlands', 'ip4': '185.14.29.140', 'dnscryptpubkey': 'pubkey.random2.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}, 'ns2.sg.dns.d0wn.biz': {'ip6': '2403:5680::1:200f', 'dnscryptfingerprint': '0F00:63C4:6EAF:29C3:29CD:E125:2033:6F0A:0C72:7CDD:F1F4:3D47:F95D:02BC:07F7:9FFC', 'countrycode': 'sg', 'dnscryptcertname': '2.dnscrypt-cert.sg2.d0wn.biz', 'country': 'Singapore', 'ip4': '210.16.120.139', 'dnscryptpubkey': 'pubkey.sg2.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.fr.dns.d0wn.biz': {'ip6': '2001:41d0:d:1c5::7d09:1', 'dnscryptfingerprint': '58A8:22D3:29EB:C14F:BCEB:45AF:42EB:2F58:C797:0AD3:ED31:397D:1D34:8636:2375:7251', 'countrycode': 'fr', 'dnscryptcertname': '2.dnscrypt-cert.fr.d0wn.biz', 'country': 'France', 'ip4': '151.80.7.115', 'dnscryptpubkey': 'pubkey.fr.dnscrypt.d0wn.biz', 'dnscryptports': '54 1053 5353 27015'}, 'ns1.ca.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '9DCE:B0A9:9653:C069:8583:AA5C:498C:3A75:8FBB:AEAA:55A8:6D0F:7C50:896C:45F5:F5ED', 'countrycode': 'ca', 'dnscryptcertname': '2.dnscrypt-cert.ca.d0wn.biz', 'country': 'Canada', 'ip4': '198.50.244.26', 'dnscryptpubkey': 'pubkey.ca.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.se.dns.d0wn.biz': {'ip6': '2a02:7aa0:1619::4f50:a69', 'dnscryptfingerprint': '9D4F:762B:DD24:F77A:64B4:7E0F:F5C6:93FD:A02A:39E9:8FEC:0CEE:F252:3A5F:A403:C032', 'countrycode': 'se', 'dnscryptcertname': '2.dnscrypt-cert.se.d0wn.biz', 'country': 'Sweden', 'ip4': '95.215.44.124', 'dnscryptpubkey': 'pubkey.se.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.dk.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '0838:C9CF:2292:2D4C:4DB7:4A5E:ED10:DD36:66DD:9551:7238:6387:B7A0:2FA0:885A:5F77', 'countrycode': 'dk', 'dnscryptcertname': '2.dnscrypt-cert.dk.d0wn.biz', 'country': 'Denmark', 'ip4': '77.66.108.93', 'dnscryptpubkey': 'pubkey.dk.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.uk.dns.d0wn.biz': {'ip6': '2a04:92c7:7:7::14ae:460a', 'dnscryptfingerprint': 'FADB:BE63:7FCD:FE22:0DBE:D433:438C:5A1D:C267:1E96:4B67:1918:B15F:9121:77D7:5B2E', 'countrycode': 'uk', 'dnscryptcertname': '2.dnscrypt-cert.uk.d0wn.biz', 'country': 'United Kingdom', 'ip4': '185.121.25.85', 'dnscryptpubkey': 'pubkey.uk.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 1053 5353 27015'}, 'ns1.is.dns.d0wn.biz': {'ip6': '', 'dnscryptfingerprint': '2B28:974E:073A:6B38:722A:5BE1:F7A0:250C:508F:A809:238F:8F3D:76D8:6098:20D7:B2D9', 'countrycode': 'is', 'dnscryptcertname': '2.dnscrypt-cert.is.d0wn.biz', 'country': 'Iceland', 'ip4': '37.235.49.61', 'dnscryptpubkey': 'pubkey.is.dnscrypt.d0wn.biz', 'dnscryptports': '54 80 443 5353 1053 27015'}}
        # update content of 'self.d0wns_DNS' with argument D0WNDNS: if 'self.d0wns_DNS = {}' with self.load_d0wns_dns() called from mainwindow rightclick and copy from debug.log
        
        oVPN_DNS = { 
                        'ns1.ch.dns.ovpn.to': {
                            'countrycode': 'ch', 
                            'dnscryptcertname': '2.dnscrypt-cert.swiss1.ovpn.to', 
                            'country': 'Switzerland', 
                            'dnscryptpubkey': 'pubkey.ch.dnscrypt.ovpn.to', 
                            'ip6': '2a03:9a60:827:abcd::ef42', 
                            'ip4': '185.128.41.238', 
                            'dnscryptports': '5353', 
                            'dnscryptfingerprint': '7A66:D5BA:186D:4C52:DD0F:FB42:0DD7:B9BF:7A4C:3442:E309:FD38:CC86:4E76:1445:877E',
                            #'expire': '2017-Aug-21'
                            },
                        }
        for key,value in oVPN_DNS.items():
            self.d0wns_DNS[key] = value
        
        if D0WNDNS == True:
            self.d0wns_DNS = {}
        
        self.FLAGS_B64 = flags_b64.flagsb64()
        print("len(self.FLAGS_B64) = '%s'" % (len(self.FLAGS_B64)))

        self.VAR['CFG'] = dict()
        self.VAR['CFG']['AUTOSTART'] = False
        self.VAR['CFG']['AS_DELAY_TIME'] = 30
        self.VAR['CFG']['AS_LIST_DELAY'] = [ 10, 20, 30, 40, 50, 60 ]
        
        # default False
        self.nbpage0, self.nbpage1, self.nbpage2, self.nbpage3 = False, False, False, False
        self.systray_menu = False
        self.WINDOW_QUIT_OPEN = False
        self.WINDOW_ABOUT_OPEN = False
        self.MOUSELEVEL = False
        self.API_DIR = False
        self.OPENVPN_DIR = False
        self.INTERFACES = False
        self.DEBUG_LOGFILE = False
        self.statusbar_text = False
        self.USERID = False
        self.GATEWAY_LOCAL = False
        self.GATEWAY_DNS1 = False
        self.GATEWAY_DNS2 = False
        self.WIN_TAP_DEVICE = False
        self.WIN_EXT_DEVICE = False
        self.SAVE_APIKEY_INFILE = False
        
        # lists
        self.WIN_TAP_DEVS = list()
        self.PROFILES = list()
        
        # dicts
        self.FLAG_CACHE_PIXBUF = {}
        self.ICON_CACHE_PIXBUF = {}
        
        # requests
        self.request_LOAD_ACCDATA = True
        self.request_UPDATE = True
        self.request_LOAD_SRVDATA = False
        
        # triggers
        self.MSGWARN_WINDOW_OPEN = False
        self.ACCWINDOW_OPEN = False
        self.HIDECELLSWINDOW_OPEN = False
        self.SETTINGSWINDOW_OPEN = False
        self.LANG_FONT_CHANGE = False
        self.STATE_OVPN = False
        self.STATE_CERTDL = False
        self.WIN_FIREWALL_ADDED_RULE_TO_VCP = False
        self.WIN_RESET_EXT_DEVICE = False
        self.WIN_FIREWALL_STARTED = False
        self.WIN_DNS_CHANGED = False
        self.UPDATE_SWITCH = False
        self.isWRITING_OPTFILE = False
        self.WIN_EXT_DHCP_DNS = False
        
        # timers running
        self.win_firewall_tap_blockoutbound_running = False
        self.timer_load_remote_data_running = False
        self.timer_ovpn_ping_running = False
        self.timer_check_certdl_running = False
        self.stop_systray_timer = False
        self.systray_timer_running = False
        self.inThread_jump_server_running = False
        
        # lasts and nexts
        self.LAST_CFG_UPDATE = 0
        self.LAST_CHECK_MYIP = 0
        self.NEXT_PING_EXEC = 0
        self.LAST_CHECK_INET_FALSE = 0
        self.LAST_MSGWARN_WINDOW = 0
        self.LAST_MSGWARN_WINDOW_DNS = 0
        self.LAST_OVPN_PING_DEAD_MESSAGE = 0
        self.LAST_OVPN_ACC_DATA_UPDATE = 0
        self.LAST_OVPN_SRV_DATA_UPDATE = 0
        self.LAST_HIT_UPDATE_BUTTON5 = 0
        self.LAST_CHECK_CFG_UPDATE = 0
        self.LAST_CHECK_CFG_UPDATE_FORCE = 0
        self.MOUSE_IN_TRAY = 0
        
        # config options
        self.OPENVPN_EXE = False
        self.OPENVPN_SILENT_SETUP = False
        self.APP_LANGUAGE = "en"
        self.APP_FONT_SIZE = "9"
        self.APP_THEME = "Adwaita"
        self.ICONS_THEME = "standard"
        self.WIN_ENABLE_NOTIFICATIONS = True
        self.DISABLE_ALL_NOTIFICATIONS = False
        self.TAP_BLOCKOUTBOUND = False
        self.NO_WIN_FIREWALL = False
        self.NO_DNS_CHANGE = False
        self.MYDNS = {}
        self.UPDATEOVPNONSTART = False
        self.APIKEY = False
        self.LOAD_DATA_EVERY = 900
        self.LOAD_ACCDATA = False
        self.LOAD_SRVDATA = False
        self.SRV_LIGHT_WIDTH = "512"
        self.SRV_LIGHT_HEIGHT = "720"
        self.SRV_WIDTH = "1280"
        self.SRV_HEIGHT = "720"
        self.SRV_LIGHT_WIDTH_DEFAULT = self.SRV_LIGHT_WIDTH
        self.SRV_LIGHT_HEIGHT_DEFAULT = self.SRV_LIGHT_HEIGHT
        self.SRV_WIDTH_DEFAULT = self.SRV_WIDTH
        self.SRV_HEIGHT_DEFAULT = self.SRV_HEIGHT
        self.WIN_BACKUP_FIREWALL = False
        self.WIN_RESET_FIREWALL = False
        self.WIN_DONT_ASK_FW_EXIT = False
        self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = True
        self.WIN_DISABLE_EXT_IF_ON_DISCO = False
        self.DISABLE_SRV_WINDOW = False
        self.DISABLE_ACC_WINDOW = False
        self.DISABLE_QUIT_ENTRY = True
        
        # from befores
        self.VAR['CACHE'] = dict()
        self.VAR['CACHE']['systraytext'] = False
        self.VAR['CACHE']['systrayicon'] = False
        self.VAR['CACHE']['statusbartext'] = False
        self.VAR['CACHE']['icontheme'] = self.ICONS_THEME
        
        # any vars
        self.CA_FIXED_HASH = "f37dff160dda454d432e5f0e0f30f8b20986b59daadabf2d261839de5dfd1e7d8a52ecae54bdd21c9fee9238628f9fff70c7e1a340481d14f3a1bdeea4a162e8"
        self.WHITELIST_PUBLIC_PROFILE = {
            "Intern 01) oVPN Connection Check": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"80","proto":"tcp"},
            "Intern 02) https://vcp.ovpn.to": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"443","proto":"tcp"},
            "Intern 03) IRC": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"6697","proto":"tcp"},
            "Intern 04) DNS": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"53","proto":"tcp"},
            "Intern 05) DNS": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"53","proto":"udp"},
            "Intern 06) SSH": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"22","proto":"tcp"},
            "Intern 07) SOCKS": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"1080","proto":"tcp"},
            "Intern 08) HTTP": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"3128","proto":"tcp"},
            "Intern 09) SOCKS Random": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"1081","proto":"tcp"},
            "Intern 10) HTTP Random": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"3129","proto":"tcp"},
            "Intern 11) STUNNEL HTTP": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"8081","proto":"tcp"},
            "Intern 12) STUNNEL SOCKS": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"8080","proto":"tcp"},
            "Intern 13) TOR SOCKS": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"9100","proto":"tcp"},
            "Intern 14) JABBER client": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"5222","proto":"tcp"},
            "Intern 15) JABBER transfer": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"5000","proto":"tcp"},
            "Intern 16) AnoMail IMAPs": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"993","proto":"tcp"},
            "Intern 17) AnoMail POP3s": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"995","proto":"tcp"},
            "Intern 18) AnoMail SMTPs": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"587","proto":"tcp"},
            "Intern 19) ZNC": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"6444","proto":"tcp"},
            "Intern 20) dnscrypt": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"5353","proto":"tcp"},
            "Intern 21) dnscrypt": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"5353","proto":"udp"},
            "Intern 22) nntp-50001 Binary SSL user=ovpn,pass=free": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"50001","proto":"tcp"},
            "Intern 23) nntp-50002 Binary SSL user=ovpn,pass=free": {"ip":self.VAR['OVPN']['GW']['IP4A'],"port":"50002","proto":"tcp"}
        }

    def preboot(self):
        self.debug(1,"def preboot()")
        self.self_vars()
        if DEBUG == True:
            self.show_debug_window()
        if self.OS == "win32":
                if self.win_pre1_check_app_dir():
                    if self.win_pre2_check_profiles_win():
                        if self.win_pre3_load_profile_dir_vars():
                            if self.check_config_folders():
                                if self.read_options_file():
                                    self.win_firewall_clear_vcp_rules()
                                    if self.win_detect_openvpn():
                                        if self.read_interfaces():
                                            if self.write_options_file():
                                                return True
        elif OS == "linux2" :
            self.errorquit(text=_("Operating System not supported: %s") % (self.OS))
        elif OS == "darwin":
            self.errorquit(text=_("Operating System not supported: %s") % (self.OS))
        else: 
            self.errorquit(text=_("Operating System not supported: %s") % (self.OS))

    def win_pre1_check_app_dir(self):
        self.debug(1,"def win_pre1_check_app_dir()")
        os_appdata = os.getenv('APPDATA')
        if os.path.exists("appdata"):
            print("alternative folder found")
            self.BIN_DIR = os.getcwd()
            self.APP_DIR = "%s\\appdata\\ovpn" % (self.BIN_DIR)
        else:
            self.APP_DIR = "%s\\ovpn" % (os_appdata)
            self.BIN_DIR = "%s\\bin\\client\\dist" % (self.APP_DIR)
        self.CA_FILE = "%s\\cacert_ovpn.pem" % (self.BIN_DIR)
        if not os.path.exists(self.APP_DIR):
            self.debug(1,"win_pre1_check_app_dir %s not found, creating." % (self.APP_DIR))
            os.mkdir(self.APP_DIR)
        if os.path.exists(self.APP_DIR):
            self.debug(1,"win_pre1_check_app_dir self.APP_DIR=%s :True" % (self.APP_DIR))
            return True
        else:
            self.errorquit(text = _("Could not create app_dir: %s") % (self.APP_DIR))

    def list_profiles(self):
        self.debug(1,"def list_profiles()")
        self.profiles_unclean = os.listdir(self.APP_DIR)
        for profile in self.profiles_unclean:
            if profile.isdigit():
                self.PROFILES.append(profile)
        #self.PROFILES_COUNT = int(len(self.PROFILES))
        self.debug(1,"def list_profiles: profiles_count %s" % (len(self.PROFILES)))

    def win_pre2_check_profiles_win(self):
        self.debug(1,"def win_pre2_check_profiles_win()")
        self.list_profiles()
        if len(self.PROFILES) == 0:
            self.debug(1,"No profiles found")
            if self.USERID == False:
                self.debug(1,"spawn popup userid = %s" % (self.USERID))
                self.debug(1,"def win_pre2_check_profiles_win: before form_ask_userid")
                self.form_ask_userid()
                self.debug(1,"def win_pre2_check_profiles_win: after form_ask_userid")
                if not self.USERID == False and not self.APIKEY == False:
                    self.debug(1,"def win_pre2_check_profiles_win: L:310")
                    return True
        elif len(self.PROFILES) == 1:
            userid = int(self.PROFILES[0])
            print(userid)
            if userid > 1:
                self.USERID = userid
                return True
        elif len(self.PROFILES) > 1:
            if not self.select_userid() == True:
                self.errorquit(text=_("Select User-ID failed!"))
            return True

    def win_pre3_load_profile_dir_vars(self):
        self.debug(1,"def win_pre3_load_profile_dir_vars()")
        self.API_DIR = "%s\\%s" % (self.APP_DIR,self.USERID)
        self.DEBUG_LOGFILE = "%s\\client_debug.log" % (self.BIN_DIR)
        if os.path.isfile(self.DEBUG_LOGFILE):
            try:
                os.remove(self.DEBUG_LOGFILE)
            except Exception as e:
                pass
        self.lock_file = "%s\\lock.file" % (self.APP_DIR)
        self.OPT_FILE = "%s\\options.cfg" % (self.API_DIR)
        self.api_cfg = "%s\\ovpnapi.conf" % (self.API_DIR)
        if os.path.isfile(self.api_cfg):
            os.remove(self.api_cfg)
        self.VPN_DIR = "%s\\openvpn" % (self.API_DIR)
        self.prx_dir = "%s\\proxy" % (self.API_DIR)
        self.stu_dir = "%s\\stunnel" % (self.API_DIR)
        self.pfw_dir = "%s\\pfw" % (self.API_DIR)
        self.pfw_bak = "%s\\pfw.%s.bak.wfw" % (self.pfw_dir,int(time.time()))
        #self.pfw_private_log = "%s\\pfw.private.%s.log" % (self.pfw_dir,self.BOOTTIME)
        #self.pfw_public_log = "%s\\pfw.public.%s.log" % (self.pfw_dir,self.BOOTTIME)
        #self.pfw_domain_log = "%s\\pfw.domain.%s.log" % (self.pfw_dir,self.BOOTTIME)
        
        self.VPN_CFG = "%s\\config" % (self.VPN_DIR)
        self.VPN_CFGip4 = "%s\\ip4" % (self.VPN_CFG)
        self.VPN_CFGip46 = "%s\\ip46" % (self.VPN_CFG)
        self.VPN_CFGip64 = "%s\\ip64" % (self.VPN_CFG)
        
        self.dns_d0wntxt =  "%s\\dns.txt" % (self.API_DIR)
        
        self.zip_cfg = "%s\\confs.zip" % (self.VPN_DIR)
        self.zip_crt = "%s\\certs.zip" % (self.VPN_DIR)
        self.api_upd = "%s\\lastupdate.txt" % (self.VPN_DIR)
        if os.path.isfile(self.api_upd):
            os.remove(self.api_upd)
        
        if self.load_icons() == False:
            return False
        
        if not self.load_ca_cert():
            return False
        
        self.WINDIR = os.getenv('WINDIR')
        if os.path.isdir(self.WINDIR):
            self.WIN_NETSH_EXE = "%s\\system32\\netsh.exe" % (self.WINDIR)
            self.WIN_ROUTE_EXE = "%s\\system32\\route.exe" % (self.WINDIR)
            self.WIN_IPCONFIG_EXE = "%s\\system32\\ipconfig.exe" % (self.WINDIR)
            self.WIN_TASKKILL_EXE = "%s\\system32\\taskkill.exe" % (self.WINDIR)
        else:
            self.errorquit(text=_("Error: '%s' not found!") % (self.WINDIR))
        
        if not os.path.isfile(self.WIN_NETSH_EXE):
            self.errorquit(text=_("Error: '%s' not found!") % (self.WIN_NETSH_EXE))
        
        if not os.path.isfile(self.WIN_ROUTE_EXE):
            self.errorquit(text=_("Error: '%s' not found!") % (self.WIN_ROUTE_EXE))
        
        if not os.path.isfile(self.WIN_IPCONFIG_EXE):
            self.errorquit(text=_("Error: '%s' not found!") % (self.WIN_IPCONFIG_EXE))
        
        if not os.path.isfile(self.WIN_TASKKILL_EXE):
            self.errorquit(text=_("Error: '%s' not found!") % (self.WIN_TASKKILL_EXE))
        
        self.debug(1,"win_pre3_load_profile_dir_vars loaded")
        return True

    def load_icons(self):
        self.debug(2,"def load_icons()")
        # called from: 
        """
            def win_pre3_load_profile_dir_vars()
            def read_options_file()
            def cb_icons_switcher_changed()
        """
        self.app_icon = self.decode_icon("app_icon")

        if self.ICONS_THEME == "standard":
            self.systray_icon_connected = self.app_icon
            self.systray_icon_connect = self.decode_icon("connect")
            self.systray_icon_testing = self.decode_icon("testing")
            self.systray_icon_disconnected = self.decode_icon("disconnect1")
            self.systray_icon_disconnected_traymenu = self.decode_icon("disconnect1_menu")
            self.systray_icon_syncupdate1 = self.decode_icon("sync_2a")
            self.systray_icon_syncupdate2 = self.decode_icon("sync_2b")
            self.systray_icon_syncupdate3 = self.decode_icon("sync_2c")
        
        elif self.ICONS_THEME == "classic":
            self.systray_icon_connected = self.decode_icon("connected_classic")
            self.systray_icon_connect = self.decode_icon("connect")
            self.systray_icon_testing = self.decode_icon("testing")
            self.systray_icon_disconnected = self.decode_icon("disconnect1")
            self.systray_icon_disconnected_traymenu = self.decode_icon("disconnect1_menu")
            self.systray_icon_syncupdate1 = self.decode_icon("sync_1a")
            self.systray_icon_syncupdate2 = self.decode_icon("sync_1b")
            self.systray_icon_syncupdate3 = self.decode_icon("sync_1c")
        
        elif self.ICONS_THEME == "classic2":
            self.systray_icon_connected = self.decode_icon("connected_classic")
            self.systray_icon_connect = self.decode_icon("connect")
            self.systray_icon_testing = self.decode_icon("testing")
            self.systray_icon_disconnected = self.decode_icon("disconnect2")
            self.systray_icon_disconnected_traymenu = self.decode_icon("disconnect1_menu")
            self.systray_icon_syncupdate1 = self.decode_icon("sync_1a")
            self.systray_icon_syncupdate2 = self.decode_icon("sync_1b")
            self.systray_icon_syncupdate3 = self.decode_icon("sync_1c")
        
        elif self.ICONS_THEME == "shield_bluesync":
            self.systray_icon_connected = self.app_icon
            self.systray_icon_connect = self.decode_icon("connect")
            self.systray_icon_testing = self.decode_icon("testing")
            self.systray_icon_disconnected = self.decode_icon("disconnect1")
            self.systray_icon_disconnected_traymenu = self.decode_icon("disconnect1_menu")
            self.systray_icon_syncupdate1 = self.decode_icon("sync_1a")
            self.systray_icon_syncupdate2 = self.decode_icon("sync_1b")
            self.systray_icon_syncupdate3 = self.decode_icon("sync_1c")
        
        elif self.ICONS_THEME == "experimental":
            self.systray_icon_connected = self.app_icon
            self.systray_icon_connect = self.decode_icon("connect")
            self.systray_icon_testing = self.decode_icon("testing")
            self.systray_icon_disconnected = self.decode_icon("disconnect3")
            self.systray_icon_disconnected_traymenu = self.decode_icon("disconnect3_menu")
            self.systray_icon_syncupdate1 = self.decode_icon("sync_2a")
            self.systray_icon_syncupdate2 = self.decode_icon("sync_2b")
            self.systray_icon_syncupdate3 = self.decode_icon("sync_2c")
        
        elif self.ICONS_THEME == "private":
            self.ico_dir_theme = "%s\\ico\\private" % (self.BIN_DIR)
            if os.path.isdir(self.ico_dir_theme):
                systray_icon_connected = "%s\\connected.ico" % (self.ico_dir_theme)
                systray_icon_connect = "%s\\connect.ico" % (self.ico_dir_theme)
                systray_icon_testing = "%s\\testing.ico" % (self.ico_dir_theme)
                systray_icon_disconnected = "%s\\disconnect.ico" % (self.ico_dir_theme)
                systray_icon_disconnected_traymenu = "%s\\disconnect_menu.ico" % (self.ico_dir_theme)
                systray_icon_syncupdate1 = "%s\\sync_1.ico" % (self.ico_dir_theme)
                systray_icon_syncupdate2 = "%s\\sync_2.ico" % (self.ico_dir_theme)
                systray_icon_syncupdate3 = "%s\\sync_3.ico" % (self.ico_dir_theme)
                checkfiles = [systray_icon_connected,systray_icon_connect,systray_icon_testing,systray_icon_disconnected,systray_icon_disconnected_traymenu,systray_icon_syncupdate1,systray_icon_syncupdate2,systray_icon_syncupdate3]

                missing_file = list()
                for file in checkfiles:
                    if not os.path.isfile(file):
                        missing_file.append(file.rsplit("\\", 1)[1])
                        self.debug(1,"def load_icons: file '%s' not found" %(file))

                if missing_file:
                    self.msgwarn(_("Private Icon(s) not found in:\n%s\n\nMissing Icons:\n%s") % (self.ico_dir_theme,missing_file),_("Error"))
                    return False
                else:
                    self.systray_icon_connected = systray_icon_connected
                    self.systray_icon_connect = systray_icon_connect
                    self.systray_icon_testing = systray_icon_testing
                    self.systray_icon_disconnected = systray_icon_disconnected
                    self.systray_icon_disconnected_traymenu = systray_icon_disconnected_traymenu
                    self.systray_icon_syncupdate1 = systray_icon_syncupdate1
                    self.systray_icon_syncupdate2 = systray_icon_syncupdate2
                    self.systray_icon_syncupdate3 = systray_icon_syncupdate3
            else:
                #self.debug(1,"def load_icons(), private icon dir not found: '%s'" % (self.ico_dir_theme))
                self.msgwarn(_("Private Icon Dir not found:\n%s") % (self.ico_dir_theme),_("Error"))
                return False

        self.VAR['CACHE']['systrayicon'] = False
        return True

    def check_config_folders(self):
        self.debug(1,"def check_config_folders()")
        try:
            #self.debug(1,"def check_config_folders userid = %s" % (self.USERID))
            self.debug(1,"def check_config_folders: userid found")
            if not os.path.exists(self.API_DIR):
                self.debug(1,"api_dir %s not found, creating." % (self.API_DIR))
                os.mkdir(self.API_DIR)
            if os.path.isfile(self.lock_file):
                try:
                    os.remove(self.lock_file)
                except Exception as e:
                    self.errorquit(text=_("Could not remove lock file.\nFile itself locked because another oVPN Client instance running?"))
            if not os.path.isfile(self.lock_file):
                self.LOCK = open(self.lock_file,'wt')
                self.LOCK.write('1')
            if not os.path.exists(self.VPN_DIR):
                os.mkdir(self.VPN_DIR)
            if not os.path.exists(self.VPN_CFG):
                os.mkdir(self.VPN_CFG)
            if not os.path.exists(self.VPN_CFGip4):
                os.mkdir(self.VPN_CFGip4)
            if not os.path.exists(self.VPN_CFGip46):
                os.mkdir(self.VPN_CFGip46)
            if not os.path.exists(self.VPN_CFGip64):
                os.mkdir(self.VPN_CFGip64)
            if not os.path.exists(self.prx_dir):
                os.mkdir(self.prx_dir)
            if not os.path.exists(self.stu_dir):
                os.mkdir(self.stu_dir)
            if not os.path.exists(self.pfw_dir):
                os.mkdir(self.pfw_dir)
            if os.path.exists(self.API_DIR) and os.path.exists(self.VPN_DIR) and os.path.exists(self.VPN_CFG) \
            and os.path.exists(self.prx_dir) and os.path.exists(self.stu_dir) and os.path.exists(self.pfw_dir):
                return True
            else:
                self.errorquit(text=_("Creating API-DIRS\n%s \n%s \n%s \n%s \n%s failed!") % (self.API_DIR,self.VPN_DIR,self.prx_dir,self.stu_dir,self.pfw_dir))
        except Exception as e:
            self.debug(1,"def check_config_folders: failed, exception = '%s'" % (e))
            self.errorquit(text=_("Creating config folders failed!"))

    def read_options_file(self):
        self.debug(1,"def read_options_file()")
        if os.path.isfile(self.OPT_FILE):
            try:
                #parser = SafeConfigParser()
                parser = configparser.ConfigParser()
                parser.read(self.OPT_FILE)
                
                try:
                    APIKEY = parser.get('oVPN','apikey')
                    if APIKEY == "False" and not self.APIKEY == False:
                        # don't remove this pass or we go to else and this is not what we wanna have!
                        pass
                    elif APIKEY == "False":
                        self.APIKEY = False
                    else:
                        self.SAVE_APIKEY_INFILE = True
                        self.APIKEY = APIKEY
                except Exception as e:
                    self.debug(1,"def read_options_file: apikey failed, exception = '%s'"%(e))
                
                try:
                    gDEBUG = parser.get('oVPN','debugmode')
                    self.debug(1,"def read_options_file: debug 03.01.1, gDEBUG = '%s'"%(gDEBUG))
                    if gDEBUG == "True":
                        self.DEBUG = True
                        if self.DEBUGWINDOW_OPEN == False:
                            self.show_debug_window()
                    else:
                        self.DEBUG = False
                    self.debug(1,BUILT_STRING)
                except Exception as e:
                    self.debug(1,"def read_options_file: debugmode failed, exception = '%s'"%(e))
                
                try:
                    APPLANG = parser.get('oVPN','applanguage')
                    self.debug(1,"APPLANG = parser.get(oVPN,'%s') " % (APPLANG))
                    if APPLANG in self.INSTALLED_LANGUAGES:
                        self.debug(1,"def read_options_file: APPLANG '%s' in self.INSTALLED_LANGUAGES" % (APPLANG))
                        if self.init_localization(APPLANG) == True:
                            if self.APP_LANGUAGE == APPLANG:
                                self.debug(1,"NEW self.APP_LANGUAGE = '%s'" % (self.APP_LANGUAGE))
                    else:
                        self.debug(1,"def read_options_file: self.APP_LANGUAGE = '%s'" % (self.APP_LANGUAGE))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.APP_LANGUAGE failed, exception = '%s'"%(e))
                
                try:
                    LAST_CFG_UPDATE = parser.getint('oVPN','lastcfgupdate')
                    if not LAST_CFG_UPDATE >= 0:
                        self.LAST_CFG_UPDATE = 0
                    else:
                        self.LAST_CFG_UPDATE = LAST_CFG_UPDATE
                    self.debug(1,"def read_options_file: self.LAST_CFG_UPDATE = '%s'" % (self.LAST_CFG_UPDATE))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.LAST_CFG_UPDATE failed, exception = '%s'"%(e))
                
                try:
                    OVPN_FAV_SERVER = parser.get('oVPN','favserver')
                    if OVPN_FAV_SERVER == "False": 
                        self.VAR['OVPN']['FAVSRV'] = False
                        self.VAR['OVPN']['AUTOCONNECT'] = False
                    else:
                        self.VAR['OVPN']['FAVSRV'] = OVPN_FAV_SERVER
                        self.VAR['OVPN']['AUTOCONNECT'] = True
                    self.debug(1,"def read_options_file: self.VAR['OVPN']['FAVSRV'] = '%s'" % (self.VAR['OVPN']['FAVSRV']))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.VAR['OVPN']['FAVSRV'] failed, exception = '%s'"%(e))
                
                try:
                    WIN_EXT_DEVICE = parser.get('oVPN','winextdevice')
                    if WIN_EXT_DEVICE == "False": 
                        self.WIN_EXT_DEVICE = False
                    else:
                        self.WIN_EXT_DEVICE = WIN_EXT_DEVICE
                    self.debug(1,"def read_options_file: self.WIN_EXT_DEVICE = '%s'" % (self.WIN_EXT_DEVICE))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.WIN_EXT_DEVICE failed, exception = '%s'"%(e))
                
                try:
                    WIN_TAP_DEVICE = parser.get('oVPN','wintapdevice')
                    if WIN_TAP_DEVICE == "False": 
                        self.WIN_TAP_DEVICE = False
                    else:
                        self.WIN_TAP_DEVICE = WIN_TAP_DEVICE
                    self.debug(1,"def read_options_file: self.WIN_TAP_DEVICE = '%s'" % (self.WIN_TAP_DEVICE))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.WIN_TAP_DEVICE failed, exception = '%s'"%(e))
                
                try:
                    OPENVPN_EXE = parser.get('oVPN','openvpnexe')
                    if OPENVPN_EXE == "False":
                        self.OPENVPN_EXE = False
                    else:
                        self.OPENVPN_EXE = OPENVPN_EXE
                    self.debug(1,"def read_options_file: self.OPENVPN_EXE = '%s'" % (self.OPENVPN_EXE))
                except Exception as e:
                    self.debug(1,"def read_options_file: openvpnexe failed, exception = '%s'"%(e))
                
                try:
                    AUTOSTART_DELAY_TIME = parser.getint('oVPN','autostartdelay')
                    if AUTOSTART_DELAY_TIME >= 10:
                        self.VAR['CFG']['AS_DELAY_TIME'] = AUTOSTART_DELAY_TIME
                    else:
                        self.VAR['CFG']['AS_DELAY_TIME'] = 10
                    self.debug(1,"def read_options_file: self.VAR['CFG']['AS_DELAY_TIME'] = '%s'" % (self.VAR['CFG']['AS_DELAY_TIME']))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.VAR['CFG']['AS_DELAY_TIME'] failed, exception = '%s'"%(e))
                
                try:
                    self.VAR['CFG']['AUTOSTART'] = parser.getboolean('oVPN','autostart')
                    if self.VAR['CFG']['AUTOSTART'] == True:
                        try:
                            schedule_task.set_task(self.DEBUG,self.VAR['CFG']['AS_DELAY_TIME'])
                        except Exception as e:
                            pass
                    self.debug(1,"def read_options_file: self.VAR['CFG']['AUTOSTART'] = '%s'" % (self.VAR['CFG']['AUTOSTART']))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.VAR['CFG']['AUTOSTART'] failed, exception = '%s'"%(e))
                
                try:
                    self.UPDATEOVPNONSTART = parser.getboolean('oVPN','updateovpnonstart')
                    self.debug(1,"def read_options_file: self.UPDATEOVPNONSTART = '%s'" % (self.UPDATEOVPNONSTART))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.UPDATEOVPNONSTART failed, exception = '%s'"%(e))
                
                try:
                    ocfgv = parser.get('oVPN','configversion')
                    if ocfgv == "23x" or ocfgv == "23x46" or ocfgv == "23x64":
                        self.VAR['OVPN']['CFGTYPE'] = ocfgv
                    else:
                        self.VAR['OVPN']['CFGTYPE'] = "23x"
                    
                    if self.VAR['OVPN']['CFGTYPE'] == "23x":
                        self.VAR['OVPN']['GW']['IP4'] = self.VAR['OVPN']['GW']['IP4A']
                        self.VPN_CFG = self.VPN_CFGip4
                    elif self.VAR['OVPN']['CFGTYPE'] == "23x46":
                        self.VAR['OVPN']['GW']['IP4'] = self.VAR['OVPN']['GW']['IP4B']
                        self.VPN_CFG = self.VPN_CFGip46
                    elif self.VAR['OVPN']['CFGTYPE'] == "23x64":
                        self.VAR['OVPN']['GW']['IP4'] = self.VAR['OVPN']['GW']['IP4B']
                        self.VPN_CFG = self.VPN_CFGip64
                    
                    self.debug(1,"def read_options_file: self.VAR['OVPN']['CFGTYPE'] = '%s'" % (self.VAR['OVPN']['CFGTYPE']))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.VAR['OVPN']['CFGTYPE'] failed, exception = '%s'"%(e))
                
                try:
                    self.WIN_RESET_FIREWALL = parser.getboolean('oVPN','winresetfirewall')
                    self.debug(1,"def read_options_file: self.WIN_RESET_FIREWALL = '%s'" % (self.WIN_RESET_FIREWALL))
                except Exception as e:
                    self.debug(1,"def read_options_file: winresetfirewall failed, exception = '%s'"%(e))
                
                try:
                    self.WIN_BACKUP_FIREWALL = parser.getboolean('oVPN','winbackupfirewall')
                    self.debug(1,"def read_options_file: self.WIN_BACKUP_FIREWALL = '%s'" % (self.WIN_RESET_FIREWALL))
                except Exception as e:
                    self.debug(1,"def read_options_file: winbackupfirewall failed, exception = '%s'"%(e))
                
                try:
                    self.NO_WIN_FIREWALL = parser.getboolean('oVPN','nowinfirewall')
                    self.debug(1,"def read_options_file: self.NO_WIN_FIREWALL = '%s'" % (self.NO_WIN_FIREWALL))
                except Exception as e:
                    self.debug(1,"def read_options_file: nowinfirewall failed, exception = '%s'"%(e))
                
                try:
                    self.WIN_DONT_ASK_FW_EXIT = parser.getboolean('oVPN','winnoaskfwonexit')
                    self.debug(1,"def read_options_file: self.WIN_DONT_ASK_FW_EXIT = '%s'" % (self.WIN_DONT_ASK_FW_EXIT))
                except Exception as e:
                    self.debug(1,"def read_options_file: winnoaskfwonexit failed, exception = '%s'"%(e))
                
                try:
                    self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = parser.getboolean('oVPN','winfwblockonexit')
                    self.debug(1,"def read_options_file: self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = '%s'" % (self.WIN_ALWAYS_BLOCK_FW_ON_EXIT))
                except Exception as e:
                    self.debug(1,"def read_options_file: winfwblockonexit failed, exception = '%s'"%(e))

                try:
                    self.WIN_DISABLE_EXT_IF_ON_DISCO = parser.getboolean('oVPN','windisableextifondisco')
                    self.debug(1,"def read_options_file: self.WIN_DISABLE_EXT_IF_ON_DISCO = '%s'" % (self.WIN_DISABLE_EXT_IF_ON_DISCO))
                except Exception as e:
                    self.debug(1,"def read_options_file: windisableextifondisco failed, exception = '%s'"%(e))
                
                
                try:
                    self.TAP_BLOCKOUTBOUND = parser.getboolean('oVPN','wintapblockoutbound')
                    self.debug(1,"def read_options_file: self.TAP_BLOCKOUTBOUND = '%s'" % (self.TAP_BLOCKOUTBOUND))
                except Exception as e:
                    self.debug(1,"def read_options_file: wintapblockoutbound failed, exception = '%s'"%(e))
                
                try:
                    self.NO_DNS_CHANGE = parser.getboolean('oVPN','nodnschange')
                    self.debug(1,"def read_options_file: self.NO_DNS_CHANGE = '%s'" % (self.NO_DNS_CHANGE))
                except Exception as e:
                    self.debug(1,"def read_options_file: nodnschange failed, exception = '%s'"%(e))

                try:
                    LOAD_DATA_EVERY = parser.getint('oVPN','loaddataevery')
                    if LOAD_DATA_EVERY >= 66:
                        self.LOAD_DATA_EVERY = LOAD_DATA_EVERY
                    else:
                        self.LOAD_DATA_EVERY = 900
                        
                    self.debug(1,"def read_options_file: self.LOAD_DATA_EVERY = '%s'" % (self.LOAD_DATA_EVERY))
                except Exception as e:
                    self.debug(1,"def read_options_file: apikey loaddataevery, exception = '%s'"%(e))
                    
                try:
                    MAINWINDOW_SHOWCELLS = json.loads(str(parser.get('oVPN','mainwindowshowcells')))
                    if len(MAINWINDOW_SHOWCELLS) > 0:
                        self.VAR['MAIN']['SHOWCELLS'] = MAINWINDOW_SHOWCELLS
                        self.debug(1,"def read_options_file: self.VAR['MAIN']['SHOWCELLS'] = '%s'" % (self.VAR['MAIN']['SHOWCELLS']))
                except Exception as e:
                    self.debug(1,"def read_options_file: mainwindowshowcells failed, exception = '%s'"%(e))
                    
                try:
                    self.LOAD_ACCDATA = parser.getboolean('oVPN','loadaccinfo')
                    self.debug(1,"def read_options_file: self.LOAD_ACCDATA = '%s'" % (self.LOAD_ACCDATA))
                except Exception as e:
                    self.debug(1,"def read_options_file: loadaccinfo failed, exception = '%s'"%(e))
                
                try:
                    self.LOAD_SRVDATA = parser.getboolean('oVPN','serverviewextend')
                    self.debug(1,"def read_options_file: self.LOAD_SRVDATA = '%s'" % (self.LOAD_SRVDATA))
                except Exception as e:
                    self.debug(1,"def read_options_file: serverviewextend failed, exception = '%s'"%(e))
                
                try:
                    SRV_LIGHT_WIDTH = parser.getint('oVPN','serverviewlightwidth')
                    SRV_LIGHT_HEIGHT = parser.getint('oVPN','serverviewlightheight')
                    SRV_WIDTH = parser.getint('oVPN','serverviewextendwidth')
                    SRV_HEIGHT = parser.getint('oVPN','serverviewextendheight')
                    if SRV_LIGHT_WIDTH >= 1 and SRV_LIGHT_HEIGHT >= 1 and SRV_WIDTH >= 1 and SRV_HEIGHT >= 1:
                        self.SRV_LIGHT_WIDTH = SRV_LIGHT_WIDTH
                        self.SRV_LIGHT_HEIGHT = SRV_LIGHT_HEIGHT
                        self.SRV_WIDTH = SRV_WIDTH
                        self.SRV_HEIGHT = SRV_HEIGHT
                        self.debug(1,"def read_options_file: self.SRV_LIGHT_WIDTH,self.SRV_LIGHT_HEIGHT = '%sx%s'" % (self.SRV_LIGHT_WIDTH,self.SRV_LIGHT_HEIGHT))
                        self.debug(1,"def read_options_file: self.SRV_WIDTH,self.SRV_HEIGHT Window Size = '%sx%s'" % (self.SRV_WIDTH,self.SRV_HEIGHT))
                except Exception as e:
                    self.debug(1,"def read_options_file: serverviewsize failed, exception = '%s'"%(e))
                
                try:
                    self.APP_THEME = parser.get('oVPN','theme')
                    self.debug(1,"def read_options_file: self.APP_THEME = '%s'" % (self.APP_THEME))
                except Exception as e:
                    self.debug(1,"def read_options_file: theme failed, exception = '%s'"%(e))
                
                try:
                    self.ICONS_THEME = parser.get('oVPN','icons')
                    self.load_icons()
                    self.debug(1,"def read_options_file: self.ICONS_THEME = '%s'" % (self.ICONS_THEME))
                except Exception as e:
                    self.debug(1,"def read_options_file: icons failed, exception = '%s'"%(e))
                
                try:
                    self.APP_FONT_SIZE = parser.get('oVPN','font')
                    self.debug(1,"def read_options_file: self.APP_FONT_SIZE = '%s'" % (self.APP_FONT_SIZE))
                except Exception as e:
                    self.debug(1,"def read_options_file: font failed, exception = '%s'"%(e))
                
                try:
                    self.WIN_ENABLE_NOTIFICATIONS = parser.getboolean('oVPN','winnotify')
                    self.debug(1,"def read_options_file: self.WIN_ENABLE_NOTIFICATIONS '%s'" % (self.WIN_ENABLE_NOTIFICATIONS))
                except Exception as e:
                    self.debug(1,"def read_options_file: winnotify failed, exception = '%s'"%(e))
                
                try:
                    self.DISABLE_QUIT_ENTRY = parser.getboolean('oVPN','disablequitentry')
                    self.debug(1,"def read_options_file: self.DISABLE_QUIT_ENTRY '%s'" % (self.DISABLE_QUIT_ENTRY))
                except Exception as e:
                    self.debug(1,"def read_options_file: disablequitentry failed, exception = '%s'"%(e))
                
                try:
                    MYDNS = json.loads(str(parser.get('oVPN','mydns')))
                    if len(MYDNS) > 0:
                        self.MYDNS = MYDNS
                    self.debug(1,"def read_options_file: len(self.MYDNS) == '%s', self.MYDNS == '%s'"%(len(self.MYDNS),self.MYDNS))
                except Exception as e:
                    self.debug(1,"def read_options_file: self.MYDNS = json.loads failed, exception = '%s'"%(e))
                    self.MYDNS = {}
                
                self.debug(1,"def read_options_file: debug 04")
                return True
            
            except Exception as e:
                self.debug(1,"def read_options_file: failed #1, exception = '%s'"%(e))
                self.msgwarn(_("Read config file failed!"),_("Error"))
                try:
                    os.remove(self.OPT_FILE)
                except Exception as e:
                    pass
        
        else:
            self.debug(1,"def read_options_file: create config")
            # We have no config file here at first start, set right values
            self.VPN_CFG = self.VPN_CFGip4
            self.init_localization(None)
            try:
                cfg = open(self.OPT_FILE,'wt')
                #parser = SafeConfigParser()
                parser = configparser.ConfigParser()
                parser.add_section('oVPN')
                parser.set('oVPN','apikey','%s'%(self.APIKEY))
                parser.set('oVPN','debugmode','%s'%(self.DEBUG))
                parser.set('oVPN','applanguage','%s'%(self.APP_LANGUAGE))
                parser.set('oVPN','lastcfgupdate','%s'%(self.LAST_CFG_UPDATE))
                parser.set('oVPN','favserver','%s'%(self.VAR['OVPN']['FAVSRV']))
                parser.set('oVPN','winextdevice','%s'%(self.WIN_EXT_DEVICE))
                parser.set('oVPN','wintapdevice','%s'%(self.WIN_TAP_DEVICE))
                parser.set('oVPN','openvpnexe','%s'%(self.OPENVPN_EXE))
                parser.set('oVPN','autostartdelay','%s'%(self.VAR['CFG']['AS_DELAY_TIME']))
                parser.set('oVPN','autostart','%s'%(self.VAR['CFG']['AUTOSTART']))
                parser.set('oVPN','updateovpnonstart','%s'%(self.UPDATEOVPNONSTART))
                parser.set('oVPN','configversion','%s'%(self.VAR['OVPN']['CFGTYPE']))
                parser.set('oVPN','serverviewextend','%s'%(self.LOAD_SRVDATA))
                parser.set('oVPN','serverviewlightwidth','%s'%(self.SRV_LIGHT_WIDTH_DEFAULT))
                parser.set('oVPN','serverviewlightheight','%s'%(self.SRV_LIGHT_HEIGHT_DEFAULT))
                parser.set('oVPN','serverviewextendwidth','%s'%(self.SRV_WIDTH_DEFAULT))
                parser.set('oVPN','serverviewextendheight','%s'%(self.SRV_HEIGHT_DEFAULT))
                parser.set('oVPN','theme','%s'%(self.APP_THEME))
                parser.set('oVPN','icons','%s'%(self.ICONS_THEME))
                parser.set('oVPN','font','%s'%(self.APP_FONT_SIZE))
                parser.set('oVPN','winresetfirewall','%s'%(self.WIN_RESET_FIREWALL))
                parser.set('oVPN','winbackupfirewall','%s'%(self.WIN_BACKUP_FIREWALL))
                parser.set('oVPN','nowinfirewall','%s'%(self.NO_WIN_FIREWALL))
                parser.set('oVPN','nodnschange','%s'%(self.NO_DNS_CHANGE))
                parser.set('oVPN','winnoaskfwonexit','%s'%(self.WIN_DONT_ASK_FW_EXIT))
                parser.set('oVPN','winfwblockonexit','%s'%(self.WIN_ALWAYS_BLOCK_FW_ON_EXIT))
                parser.set('oVPN','windisableextifondisco','%s'%(self.WIN_DISABLE_EXT_IF_ON_DISCO))
                parser.set('oVPN','wintapblockoutbound','%s'%(self.TAP_BLOCKOUTBOUND))
                parser.set('oVPN','loadaccinfo','%s'%(self.LOAD_ACCDATA))
                parser.set('oVPN','loaddataevery','%s'%(self.LOAD_DATA_EVERY))
                parser.set('oVPN','mainwindowshowcells','%s'%(json.dumps(str(self.VAR['MAIN']['SHOWCELLS']), ensure_ascii=True)))
                parser.set('oVPN','disablequitentry','%s'%(self.DISABLE_QUIT_ENTRY))
                parser.set('oVPN','winnotify','%s'%(self.WIN_ENABLE_NOTIFICATIONS))
                parser.set('oVPN','mydns','False')
                #parser.write(bytes(cfg,locale.getpreferredencoding()))
                parser.write(cfg)
                cfg.close()
                return True
            except Exception as e:
                self.debug(1,"def read_options_file: create failed, exception = '%s'"%(e))
                sys.exit()

    def write_options_file(self):
        if self.isWRITING_OPTFILE == True:
            self.debug(1,"self.isWRITING_OPTFILE == True")
            return False
        self.isWRITING_OPTFILE = True
        self.debug(1,"def write_options_file()")
        try:
            if not self.APIKEY == False:
                if self.SAVE_APIKEY_INFILE == True:
                    APIKEY = self.APIKEY
                else:
                    APIKEY = False
            else:
                APIKEY = False
            cfg = open(self.OPT_FILE,'wt')
            #parser = SafeConfigParser()
            parser = configparser.ConfigParser()
            parser.add_section('oVPN')
            parser.set('oVPN','apikey','%s'%(APIKEY))
            parser.set('oVPN','debugmode','%s'%(self.DEBUG))
            parser.set('oVPN','applanguage','%s'%(self.APP_LANGUAGE))
            parser.set('oVPN','lastcfgupdate','%s'%(self.LAST_CFG_UPDATE))
            parser.set('oVPN','favserver','%s'%(self.VAR['OVPN']['FAVSRV']))
            parser.set('oVPN','winextdevice','%s'%(self.WIN_EXT_DEVICE))
            parser.set('oVPN','wintapdevice','%s'%(self.WIN_TAP_DEVICE))
            parser.set('oVPN','openvpnexe','%s'%(self.OPENVPN_EXE))
            parser.set('oVPN','autostartdelay','%s'%(self.VAR['CFG']['AS_DELAY_TIME']))
            parser.set('oVPN','autostart','%s'%(self.VAR['CFG']['AUTOSTART']))
            parser.set('oVPN','updateovpnonstart','%s'%(self.UPDATEOVPNONSTART))
            parser.set('oVPN','configversion','%s'%(self.VAR['OVPN']['CFGTYPE']))
            parser.set('oVPN','serverviewextend','%s'%(self.LOAD_SRVDATA))
            parser.set('oVPN','serverviewlightwidth','%s'%(self.SRV_LIGHT_WIDTH))
            parser.set('oVPN','serverviewlightheight','%s'%(self.SRV_LIGHT_HEIGHT))
            parser.set('oVPN','serverviewextendwidth','%s'%(self.SRV_WIDTH))
            parser.set('oVPN','serverviewextendheight','%s'%(self.SRV_HEIGHT))
            parser.set('oVPN','theme','%s'%(self.APP_THEME))
            parser.set('oVPN','icons','%s'%(self.ICONS_THEME))
            parser.set('oVPN','font','%s'%(self.APP_FONT_SIZE))
            parser.set('oVPN','winresetfirewall','%s'%(self.WIN_RESET_FIREWALL))
            parser.set('oVPN','winbackupfirewall','%s'%(self.WIN_BACKUP_FIREWALL))
            parser.set('oVPN','nowinfirewall','%s'%(self.NO_WIN_FIREWALL))
            parser.set('oVPN','nodnschange','%s'%(self.NO_DNS_CHANGE))
            parser.set('oVPN','winnoaskfwonexit','%s'%(self.WIN_DONT_ASK_FW_EXIT))
            parser.set('oVPN','winfwblockonexit','%s'%(self.WIN_ALWAYS_BLOCK_FW_ON_EXIT))
            parser.set('oVPN','windisableextifondisco','%s'%(self.WIN_DISABLE_EXT_IF_ON_DISCO))
            parser.set('oVPN','wintapblockoutbound','%s'%(self.TAP_BLOCKOUTBOUND))
            parser.set('oVPN','loadaccinfo','%s'%(self.LOAD_ACCDATA))
            parser.set('oVPN','loaddataevery','%s'%(self.LOAD_DATA_EVERY))
            parser.set('oVPN','mainwindowshowcells','%s'%(json.dumps(self.VAR['MAIN']['SHOWCELLS'], ensure_ascii=True)))
            parser.set('oVPN','disablequitentry','%s'%(self.DISABLE_QUIT_ENTRY))
            parser.set('oVPN','winnotify','%s'%(self.WIN_ENABLE_NOTIFICATIONS))
            parser.set('oVPN','mydns','%s'%(json.dumps(self.MYDNS, ensure_ascii=True)))
            parser.write(cfg)
            cfg.close()
            self.isWRITING_OPTFILE = False
            return True
        except Exception as e:
            self.debug(1,"def write_options_file: failed, exception = '%s'"%(e))
            sys.exit()
        self.isWRITING_OPTFILE = False

    def read_interfaces(self):
        self.debug(1,"def read_interfaces()")
        if self.OS == "win32":
            if self.WIN_RESET_EXT_DEVICE == False:
                if self.win_read_interfaces() == True:
                    if self.win_firewall_export_on_start() == True:
                        if self.win_read_dns_to_backup() == True:
                            if self.read_gateway_from_interface() == True:
                                return True
                            else:
                                i = 0
                                while not self.read_gateway_from_interface():
                                    if i > 5:
                                        return False
                                    time.sleep(5)
                                    i += 1
                                return True
            else:
                self.win_netsh_restore_dns()
                self.WIN_RESET_EXT_DEVICE = False
                if self.win_read_interfaces() == True:
                    if self.win_firewall_export_on_start() == True:
                        if self.win_read_dns_to_backup() == True:
                            if self.read_gateway_from_interface() == True:
                                return True

    def win_read_interfaces(self):
        self.debug(1,"def win_read_interfaces()")
        try:
            print("win_read_interfaces debug 1")
            self.INTERFACES = winregs.get_networkadapterlist(self.DEBUG,False)
            print(self.INTERFACES)
            print("win_read_interfaces debug 2")
            try:
                print("win_read_interfaces debug 2.1")
                if not self.INTERFACES == False and len(self.INTERFACES) < 2:
                    print("win_read_interfaces debug 2.2")
                    self.errorquit(text=_("Could not read your Network Interfaces!"))
                print("win_read_interfaces debug 2.3")
            except Exception as e:
                print("win_read_interfaces debug 4")
                self.errorquit(text=_("Could not read your Network Interfaces!\nPlease rename your network adapters to:\nlan1, lan2, wifi1, wifi1, vpn1, vpn2\nexception: %s") % (e))
            try:
                print("win_read_interfaces debug 5")
                newdata = winregs.get_tapadapters(self.DEBUG,self.OPENVPN_EXE,self.INTERFACES)
                print("win_read_interfaces debug 6")
            except TypeError:
                print("win_read_interfaces debug 7")
                self.errorquit(text=_("Could not read your TAP Network Interfaces!\nPlease rename your network adapters to:\nlan1, lan2, wifi1, wifi1, vpn1, vpn2"))
            print("win_read_interfaces debug 8")
            self.INTERFACES = newdata["INTERFACES"]
            print("win_read_interfaces debug 9")
            self.WIN_TAP_DEVS = newdata["TAP_DEVS"]
            print("win_read_interfaces debug 10")
            self.debug(1,"def win_read_interfaces: self.WIN_TAP_DEVS = '%s'" % (self.WIN_TAP_DEVS))
            self.debug(1,"def win_read_interfaces: self.INTERFACES = '%s'"%(self.INTERFACES))
            if len(self.WIN_TAP_DEVS) == 0:
                if self.upgrade_openvpn() == True:
                    if not self.win_detect_openvpn() == True:
                        self.errorquit(text=_("No OpenVPN TAP-Windows Adapter found!"))
            elif len(self.WIN_TAP_DEVS) == 1 or self.WIN_TAP_DEVS[0] == self.WIN_TAP_DEVICE:
                self.WIN_TAP_DEVICE = self.WIN_TAP_DEVS[0]
            else:
                self.debug(1,"def win_read_interfaces: self.WIN_TAP_DEVS (query) = '%s'" % (self.WIN_TAP_DEVS))
                self.win_select_tapadapter()
            print("debug 2")
            if self.WIN_TAP_DEVICE == False:
                self.errorquit(text=_("No OpenVPN TAP-Adapter found!\nPlease install openVPN!\nURL1: %s\nURL2: %s") % (openvpn.values(DEBUG)["OPENVPN_DL_URL"],openvpn.values(DEBUG)["OPENVPN_DL_URL_ALT"]))
            else:
                #badchars = ["%","&","$"]
                #for char in badchars:
                #   if char in self.WIN_TAP_DEVICE:
                #       self.errorquit(text=_("Invalid characters in '%s'") % char)
                self.debug(1,"def win_read_interfaces: Selected TAP: '%s'" % (self.WIN_TAP_DEVICE))
                self.win_enable_tap_interface()
                self.debug(1,"def win_read_interfaces: remaining INTERFACES = %s (cfg: %s)"%(self.INTERFACES,self.WIN_EXT_DEVICE))
                if len(self.INTERFACES) > 1:
                    if not self.WIN_EXT_DEVICE == False and self.WIN_EXT_DEVICE in self.INTERFACES:
                        self.debug(1,"def win_read_interfaces: loaded self.WIN_EXT_DEVICE %s from options file"%(self.WIN_EXT_DEVICE))
                        return True
                    else:
                        return self.win_select_networkadapter()
                elif len(self.INTERFACES) < 1:
                    self.errorquit(text=_("No Network Adapter found!"))
                else:
                    self.WIN_EXT_DEVICE = self.INTERFACES[0]
                    self.debug(1,"def win_read_interfaces: External Interface = %s"%(self.WIN_EXT_DEVICE))
                    return True
        except Exception as e:
            self.debug(1,"def win_read_interfaces: failed, exception = '%s'"%(e))

    def win_select_tapadapter(self):
        try:
            dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK)
            dialogWindow.set_position(Gtk.WindowPosition.CENTER)
            dialogWindow.set_transient_for(self.window)
            dialogWindow.set_border_width(8)
            try:
                dialogWindow.set_icon(self.app_icon)
            except Exception as e:
                pass
            text = _("Multiple TAPs found!\n\nPlease select your TAP Adapter!")
            dialogWindow.set_title(text)
            dialogWindow.set_markup(text)
            dialogBox = dialogWindow.get_content_area()
            liststore = Gtk.ListStore(str)
            combobox = Gtk.ComboBoxText.new()
            combobox.pack_start(cell, True)
            for INTERFACE in self.WIN_TAP_DEVS:
                self.debug(1,"add tap interface '%s' to combobox" % (INTERFACE))
                combobox.append_text(INTERFACE)
            combobox.connect('changed',self.cb_tap_interface_selector_changed)
            dialogBox.pack_start(combobox,False,False,0)
            dialogWindow.show_all()
            dialogWindow.run()
            dialogWindow.destroy()
        except Exception as e:
            self.debug(1,"def win_select_tapadapter: failed, exception = '%s'"%(e))

    def win_select_networkadapter(self):
        try:
            dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK)
            dialogWindow.set_position(Gtk.WindowPosition.CENTER)
            dialogWindow.set_transient_for(self.window)
            dialogWindow.set_border_width(8)
            try:
                dialogWindow.set_icon(self.app_icon)
            except Exception as e:
                pass
            text = _("Choose your External Network Adapter!")
            dialogWindow.set_title(text)
            dialogWindow.set_markup(text)
            dialogBox = dialogWindow.get_content_area()
            combobox = Gtk.ComboBoxText.new()
            for INTERFACE in self.INTERFACES:
                self.debug(1,"add interface %s to combobox" % (INTERFACE))
                combobox.append_text(INTERFACE)
            combobox.connect('changed',self.cb_interface_selector_changed)
            dialogBox.pack_start(combobox,False,False,0)
            dialogWindow.show_all()
            self.debug(1,"open interface selector")
            dialogWindow.run()
            self.debug(1,"close interface selector")
            dialogWindow.destroy()
            if not self.WIN_EXT_DEVICE == False:
                return True
        except Exception as e:
            self.debug(1,"def win_select_networkadapter: failed, exception = '%s'"%(e))

    def select_userid(self):
        try:
            self.debug(1,"def select_userid()")
            dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK)
            dialogWindow.set_position(Gtk.WindowPosition.CENTER)
            dialogWindow.set_transient_for(self.window)
            dialogWindow.set_border_width(8)
            try:
                dialogWindow.set_icon(self.app_icon)
            except Exception as e:
                pass
            text = _("Please select your User-ID!")
            dialogWindow.set_title(text)
            dialogWindow.set_markup(text)
            dialogBox = dialogWindow.get_content_area()
            liststore = Gtk.ListStore(str)
            combobox = Gtk.ComboBoxText.new()
            for userid in self.PROFILES:
                self.debug(1,"add userid '%s' to combobox" % (userid))
                combobox.append_text(userid)
            combobox.connect('changed',self.cb_select_userid)
            dialogBox.pack_start(combobox,False,False,0)
            dialogWindow.show_all()
            self.debug(1,"open userid selector")
            dialogWindow.run()
            self.debug(1,"close userid interface selector")
            dialogWindow.destroy()
            if self.USERID > 1 and os.path.isdir("%s\\%s" % (self.APP_DIR,self.USERID)):
                return True
        except Exception as e:
            self.debug(1,"def select_userid: failed, exception = '%s'"%(e))

    def on_right_click_mainwindow(self, treeview, event):
        try:
            self.debug(1,"def on_right_click_mainwindow()")
            #self.IDLE_TIME = 0
            self.destroy_systray_menu()
            # get selection, also when treeview is sorted by a row
            servername = False
            pthinfo = self.treeview.get_path_at_pos(int(event.x), int(event.y))
            if pthinfo is not None:
                tree_selection = self.treeview.get_selection()
                (model, pathlist) = tree_selection.get_selected_rows()
                for path in pathlist:
                    tree_iter = model.get_iter(path)
                    servername = model.get_value(tree_iter,2)
            else:
                return False
            if servername:
                if event.button == 1:
                    self.debug(1,"mainwindow left click (%s)" % (servername))
                elif event.button == 3:
                    self.make_context_menu_servertab(servername)
                    self.debug(1,"mainwindow right click (%s)" % (servername))
        except Exception as e:
            self.debug(1,"def on_right_click_mainwindow: failed, exception = '%s'"%(e))

    def make_context_menu_servertab(self,servername):
        self.debug(1,"def make_context_menu_servertab: %s" % (servername))
        try:
            context_menu_servertab = Gtk.Menu()
            self.context_menu_servertab = context_menu_servertab
            
            if self.VAR['OVPN']['CONN']['SERVER'] == servername:
                disconnect = Gtk.MenuItem(_("Disconnect %s")%(self.VAR['OVPN']['CONN']['SERVER']))
                context_menu_servertab.append(disconnect)
                disconnect.connect('button-release-event', self.cb_kill_openvpn)
            else:
                connect = Gtk.MenuItem(_("Connect to %s")%(servername))
                context_menu_servertab.append(connect)
                connect.connect('button-release-event',self.cb_jump_openvpn,servername)
            
            sep = Gtk.SeparatorMenuItem()
            context_menu_servertab.append(sep)
            
            if self.VAR['OVPN']['FAVSRV'] == servername:
                delfavorite = Gtk.MenuItem(_("Remove AutoConnect: %s")%(servername))
                delfavorite.connect('button-release-event',self.cb_del_ovpn_favorite_server,servername)
                context_menu_servertab.append(delfavorite)
            else:
                setfavorite = Gtk.MenuItem(_("Set AutoConnect: %s")%(servername))
                setfavorite.connect('button-release-event',self.cb_set_ovpn_favorite_server,servername)
                context_menu_servertab.append(setfavorite)
            
            sep = Gtk.SeparatorMenuItem()
            context_menu_servertab.append(sep)
            
            self.make_context_menu_servertab_d0wns_dnsmenu(servername)
            
            sep = Gtk.SeparatorMenuItem()
            context_menu_servertab.append(sep)
            
            if self.DISABLE_SRV_WINDOW == False:
                try:
                    if self.LOAD_SRVDATA == True:
                        opt = _("[enabled]")
                    else:
                        opt = _("[disabled]")
                    extserverview = Gtk.MenuItem(_("Load Server Information %s") %(opt))
                    extserverview.connect('button-release-event', self.cb_extserverview)
                    context_menu_servertab.append(extserverview)
                except Exception as e:
                    self.debug(1,"def make_context_menu_servertab: extserverview failed, exception = '%s'"%(e))

                try:
                    if self.LOAD_SRVDATA == True:
                        hidecells = Gtk.MenuItem(_("Hide unwanted cells"))
                        hidecells.connect('button-release-event', self.cb_hide_cells)
                        context_menu_servertab.append(hidecells)
                except Exception as e:
                    self.debug(1,"def make_context_menu_servertab: hidecells failed, exception = '%s'"%(e))

                try:
                    if self.LOAD_SRVDATA == True:
                        WIDTH = self.SRV_WIDTH
                        HEIGHT = self.SRV_HEIGHT
                    else:
                        WIDTH = self.SRV_LIGHT_WIDTH
                        HEIGHT = self.SRV_LIGHT_HEIGHT
                    extserverviewsize = Gtk.MenuItem(_("Set Server-View Size [%sx%s]") %(int(WIDTH),int(HEIGHT)))
                    extserverviewsize.connect('button-release-event', self.cb_extserverview_size)
                    context_menu_servertab.append(extserverviewsize)
                except Exception as e:
                    self.debug(1,"def make_context_menu_servertab: extserverviewsize failed, exception = '%s'"%(e))
                    
                try:
                    loaddataevery = Gtk.MenuItem(_("Update every: %s seconds") %(self.LOAD_DATA_EVERY))
                    loaddataevery.connect('button-release-event', self.cb_set_loaddataevery)
                    context_menu_servertab.append(loaddataevery)
                except Exception as e:
                    self.debug(1,"def make_context_menu_servertab: loaddataevery failed, exception = '%s'"%(e))

            context_menu_servertab.show_all()
            GLib.idle_add(context_menu_servertab.popup,None, None, None, 3, 0, 0)
            self.debug(1,"def make_context_menu_servertab: return")
            return
        except Exception as e:
            self.debug(1,"def make_context_menu_servertab: failed, exception = '%s'"%(e))

    def make_context_menu_servertab_d0wns_dnsmenu(self,servername):
        try:
            self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: servername = '%s'" % (servername))
            
            if D0WNDNS == True and len(self.d0wns_DNS) == 0:
                self.load_d0wns_dns()
            
            dnsmenu = Gtk.Menu()
            dnsm = Gtk.MenuItem(_("Change DNS"))
            dnsm.set_submenu(dnsmenu)
            
            try:
                pridns = self.MYDNS[servername]["primary"]["ip4"]
                priname = self.MYDNS[servername]["primary"]["dnsname"]
                string = _("Primary DNS: %s (%s)") % (priname,pridns)
                pridnsm = Gtk.MenuItem(string)
                cbdata = {servername:{"primary":{"ip4":pridns,"dnsname":priname}}}
                pridnsm.connect('button-release-event',self.cb_del_dns,cbdata)
                self.context_menu_servertab.append(pridnsm)
                self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: pridns = '%s', priname = '%s'"%(pridns,priname))
            except Exception as e:
                pridns = False
            
            try:
                secdns = self.MYDNS[servername]["secondary"]["ip4"]
                secname = self.MYDNS[servername]["secondary"]["dnsname"]
                string = _("Secondary DNS: %s (%s)") % (secname,secdns)
                secdnsm = Gtk.MenuItem(string)
                cbdata = {servername:{"secondary":{"ip4":secdns,"dnsname":secname}}}
                secdnsm.connect('button-release-event',self.cb_del_dns,cbdata)
                self.context_menu_servertab.append(secdnsm)
                self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: secdns = '%s', secname = '%s'"%(secdns,secname))
            except Exception as e:
                secdns = False
            
            dnsdict = OrderedDict(sorted(self.d0wns_DNS.items(), key=lambda k: (k[1]['countrycode'],k), reverse=False))
            self.debug(59,"dnsdict = '%s'" % (dnsdict)) 
            i=0
            for name,value in dnsdict.items():
                try:
                    self.debug(59,"try name = '%s', len(value) = '%s', value = '%s'" % (name,len(value),value))
                    
                    dnsip4 = value['ip4']
                    countrycode = value['countrycode']
                    
                    dnssubmenu = Gtk.Menu()
                    dnssubmtext = "%s (%s)" % (name,dnsip4)
                    dnssubm = Gtk.ImageMenuItem(dnssubmtext)
                    dnssubm.set_submenu(dnssubmenu)
                    img = Gtk.Image()
                    imgfile = self.decode_flag(countrycode)
                    img.set_from_pixbuf(imgfile)
                    dnssubm.set_always_show_image(True)
                    dnssubm.set_image(img)
                    dnsmenu.append(dnssubm)
                    
                    try:
                        cbdata = {servername:{"primary":{"ip4":dnsip4,"dnsname":name}}}
                        if pridns == dnsip4:
                            string = _("Primary DNS '%s' @ %s") % (pridns,servername)
                            setpridns = Gtk.MenuItem(string)
                            setpridns.connect('button-release-event',self.cb_del_dns,cbdata)
                        else:
                            setpridns = Gtk.MenuItem(_("Set Primary DNS"))
                            setpridns.connect('button-release-event',self.cb_set_dns,cbdata)
                        dnssubmenu.append(setpridns)
                    except Exception as e:
                        self.debug(1,"dnssubmenu.append(setpridns) failed, exception = '%s'"%(e))
                    
                    try:
                        cbdata = {servername:{"secondary":{"ip4":dnsip4,"dnsname":name}}}
                        if secdns == dnsip4:
                            string = _("Secondary DNS '%s' @ %s") % (secdns,servername)
                            setsecdns = Gtk.MenuItem(string)
                            setsecdns.connect('button-release-event',self.cb_del_dns,cbdata)
                        else:
                            setsecdns = Gtk.MenuItem(_("Set Secondary DNS"))
                            setsecdns.connect('button-release-event',self.cb_set_dns,cbdata)
                        dnssubmenu.append(setsecdns)
                    except Exception as e:
                        self.debug(1,"dnssubmenu.append(setsecdns) failed, exception = '%s'"%(e))
                        
                    self.debug(59,"dnsmenu.append name = '%s' i=%s" % (name,i))
                    i += 1
                except Exception as e:
                    self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: dnsmenu.append(dnssubm) '%s' failed " % (countrycode))
                
            dnsm.show_all()
            self.context_menu_servertab.append(dnsm)
        except Exception as e:
            self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: failed, exception = '%s'"%(e))

    def systray_timer(self):
        try:
            self.debug(10,"def systray_timer()")
            starttime = time.time()
            self.systray_timer_running = True
            if self.stop_systray_timer == True:
                self.systray_timer_running = False
                return False
            
            if not self.systray_menu == False:
                self.check_hide_popup()
            
            try:
                self.debug(10,"self.LAST_MSGWARN_WINDOW = '%s'" % (self.LAST_MSGWARN_WINDOW))
                if self.LAST_MSGWARN_WINDOW > 0 and (int(time.time())-self.LAST_MSGWARN_WINDOW) > 9:
                    self.msgwarn_window.destroy()
                    self.LAST_MSGWARN_WINDOW = 0
            except Exception as e:
                pass
            
            if self.UPDATE_SWITCH == True and self.SETTINGSWINDOW_OPEN == True:
                self.debug(1,"def systray_timer: UPDATE_SWITCH")
                
                # Language changed
                if self.LANG_FONT_CHANGE == True:
                    if self.VAR['MAIN']['OPEN'] == True:
                        self.mainwindow.set_title(_("Server"))
                    if self.SETTINGSWINDOW_OPEN == True:
                        self.settingswindow.set_title(_("Settings"))
                    if self.ACCWINDOW_OPEN == True:
                        self.accwindow.set_title(_("Account"))
                    
                    self.debug(1,"def systray_timer: self.LANG_FONT_CHANGE == True")
                    pages = [self.nbpage0, self.nbpage1, self.nbpage2, self.nbpage3]
                    for page in pages:
                        try:
                            if not page == False:
                                self.settingsnotebook.remove(page)
                        except Exception as e:
                            self.debug(1,"def systray_timer: remove page '%s' failed, exception = '%s'"%(page,e))
                    try:
                        self.show_hide_security_window()
                        self.show_hide_options_window()
                        self.show_hide_updates_window()
                        self.settingswindow.show_all()
                        self.settingsnotebook.set_current_page(1)
                    except Exception as e:
                        self.debug(1,"def systray_timer: settingswindow failed, exception = '%s'"%(page,e))
                    self.LANG_FONT_CHANGE = False
                
                if self.state_openvpn() == True:
                    self.switch_fw.set_sensitive(False)
                    self.switch_fwblockonexit.set_sensitive(False)
                    self.switch_fwdontaskonexit.set_sensitive(False)
                    self.switch_fwresetonconnect.set_sensitive(False)
                    self.switch_fwbackupmode.set_sensitive(False)
                    self.switch_nodns.set_sensitive(False)
                    self.button_switch_network_adapter.set_sensitive(False)
                    try:
                        self.settingsnotebook.remove(self.nbpage3)
                    except Exception as e:
                        pass
                elif self.NO_WIN_FIREWALL == True:
                    self.switch_fwblockonexit.set_sensitive(False)
                    self.switch_fwdontaskonexit.set_sensitive(False)
                    self.switch_fwresetonconnect.set_sensitive(False)
                    self.switch_fwbackupmode.set_sensitive(False)
                    self.switch_tapblockoutbound.set_sensitive(False)
                else:
                    self.switch_fw.set_sensitive(True)
                    self.switch_fwblockonexit.set_sensitive(True)
                    self.switch_fwdontaskonexit.set_sensitive(True)
                    self.switch_fwresetonconnect.set_sensitive(True)
                    self.switch_fwbackupmode.set_sensitive(True)
                    self.switch_nodns.set_sensitive(True)
                    self.button_switch_network_adapter.set_sensitive(True)
                    try:
                        self.settingsnotebook.remove(self.nbpage3)
                    except Exception as e:
                        pass
                    try:
                        self.show_hide_backup_window()
                        self.settingswindow.show_all()
                    except Exception as e:
                        pass
                
                # def settings_firewall_switch_nofw()
                if self.NO_WIN_FIREWALL == True:
                    self.switch_fw.set_active(False)
                    try:
                        self.settingsnotebook.remove(self.nbpage3)
                    except Exception as e:
                        pass
                else:
                    self.switch_fw.set_active(True)
                
                # def settings_firewall_switch_tapblockoutbound()
                if self.TAP_BLOCKOUTBOUND == True:
                    self.switch_tapblockoutbound.set_active(True)
                else:
                    self.switch_tapblockoutbound.set_active(False)
                
                # def settings_firewall_switch_fwblockonexit()
                if self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == True:
                    self.switch_fwblockonexit.set_active(True)
                else:
                    self.switch_fwblockonexit.set_active(False)
                
                # def settings_firewall_switch_fwdontaskonexit()
                if self.WIN_DONT_ASK_FW_EXIT == True:
                    self.switch_fwdontaskonexit.set_active(True)
                else:
                    self.switch_fwdontaskonexit.set_active(False)
                
                # def settings_firewall_switch_fwresetonconnect()
                if self.WIN_RESET_FIREWALL == True:
                    self.switch_fwresetonconnect.set_active(True)
                else:
                    self.switch_fwresetonconnect.set_active(False)
                
                # def settings_firewall_switch_fwbackupmode()
                if self.WIN_BACKUP_FIREWALL == True:
                    self.switch_fwbackupmode.set_active(True)
                else:
                    self.switch_fwbackupmode.set_active(False)
                
                # def settings_network_switch_nodns()
                if self.NO_DNS_CHANGE == True:
                    self.switch_nodns.set_active(False)
                else:
                    self.switch_nodns.set_active(True)
                
                # settings_network_switch_disableextifondisco
                if self.WIN_DISABLE_EXT_IF_ON_DISCO == True:
                    self.switch_disableextifondisco.set_active(True)
                else:
                    self.switch_disableextifondisco.set_active(False)
                
                # settings_options_switch_autostart
                if self.VAR['CFG']['AUTOSTART'] == True:
                    self.switch_autostart.set_active(True)
                    self.combobox_time.set_button_sensitivity(Gtk.SensitivityType.OFF)
                else:
                    self.switch_autostart.set_active(False)
                    self.combobox_time.set_button_sensitivity(Gtk.SensitivityType.ON)
                
                # settings_options_switch_updateovpnonstart
                if self.UPDATEOVPNONSTART == True:
                    self.switch_updateovpnonstart.set_active(True)
                else:
                    self.switch_updateovpnonstart.set_active(False)
                
                # settings_options_switch_accinfo
                if self.LOAD_ACCDATA == True and not self.APIKEY == False:
                    self.switch_accinfo.set_active(True)
                else:
                    self.switch_accinfo.set_active(False)
                
                # settings_options_switch_srvinfo
                if self.LOAD_SRVDATA == True and not self.APIKEY == False:
                    self.switch_srvinfo.set_active(True)
                else:
                    self.switch_srvinfo.set_active(False)
                
                # settings_options_switch_debugmode
                if self.DEBUG == True:
                    self.switch_debugmode.set_active(True)
                else:
                    self.switch_debugmode.set_active(False)
                
                # settings_options_button_ipv6
                if self.VAR['OVPN']['CFGTYPE'] == "23x":
                    self.button_title.set_label(_("Current: IPv4 Entry Server with Exit to IPv4 (standard)"))
                    self.button_ipmode.set_label(_("Use IPv4 Entry Server with Exits to IPv4 + IPv6"))
                elif self.VAR['OVPN']['CFGTYPE'] == "23x46":
                    self.button_title.set_label(_("Current: IPv4 Entry Server with Exits to IPv4 + IPv6"))
                    self.button_ipmode.set_label(_("Use IPv4 Entry Server with Exit to IPv4 (standard)"))
                
                # settings_options_combobox_icons
                if self.ICONS_THEME == "standard":
                    active_item = 0
                if self.ICONS_THEME == "classic":
                    active_item = 1
                if self.ICONS_THEME == "classic2":
                    active_item = 2
                if self.ICONS_THEME == "shield_bluesync":
                    active_item = 3
                if self.ICONS_THEME == "experimental":
                    active_item = 4
                if self.ICONS_THEME == "private":
                    active_item = 5
                self.combobox_icons.set_active(active_item)
                
                # resize settings window
                self.settingswindow.resize(1,1)
                
                # end switches update
                self.UPDATE_SWITCH = False
            else:
                self.UPDATE_SWITCH = False
            
            systraytext = False
            if self.timer_check_certdl_running == True:
                if not self.STATE_CERTDL == False:
                    if self.STATUS_ICON_BLINK == 0:
                        systrayicon = self.systray_icon_syncupdate1
                    else:
                        systrayicon = self.systray_icon_syncupdate2
                    self.STATUS_ICON_BLINK += 1
                    if self.STATE_CERTDL == "clientupdate":
                        systraytext = _("Checking for Client Update!")
                    elif self.STATE_CERTDL == "clientupdatedl":
                        systraytext = _("Downloading Client Update!")
                    elif self.STATE_CERTDL == "lastupdate":
                        systraytext = _("Checking for Updates!")
                    elif self.STATE_CERTDL == "getconfigs":
                        systraytext = _("Downloading Configurations...")
                    elif self.STATE_CERTDL == "extract":
                        systraytext = _("Extracting Configs and Certs...")
                    statusbar_text = systraytext
                    
            elif self.inThread_jump_server_running == True:
                systraytext = _("Connecting to %s") % (self.VAR['OVPN']['CALL_SRV'])
                systrayicon = self.systray_icon_connect
                statusbar_text = systraytext
                self.debug(1,"def systray_timer: cstate = '%s'" % (systraytext))
                
            elif self.state_openvpn() == True:
                connectedseconds = int(time.time()) - self.VAR['OVPN']['CONN']['START']
                self.VAR['OVPN']['CONN']['SECONDS'] = connectedseconds
                if self.VAR['OVPN']['PING_STAT'] == -2:
                    self.VAR['OVPN']['CONN']['TESTING']= True
                    systraytext = _("Testing connection to %s") % (self.VAR['OVPN']['CONN']['SERVER'])
                    systrayicon = self.systray_icon_testing
                    statusbar_text = systraytext
                    self.debug(1,"def systray_timer: cstate = '%s'" % (systraytext))
                    
                elif self.VAR['OVPN']['PING_LAST'] == -2 and self.VAR['OVPN']['PING_DEAD'] > 1:
                    systraytext = _("Connection unstable or failed! (%s)") % (self.VAR['OVPN']['PING_DEAD'])
                    systrayicon = self.systray_icon_testing
                    statusbar_text = systraytext
                    self.debug(1,"def systray_timer: cstate = '%s'" % (systraytext))
                    if (int(time.time())-self.LAST_OVPN_PING_DEAD_MESSAGE) > 120:
                        self.send_notify(_("Connection unstable or failed!"),_("oVPN"))
                        self.LAST_OVPN_PING_DEAD_MESSAGE = int(time.time())
                        
                elif self.VAR['OVPN']['PING_STAT'] > 0:
                    try:
                        if self.VAR['OVPN']['CONN']['TESTING']== True:
                            self.VAR['OVPN']['PINGS'] = list()
                            self.VAR['OVPN']['PING_STAT'] = self.VAR['OVPN']['PING_LAST']
                            self.VAR['OVPN']['CONN']['TESTING']= False
                        m, s = divmod(connectedseconds, 60)
                        h, m = divmod(m, 60)
                        d, h = divmod(h, 24)
                        if self.VAR['OVPN']['CONN']['SECONDS'] >= 0:
                            connectedtime_text = "%d:%02d:%02d:%02d" % (d,h,m,s)
                        statusbar_text = _("Connected to %s [%s]:%s (%s) [ %s ] (%s / %s ms)") % (self.VAR['OVPN']['CONN']['SERVER'],self.VAR['OVPN']['CONN']['IP'],self.VAR['OVPN']['CONN']['PORT'],self.VAR['OVPN']['CONN']['PROTO'].upper(),connectedtime_text,int(self.VAR['OVPN']['PING_LAST']),int(self.VAR['OVPN']['PING_STAT']))
                        # systraytext Windows only shows the first 64 characters
                        systraytext = "%s [%s]:%s (%s) [%s] %sms" % (self.VAR['OVPN']['CONN']['SERVER'],self.VAR['OVPN']['CONN']['IP'],self.VAR['OVPN']['CONN']['PORT'],self.VAR['OVPN']['CONN']['PROTO'].upper(),connectedtime_text,int(self.VAR['OVPN']['PING_LAST']))
                        systrayicon = self.systray_icon_connected
                    except Exception as e:
                        self.debug(1,"def systray_timer: systraytext failed, exception '%s'"%(e))

            elif self.state_openvpn() == False:
                systraytext = _("Disconnected! Have a nice and anonymous day!")
                self.debug(2,"def systray_timer: cstate = '%s'" % (systraytext))
                statusbar_text = systraytext
                systrayicon = self.systray_icon_disconnected
                try:
                    if len(self.VAR['OVPN']['SERVERLIST']) == 0 and self.INIT_FIRST_UPDATE == True:
                        self.INIT_FIRST_UPDATE = False
                        self.load_ovpn_server()
                        if not self.APIKEY == False and len(self.VAR['OVPN']['SERVERLIST']) == 0:
                            self.debug(1,"zero server found, initiate first update")
                            self.check_remote_update("config")
                    elif len(self.VAR['OVPN']['SERVERLIST']) > 0 and self.INIT_FIRST_UPDATE == True:
                        self.INIT_FIRST_UPDATE = False
                    elif self.VAR['OVPN']['AUTOCONNECT'] == True and not self.VAR['OVPN']['FAVSRV'] == False:
                        self.VAR['OVPN']['AUTOCONNECT'] = False
                        self.debug(1,"def systray_timer: self.VAR['OVPN']['AUTOCONNECT']: self.VAR['OVPN']['FAVSRV'] = '%s'" % (self.VAR['OVPN']['FAVSRV']))
                        self.cb_jump_openvpn(0,0,self.VAR['OVPN']['FAVSRV'])
                    
                except Exception as e:
                    self.debug(1,"def timer_statusbar: OVPN_AUTO_CONNECT_ON_START failed, exception '%s'"%(e))

            try:
                try:
                    # traytext
                    if not self.VAR['CACHE']['systraytext'] == systraytext and not systraytext == False:
                        self.VAR['CACHE']['systraytext'] = systraytext
                        self.tray.set_tooltip_markup(systraytext)
                        self.debug(111,"def systray_timer: update systraytext = '%s'"%(systraytext))
                except Exception as e:
                    self.debug(1,"def systray_timer: set traytext failed, exception '%s'"%(e))
                    
                try:
                    # trayicon
                    if not self.VAR['CACHE']['systrayicon'] == systrayicon:
                        self.VAR['CACHE']['systrayicon'] = systrayicon
                        if self.APP_THEME == "private":
                            self.tray.set_from_file(systrayicon)
                        else:
                            self.tray.set_from_pixbuf(systrayicon)
                except Exception as e:
                    self.debug(1,"def systray_timer: set trayicon failed, exception '%s'"%(e))
                
                try:
                    # statusbar
                    if self.VAR['MAIN']['OPEN'] == True and self.VAR['MAIN']['HIDE'] == False:
                        if not self.VAR['CACHE']['statusbartext'] == statusbar_text:
                            self.set_statusbar_text(statusbar_text)
                            self.VAR['CACHE']['statusbartext'] = statusbar_text
                except Exception as e:
                    self.debug(1,"def systray_timer: set statusbar failed, exception '%s'"%(e))
            except Exception as e:
                self.debug(1,"def systray_timer: set 'traytext, trayicon, statusbar' failed, exception '%s'"%(e))
            
            try:
                if self.timer_load_remote_data_running == False:
                    thread = threading.Thread(target=self.load_remote_data)
                    thread.daemon = True
                    thread.start()
            except Exception as e:
                self.debug(1,"def systray_timer: thread target=self.load_remote_data failed, exception '%s'"%(e))
            runtime = int((time.time()-starttime)*1000)
            if runtime > 10000:
                self.debug(1,"def systray_timer() return runtime = '%s ms'"%(runtime))
            self.systray_timer_running = False
        except Exception as e:
            self.debug(1,"def systray_timer: failed, exception '%s'"%(e))
        return True

    def on_right_click(self, widget, event, event_time):
        self.debug(1,"def on_right_click()")
        if not self.systray_menu == False:
            self.destroy_systray_menu()
        else:
            self.make_systray_menu(event)

    def on_left_click(self, widget):
        self.debug(1,"def on_left_click()")
        if not self.systray_menu == False:
            self.destroy_systray_menu()
        else:
            if self.VAR['MAIN']['OPEN'] == False:
                try:
                    self.load_ovpn_server()
                    if len(self.VAR['OVPN']['SERVERLIST']) > 0:
                        event = Gtk.get_current_event_time()
                        self.show_mainwindow(widget, event)
                except Exception as e:
                    self.debug(1,"def show_mainwindow() on_left_click failed, exception = '%s'"%(e))
            else:
                if self.mainwindow.get_property("visible") == False:
                    self.debug(1,"def on_left_click: unhide Mainwindow")
                    self.VAR['MAIN']['HIDE'] = False
                    self.mainwindow.show()
                else:
                    self.debug(1,"def on_left_click: hide Mainwindow")
                    self.mainwindow.hide()
                    self.VAR['MAIN']['HIDE'] = True
                    return True

    def make_systray_menu(self, event):
        self.debug(1,"def make_systray_menu()")
        try:
            self.systray_menu = Gtk.Menu()
            if self.MOUSELEVEL == True:
                self.MOUSE_IN_TRAY = time.time() + 30
            else:
                self.MOUSE_IN_TRAY = time.time() + 3
            
            try:
                self.load_ovpn_server()
            except Exception as e:
                self.debug(1,"def make_systray_menu: self.load_ovpn_server() failed, exception = '%s'"%(e))
            
            try:
                self.make_systray_server_menu()
            except Exception as e:
                self.debug(1,"def make_systray_menu: self.make_systray_server_menu() failed, exception = '%s'"%(e))
            
            try:
                self.make_systray_openvpn_menu()
            except Exception as e:
                self.debug(1,"def make_systray_menu: self.make_systray_openvpn_menu() failed, exception = '%s'"%(e))
            
            try:
                self.make_systray_bottom_menu()
            except Exception as e:
                self.debug(1,"def make_systray_menu: self.make_systray_bottom_menu() failed, exception = '%s'"%(e))
            
            self.systray_menu.connect('enter-notify-event', self.systray_notify_event_enter,"systray_menu")
            self.systray_menu.show_all()
            GLib.idle_add(self.systray_menu.popup, None, None, None, event, 0, 0)
        except Exception as e:
            self.destroy_systray_menu()
            self.debug(1,"def make_systray_menu: failed, exception = '%s'"%(e))

    def make_systray_server_menu(self):
        self.debug(1,"def make_systray_server_menu()")
        self.COUNTRYNAMES = {'AF':_("Afghanistan"),'AL':_("Albania"),'DZ':_("Algeria"),'AS':_("American Samoa"),'AD':_("Andorra"),'AO':_("Angola"),'AI':_("Anguilla"),'AQ':_("Antarctica"),'AG':_("Antigua and Barbuda"),'AR':_("Argentina"),'AM':_("Armenia"),'AW':_("Aruba"),'AU':_("Australia"),'AT':_("Austria"),'AZ':_("Azerbaijan"),'BS':_("Bahamas"),'BH':_("Bahrain"),'BD':_("Bangladesh"),'BB':_("Barbados"),'BY':_("Belarus"),'BE':_("Belgium"),'BZ':_("Belize"),'BJ':_("Benin"),'BM':_("Bermuda"),'BT':_("Bhutan"),'BO':_("Plurinational State of Bolivia"),'BA':_("Bosnia and Herzegovina"),'BW':_("Botswana"),'BV':_("Bouvet Island"),'BR':_("Brazil"),'IO':_("British Indian Ocean Territory"),'BN':_("Brunei Darussalam"),'BG':_("Bulgaria"),'BF':_("Burkina Faso"),'BI':_("Burundi"),'KH':_("Cambodia"),'CM':_("Cameroon"),'CA':_("Canada"),'CV':_("Cape Verde"),'KY':_("Cayman Islands"),'CF':_("Central African Republic"),'TD':_("Chad"),'CL':_("Chile"),'CN':_("China"),'CX':_("Christmas Island"),'CC':_("Cocos (Keeling) Islands"),'CO':_("Colombia"),'KM':_("Comoros"),'CG':_("Congo"),'CD':_("the Democratic Republic of the Congo"),'CK':_("Cook Islands"),'CR':_("Costa Rica"),'HR':_("Croatia"),'CU':_("Cuba"),'CY':_("Cyprus"),'CZ':_("Czech Republic"),'DK':_("Denmark"),'DJ':_("Djibouti"),'DM':_("Dominica"),'DO':_("Dominican Republic"),'EC':_("Ecuador"),'EG':_("Egypt"),'SV':_("El Salvador"),'GQ':_("Equatorial Guinea"),'ER':_("Eritrea"),'EE':_("Estonia"),'ET':_("Ethiopia"),'FK':_("Falkland Islands (Malvinas)"),'FO':_("Faroe Islands"),'FJ':_("Fiji"),'FI':_("Finland"),'FR':_("France"),'GF':_("French Guiana"),'PF':_("French Polynesia"),'TF':_("French Southern Territories"),'GA':_("Gabon"),'GM':_("Gambia"),'GE':_("Georgia"),'DE':_("Germany"),'GH':_("Ghana"),'GI':_("Gibraltar"),'GR':_("Greece"),'GL':_("Greenland"),'GD':_("Grenada"),'GP':_("Guadeloupe"),'GU':_("Guam"),'GT':_("Guatemala"),'GG':_("Guernsey"),'GN':_("Guinea"),'GW':_("Guinea-Bissau"),'GY':_("Guyana"),'HT':_("Haiti"),'HM':_("Heard Island and McDonald Islands"),'VA':_("Holy See (Vatican City State)"),'HN':_("Honduras"),'HK':_("Hong Kong"),'HU':_("Hungary"),'IS':_("Iceland"),'IN':_("India"),'ID':_("Indonesia"),'IR':_("Islamic Republic of Iran"),'IQ':_("Iraq"),'IE':_("Ireland"),'IM':_("Isle of Man"),'IL':_("Israel"),'IT':_("Italy"),'JM':_("Jamaica"),'JP':_("Japan"),'JE':_("Jersey"),'JO':_("Jordan"),'KZ':_("Kazakhstan"),'KE':_("Kenya"),'KI':_("Kiribati"),'KW':_("Kuwait"),'KG':_("Kyrgyzstan"),'LV':_("Latvia"),'LB':_("Lebanon"),'LS':_("Lesotho"),'LR':_("Liberia"),'LY':_("Libyan Arab Jamahiriya"),'LI':_("Liechtenstein"),'LT':_("Lithuania"),'LU':_("Luxembourg"),'MO':_("Macao"),'MK':_("Macedonia"),'MG':_("Madagascar"),'MW':_("Malawi"),'MY':_("Malaysia"),'MV':_("Maldives"),'ML':_("Mali"),'MT':_("Malta"),'MH':_("Marshall Islands"),'MQ':_("Martinique"),'MR':_("Mauritania"),'MU':_("Mauritius"),'YT':_("Mayotte"),'MX':_("Mexico"),'FM':_("Federated States of Micronesia"),'MD':_("Republic of Moldova"),'MC':_("Monaco"),'MN':_("Mongolia"),'ME':_("Montenegro"),'MS':_("Montserrat"),'MA':_("Morocco"),'MZ':_("Mozambique"),'MM':_("Myanmar"),'NA':_("Namibia"),'NR':_("Nauru"),'NP':_("Nepal"),'NL':_("Netherlands"),'AN':_("Netherlands Antilles"),'NC':_("New Caledonia"),'NZ':_("New Zealand"),'NI':_("Nicaragua"),'NE':_("Niger"),'NG':_("Nigeria"),'NU':_("Niue"),'NF':_("Norfolk Island"),'MP':_("Northern Mariana Islands"),'NO':_("Norway"),'OM':_("Oman"),'PK':_("Pakistan"),'PW':_("Palau"),'PS':_("Occupied Palestinian Territory"),'PA':_("Panama"),'PG':_("Papua New Guinea"),'PY':_("Paraguay"),'PE':_("Peru"),'PH':_("Philippines"),'PN':_("Pitcairn"),'PL':_("Poland"),'PT':_("Portugal"),'PR':_("Puerto Rico"),'QA':_("Qatar"),'RE':_("Reunion"),'RO':_("Romania"),'RU':_("Russian Federation"),'RW':_("Rwanda"),'BL':_("Saint Barthelemy"),'SH':_("Saint Helena"),'KN':_("Saint Kitts and Nevis"),'LC':_("Saint Lucia"),'MF':_("Saint Martin (French part)"),'PM':_("Saint Pierre and Miquelon"),'VC':_("Saint Vincent and the Grenadines"),'WS':_("Samoa"),'SM':_("San Marino"),'ST':_("Sao Tome and Principe"),'SA':_("Saudi Arabia"),'SN':_("Senegal"),'RS':_("Serbia"),'SC':_("Seychelles"),'SL':_("Sierra Leone"),'SG':_("Singapore"),'SK':_("Slovakia"),'SI':_("Slovenia"),'SB':_("Solomon Islands"),'SO':_("Somalia"),'ZA':_("South Africa"),'GS':_("South Georgia and the South Sandwich Islands"),'ES':_("Spain"),'LK':_("Sri Lanka"),'SD':_("Sudan"),'SR':_("Suriname"),'SJ':_("Svalbard and Jan Mayen"),'SZ':_("Swaziland"),'SE':_("Sweden"),'CH':_("Switzerland"),'SY':_("Syrian Arab Republic"),'TW':_("Taiwan"),'TJ':_("Tajikistan"),'TZ':_("United Republic of Tanzania"),'TH':_("Thailand"),'TL':_("Timor-Leste"),'TG':_("Togo"),'TK':_("Tokelau"),'TO':_("Tonga"),'TT':_("Trinidad and Tobago"),'TN':_("Tunisia"),'TR':_("Turkey"),'TM':_("Turkmenistan"),'TC':_("Turks and Caicos Islands"),'TV':_("Tuvalu"),'UG':_("Uganda"),'UA':_("Ukraine"),'AE':_("United Arab Emirates"),'GB':_("United Kingdom"),'UK':_("United Kingdom"),'US':_("United States"),'UM':_("United States Minor Outlying Islands"),'UY':_("Uruguay"),'UZ':_("Uzbekistan"),'VU':_("Vanuatu"),'VE':_("Bolivarian Republic of Venezuela"),'VN':_("Viet Nam"),'VG':_("British Virgin Islands"),'VI':_("U.S. Virgin Islands"),'WF':_("Wallis and Futuna"),'EH':_("Western Sahara"),'YE':_("Yemen"),'ZM':_("Zambia"),'ZW':_("Zimbabwe")}
        if len(self.VAR['OVPN']['SERVERLIST']) > 0:
            try:
                countrycodefrombefore = 0
                for servername in self.VAR['OVPN']['SERVERLIST']:
                    servershort = servername.split(".")[0].upper()
                    
                    textstring = "%s [%s]:%s (%s)" % (servershort,self.VAR['OVPN']['CONFIGDATA'][servershort][0],self.VAR['OVPN']['CONFIGDATA'][servershort][1],self.VAR['OVPN']['CONFIGDATA'][servershort][2])
                    countrycode = servershort[:2]
                    #print "string = %s, countrycode = %s" % (textstring,countrycode)
                    
                    if not countrycodefrombefore == countrycode:
                        # create countrygroup menu
                        countrycodefrombefore = countrycode
                        cgmenu = Gtk.Menu()
                        cgmenu.connect('enter-notify-event', self.systray_notify_event_enter,"sub_cgmenu")
                        cgmenu.connect('leave-notify-event', self.systray_notify_event_leave,"sub_cgmenu")
                        self.cgmenu = cgmenu
                        try:
                            countryname = self.COUNTRYNAMES[countrycode]
                        except Exception as e:
                            countryname = countrycode
                        
                        try:
                            cgm = Gtk.ImageMenuItem(countryname)
                            img = Gtk.Image()
                            try:
                                imgfile = self.decode_flag(countrycode)
                                img.set_from_pixbuf(imgfile)
                                cgm.set_always_show_image(True)
                                cgm.set_image(img)
                                cgm.set_submenu(cgmenu)
                                self.systray_menu.append(cgm)
                            except Exception as e:
                                self.debug(1,"def make_systray_server_menu: countrycode = '%s' failed" % (countrycode))
                                self.destroy_systray_menu()
                        except Exception as e:
                            self.destroy_systray_menu()
                            self.debug(1,"def make_systray_server_menu: flagimg group1 failed, exception = '%s'"%(e))
                    
                    if self.VAR['OVPN']['CONN']['SERVER'] == servername:
                        textstring = servershort+_(" [ disconnect ]")
                        serveritem = Gtk.ImageMenuItem(textstring)
                        serveritem.connect('button-release-event', self.cb_kill_openvpn)
                    else:
                        serveritem = Gtk.ImageMenuItem(textstring)
                        serveritem.connect('button-release-event', self.cb_jump_openvpn, servername)
                    
                    img = Gtk.Image()
                    imgfile = self.decode_flag(countrycode)
                    img.set_from_pixbuf(imgfile)
                    serveritem.set_always_show_image(True)
                    serveritem.set_image(img)
                    cgmenu.append(serveritem)

            except Exception as e:
                self.destroy_systray_menu()
                self.debug(1,"def make_systray_server_menu: failed, exception = '%s'"%(e))

    def make_systray_openvpn_menu(self):
        self.debug(1,"def make_systray_openvpn_menu()")
        if self.state_openvpn() == True:
            try:
                sep = Gtk.SeparatorMenuItem()
                servershort = self.VAR['OVPN']['CONN']['SERVER'].split(".")[0].upper()
                textstring = '%s @ [%s]:%s (%s)' % (servershort,self.VAR['OVPN']['CONN']['IP'],self.VAR['OVPN']['CONN']['PORT'],self.VAR['OVPN']['CONN']['PROTO'].upper())
                disconnect = Gtk.ImageMenuItem(textstring)
                img = Gtk.Image()
                if self.APP_THEME == "private":
                    img.set_from_file(self.systray_icon_disconnected_traymenu)
                else:
                    img.set_from_pixbuf(self.systray_icon_disconnected_traymenu)
                disconnect.set_always_show_image(True)
                disconnect.set_image(img)
                self.systray_menu.append(sep)
                self.systray_menu.append(disconnect)
                disconnect.connect('button-release-event', self.cb_kill_openvpn)
            except Exception as e:
                self.debug(1,"def make_systray_openvpn_menu: failed, exception = '%s'"%(e))

    def make_systray_bottom_menu(self):
        self.debug(1,"def make_systray_bottom_menu()")
        
        sep = Gtk.SeparatorMenuItem()
        self.systray_menu.append(sep)
        
        try:
            accwindowentry = False
            if self.ACCWINDOW_OPEN == True:
                accwindowentry = Gtk.MenuItem(_("Close Account"))
            else:
                if self.LOAD_ACCDATA == True and not self.APIKEY == False:
                    accwindowentry = Gtk.MenuItem(_("Account"))
            if accwindowentry:
                self.systray_menu.append(accwindowentry)
                accwindowentry.connect('button-release-event', self.show_accwindow)
                accwindowentry.connect('leave-notify-event', self.systray_notify_event_leave,"accwindowentry")
        except Exception as e:
            self.debug(1,"def make_systray_bottom_menu: accwindowentry failed, exception = '%s'"%(e))
        
        try:
            if self.SETTINGSWINDOW_OPEN == True:
                settwindowentry = Gtk.MenuItem(_("Close Settings"))
            else:
                settwindowentry = Gtk.MenuItem(_("Settings"))
            self.systray_menu.append(settwindowentry)
            settwindowentry.connect('button-release-event', self.show_settingswindow)
            settwindowentry.connect('leave-notify-event', self.systray_notify_event_leave,"settwindowentry")
        except Exception as e:
            self.debug(1,"def make_systray_bottom_menu: settwindowentry failed, exception = '%s'"%(e))
        
        if self.DISABLE_QUIT_ENTRY == True and self.state_openvpn() == True:
            pass
        else:
            try:
                sep = Gtk.SeparatorMenuItem()
                self.systray_menu.append(sep)
                about = Gtk.MenuItem(_("About"))
                self.systray_menu.append(about)
                about.connect('button-release-event', self.show_about_dialog)
                about.connect('leave-notify-event', self.systray_notify_event_leave,"about")
            except Exception as e:
                self.debug(1,"def make_systray_bottom_menu: about failed, exception = '%s'"%(e))
            
            # add quit item
            quit = Gtk.MenuItem(_("Quit"))
            if self.state_openvpn() == True:
                quit.set_sensitive(False)
            self.systray_menu.append(quit)
            quit.connect('button-release-event', self.on_closing)
            quit.connect('leave-notify-event', self.systray_notify_event_leave,"quit")

    def systray_notify_event_leave(self, widget, event, data = None):
        self.debug(10,"def systray_notify_event_leave() data = '%s'" % (data))
        self.MOUSE_IN_TRAY = time.time() + 1

    def systray_notify_event_enter(self, widget, event, data = None):
        self.debug(10,"def systray_notify_event_enter() data = '%s'" % (data))
        self.MOUSE_IN_TRAY = time.time() + 30

    def check_hide_popup(self):
        self.debug(10,"def check_hide_popup()")
        if self.MOUSE_IN_TRAY < time.time():
            self.destroy_systray_menu()

    def check_remote_update(self,option):
        self.debug(1,"def check_remote_update(option=%s)"%(option))
        if self.timer_check_certdl_running == False:
            self.debug(1,"def check_remote_update: check_inet_connection() == True")
            try:
                thread_certdl = threading.Thread(target=lambda option=option: self.inThread_timer_check_update(option))
                thread_certdl.daemon = True
                thread_certdl.start()
                threadid_certdl = threading.currentThread()
                self.debug(1,"def check_remote_update: threadid_certdl = %s" %(threadid_certdl))
                return True
            except Exception as e:
                self.debug(1,"def check_remote_update: starting thread_certdl failed, exception = '%s'"%(e))
        else:
            self.debug(1,"def check_remote_update: timer_check_certdl_running failed, exception = '%s'"%(e))
        return False

    def inThread_timer_check_update(self,option):
        self.debug(1,"def inThread_timer_check_update(option=%s)"%(option))
        if self.check_inet_connection() == False:
            self.msgwarn(_("Could not connect to %s") % (API_DOMAIN),_("Error"))
            return False
        try:
            self.STATUS_ICON_BLINK = 0
            self.STATE_CERTDL = "lastupdate"
            self.timer_check_certdl_running = True
            try:
                self.load_ovpn_server()
                if len(self.VAR['OVPN']['SERVERLIST']) == 0:
                    self.reset_last_update()
            except Exception as e:
                self.debug(1,"def inThread_timer_check_update: self.load_ovpn_server() failed, exception = '%s'"%(e))
            if option == "client":
                self.STATE_CERTDL = "clientupdate"
                if self.API_REQUEST(API_ACTION = "winrelease_url"):
                    return self.thread_finish_check_update(True)
            elif option == "config" and self.API_REQUEST(API_ACTION = self.STATE_CERTDL):
                if self.check_last_server_update(self.curldata):
                    self.STATE_CERTDL = "getconfigs"
                    if self.API_REQUEST(API_ACTION = self.STATE_CERTDL):
                        if self.extract_ovpn():
                            self.VAR['OVPN']['SERVERLIST'] = list()
                            if self.load_ovpn_server() == True:
                                self.rebuild_mainwindow()
                            self.msgwarn(_("Configurations updated!"),_("Success"))
                            return self.thread_finish_check_update(True)
                        else:
                            self.msgwarn(_("Extraction failed!"),_("Error"))
                    else:
                        self.msgwarn(_("Download failed!"),_("Error"))
                else:
                    self.msgwarn(_("No config update available!"),_("Success"))
                    return self.thread_finish_check_update(True)
        except Exception as e:
            self.msgwarn(_("Update failed with Exception '%s'!"),_("Error"))
        return self.thread_finish_check_update(False)
        
    def thread_finish_check_update(self,retval):
        self.win_firewall_clear_vcp_rules()
        self.timer_check_certdl_running = False
        self.STATE_CERTDL = False
        self.debug(1,"def thread_finish_check_update(retval=%s)"%(retval))
        return retval

    def update_mwls(self):
        self.debug(1,"def update_mwls()")
        try:
            liststore = self.serverliststore
            debugupdate_mwls = False
            starttime = time.time()
            for row in liststore:
                server = row[2]
                if server in self.VAR['OVPN']['SERVERLIST']:
                    if debugupdate_mwls: self.debug(1,"def update_mwls: server '%s'" % (server))
                    servershort = server.split(".")[0].upper()
                    if row[2] == server:
                        value = False
                        iter = liststore.get_iter_first()
                        while iter != None and liststore.get_value(iter,2) != server:
                            iter = liststore.iter_next(iter)
                        value = liststore.get_value(iter,2)
                        cellnumber = 0
                        row_changed = 0
                        while cellnumber <= 27:
                            try:
                                oldvalue = row[cellnumber]
                                serverip4  = str(self.VAR['OVPN']['CONFIGDATA'][servershort][0])
                                serverport = str(self.VAR['OVPN']['CONFIGDATA'][servershort][1])
                                serverproto = str(self.VAR['OVPN']['CONFIGDATA'][servershort][2])
                                servercipher = str(self.VAR['OVPN']['CONFIGDATA'][servershort][3])
                                try:
                                    servermtu = str(self.VAR['OVPN']['CONFIGDATA'][servershort][4])
                                except Exception as e:
                                    servermtu = str(1500)
                                if cellnumber == 0:
                                    if self.LOAD_SRVDATA == True and len(self.VAR['OVPN']['SERVERDATA']) >= 1:
                                        try:
                                            serverstatus = self.VAR['OVPN']['SERVERDATA'][servershort]["status"]
                                            if server == self.VAR['OVPN']['CONN']['SERVER']:
                                                statusimg = self.decode_icon("shield_go")
                                            elif server == self.VAR['OVPN']['FAVSRV']:
                                                statusimg = self.decode_icon("star")
                                            elif serverstatus == "0":
                                                statusimg = self.decode_icon("bullet_red")
                                            elif serverstatus == "1":
                                                statusimg = self.decode_icon("bullet_green")
                                            elif serverstatus == "2":
                                                statusimg = self.decode_icon("bullet_white")
                                        except Exception as e:
                                            self.debug(1,"def update_mwls: self.VAR['OVPN']['SERVERDATA'][%s]['status'] not found" % (servershort))
                                            break
                                    else:
                                        if server == self.VAR['OVPN']['CONN']['SERVER']:
                                            statusimg = self.decode_icon("shield_go")
                                        elif server == self.VAR['OVPN']['FAVSRV']:
                                            statusimg = self.decode_icon("star")
                                        else:
                                            statusimg = self.decode_icon("bullet_white")
                                    try:
                                        liststore.set_value(iter,cellnumber,statusimg)
                                        row_changed += 1
                                    except Exception as e:
                                        self.debug(1,"self.serverliststore.append: statusimg '%s'" % (server))
                                    
                                elif cellnumber == 1:
                                    pass
                                
                                elif cellnumber == 2:
                                    pass
                                
                                elif cellnumber == 3 and not row[cellnumber] == serverip4:
                                    liststore.set_value(iter,cellnumber,serverip4)
                                    row_changed += 1
                                    if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' serverip4" % (server))
                                
                                elif cellnumber == 5 and not row[cellnumber] == serverport:
                                    liststore.set_value(iter,cellnumber,serverport)
                                    row_changed += 1
                                    if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' serverport" % (server))
                                
                                elif cellnumber == 6 and not row[cellnumber] == serverproto:
                                    liststore.set_value(iter,cellnumber,serverproto)
                                    row_changed += 1
                                    if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' serverproto" % (server))
                                
                                elif cellnumber == 7 and not row[cellnumber] == servermtu:
                                    liststore.set_value(iter,cellnumber,servermtu)
                                    row_changed += 1
                                    if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' servermtu" % (server))
                                
                                elif cellnumber == 8 and not row[cellnumber] == servercipher:
                                    liststore.set_value(iter,cellnumber,servercipher)
                                    row_changed += 1
                                    if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' servercipher" % (server))
                                elif self.LOAD_SRVDATA == True and len(self.VAR['OVPN']['SERVERDATA']) >= 1:
                                    try:
                                        vlanip4 = str(self.VAR['OVPN']['SERVERDATA'][servershort]["vlanip4"])
                                        vlanip6 = str(self.VAR['OVPN']['SERVERDATA'][servershort]["vlanip6"])
                                        live = str("%s Mbps" % self.VAR['OVPN']['SERVERDATA'][servershort]["traffic"]["live"])
                                        uplink = str(self.VAR['OVPN']['SERVERDATA'][servershort]["traffic"]["uplink"])
                                        cpuinfo = str(self.VAR['OVPN']['SERVERDATA'][servershort]["info"]["cpu"])
                                        raminfo = str(self.VAR['OVPN']['SERVERDATA'][servershort]["info"]["ram"])
                                        hddinfo = str(self.VAR['OVPN']['SERVERDATA'][servershort]["info"]["hdd"])
                                        traffic = str(self.VAR['OVPN']['SERVERDATA'][servershort]["traffic"]["eth0"])
                                        cpuload = str(self.VAR['OVPN']['SERVERDATA'][servershort]["cpu"]["cpu-load"])
                                        cpuovpn = str(self.VAR['OVPN']['SERVERDATA'][servershort]["cpu"]["cpu-ovpn"])
                                        cpusshd = str(self.VAR['OVPN']['SERVERDATA'][servershort]["cpu"]["cpu-sshd"])
                                        cpusock = str(self.VAR['OVPN']['SERVERDATA'][servershort]["cpu"]["cpu-sock"])
                                        cpuhttp = str(self.VAR['OVPN']['SERVERDATA'][servershort]["cpu"]["cpu-http"])
                                        cputinc = str(self.VAR['OVPN']['SERVERDATA'][servershort]["cpu"]["cpu-tinc"])
                                        ping4 = str(self.VAR['OVPN']['SERVERDATA'][servershort]["pings"]["ipv4"])
                                        ping6 = str(self.VAR['OVPN']['SERVERDATA'][servershort]["pings"]["ipv6"])
                                        serverip6 = str(self.VAR['OVPN']['SERVERDATA'][servershort]["extip6"])
                                        
                                        if cellnumber == 4 and not row[cellnumber] == serverip6:
                                            liststore.set_value(iter,cellnumber,serverip6)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' serverip6" % (server))
                                            
                                        elif cellnumber == 9 and not row[cellnumber] == live:
                                            liststore.set_value(iter,cellnumber,live)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' live" % (server))
                                        
                                        elif cellnumber == 10 and not row[cellnumber] == uplink:
                                            liststore.set_value(iter,cellnumber,uplink)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' uplink" % (server))
                                        
                                        elif cellnumber == 11 and not row[cellnumber] == vlanip4:
                                            liststore.set_value(iter,cellnumber,vlanip4)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' vlanip4" % (server))
                                        
                                        elif cellnumber == 12 and not row[cellnumber] == vlanip6:
                                            liststore.set_value(iter,cellnumber,vlanip6)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' vlanip6" % (server))
                                        
                                        elif cellnumber == 13 and not row[cellnumber] == cpuinfo:
                                            liststore.set_value(iter,cellnumber,cpuinfo)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' cpuinfo" % (server))
                                        
                                        elif cellnumber == 14 and not row[cellnumber] == raminfo:
                                            liststore.set_value(iter,cellnumber,raminfo)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' raminfo" % (server))
                                        
                                        elif cellnumber == 15 and not row[cellnumber] == hddinfo:
                                            liststore.set_value(iter,cellnumber,hddinfo)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' hddinfo" % (server))
                                        
                                        elif cellnumber == 16 and not row[cellnumber] == traffic:
                                            liststore.set_value(iter,cellnumber,traffic)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' traffic" % (server))
                                        
                                        elif cellnumber == 17 and not row[cellnumber] == cpuload:
                                            liststore.set_value(iter,cellnumber,cpuload)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' cpuload" % (server))
                                        
                                        elif cellnumber == 18 and not row[cellnumber] == cpuovpn:
                                            liststore.set_value(iter,cellnumber,cpuovpn)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' cpuovpn" % (server))
                                        
                                        elif cellnumber == 19 and not row[cellnumber] == cpusshd:
                                            liststore.set_value(iter,cellnumber,cpusshd)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' cpusshd" % (server))
                                        
                                        elif cellnumber == 20 and not row[cellnumber] == cpusock:
                                            liststore.set_value(iter,cellnumber,cpusock)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' cpusock" % (server))
                                        
                                        elif cellnumber == 21 and not row[cellnumber] == cpuhttp:
                                            liststore.set_value(iter,cellnumber,cpuhttp)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' cpuhttp" % (server))
                                        
                                        elif cellnumber == 22 and not row[cellnumber] == cputinc:
                                            liststore.set_value(iter,cellnumber,cputinc)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' cputinc" % (server))
                                        
                                        elif cellnumber == 23 and not row[cellnumber] == ping4:
                                            liststore.set_value(iter,cellnumber,ping4)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' ping4" % (server))
                                        
                                        elif cellnumber == 24 and not row[cellnumber] == ping6:
                                            liststore.set_value(iter,cellnumber,ping6)
                                            row_changed += 1
                                            if debugupdate_mwls: self.debug(1,"def update_mwls: updated server '%s' ping6" % (server))
                                        elif cellnumber == 25:
                                            pass
                                        elif cellnumber == 26:
                                            pass
                                        elif cellnumber == 27:
                                            pass
                                    except Exception as e:
                                        pass
                                        # we may fail silently for private servers
                                        #self.debug(11,"def update_mwls: extended values '%s' failed" % (server))
                            except Exception as e:
                                self.debug(1,"def update_mwls: #0 failed ")
                            cellnumber += 1
                            # end while cellnumber
                        if row_changed >= 1:
                            path = liststore.get_path(iter)
                            liststore.row_changed(path,iter)
                            self.debug(10,"def update_mwls: row_changed server '%s'" % (server))
            runtime = int((time.time()-starttime)*1000)
            if runtime > 10000:
                self.debug(1,"def update_mwls: return '%s ms'" % (runtime))
            self.debug(1,"def update_mwls: return True")
            return None
        except Exception as e:
            self.debug(1,"def update_mwls: failed, exception = '%s'"%(e))
        return False


    def call_redraw_mainwindow(self):
        self.debug(1,"def call_redraw_mainwindow()")
        if self.VAR['MAIN']['OPEN'] == True and self.VAR['MAIN']['HIDE'] == False:
            self.VAR['CACHE']['statusbartext'] = False
            try:
                GLib.idle_add(self.update_mwls)
            except Exception as e:
                self.debug(1,"def call_redraw_mainwindow: try #1 failed, exception = '%s'"%(e))

    def rebuild_mainwindow(self):
        GLib.idle_add(self.rebuild_mainwindow_glib)

    def rebuild_mainwindow_glib(self):
        try:
            if self.VAR['MAIN']['OPEN'] == True:
                if self.VAR['MAIN']['HIDE'] == True:
                    try:
                        self.destroy_mainwindow()
                        return False
                    except Exception as e:
                        return False
                else:
                    
                    try:
                        self.mainwindow.remove(self.mainwindow_vbox)
                        self.debug(1,"def rebuild_mainwindow_glib: removed vbox from mainwindow")
                    except Exception as e:
                        self.debug(1,"def rebuild_mainwindow_glib: no vbox in mainwindow")
                    
                    try:
                        if self.mainwindow_ovpn_server():
                            if self.fill_mainwindow_with_server():
                                if self.update_mwls() == None:
                                    GLib.idle_add(self.mainwindow.show_all)
                                    self.debug(1,"def rebuild_mainwindow_glib: GLib.idle_add(self.mainwindow.show_all)")
                                    return
                                else:
                                    self.debug(1,"def rebuild_mainwindow_glib: self.update_mwls() == False")
                            else:
                                self.debug(1,"def rebuild_mainwindow_glib: self.fill_mainwindow_with_server() == False")
                        else:
                            self.debug(1,"def rebuild_mainwindow_glib: self.mainwindow_ovpn_server() == False")
                    except Exception as e:
                        self.debug(1,"def rebuild_mainwindow_glib: fill window failed, exception = '%s'"%(e))
        except Exception as e:
            self.debug(1,"def rebuild_mainwindow_glib: failed, exception = '%s'"%(e))
        self.destroy_mainwindow()
        return False

    def show_mainwindow(self,widget,event):
        self.debug(1,"def show_mainwindow()")
        self.destroy_systray_menu()
        self.reset_load_remote_timer()
        self.VAR['CACHE']['statusbartext'] = False
        if self.VAR['MAIN']['OPEN'] == False:
            self.load_ovpn_server()
            try:
                self.mainwindow = Gtk.Window(Gtk.WindowType.TOPLEVEL)
                self.mainwindow.set_position(Gtk.WindowPosition.CENTER)
                self.mainwindow.connect("destroy",self.cb_destroy_mainwindow)
                self.mainwindow.connect("key-release-event",self.cb_reset_load_remote_timer)
                self.mainwindow.set_title(_("Server"))
                self.mainwindow.set_icon(self.app_icon)
                self.rebuild_mainwindow()
                self.VAR['MAIN']['OPEN'] = True
                return True
            except Exception as e:
                self.VAR['MAIN']['OPEN'] = False
                self.debug(1,"def show_mainwindow: mainwindow failed, exception = '%s'"%(e))
                return False
        else:
            self.destroy_mainwindow()

    def cell_sort(self, treemodel, iter1, iter2, user_data):
        try:
            self.debug(16,"def cell_sort()")
            sort_column, _ = treemodel.get_sort_column_id()
            iter1 = treemodel.get_value(iter1, sort_column)
            iter2 = treemodel.get_value(iter2, sort_column)
            if float(iter1) < float(iter2):
                return -1
            elif float(iter1) == float(iter2):
                return 0
            else:
                return 1
        except Exception as e:
            return 0
            self.debug(1,"def cell_sort: failed, exception = '%s'"%(e))

    def cell_sort_traffic(self, treemodel, iter1, iter2, user_data):
        try:
            self.debug(16,"def cell_sort_traffic()")
            sort_column, _ = treemodel.get_sort_column_id()
            data1 = treemodel.get_value(iter1, sort_column)
            data2 = treemodel.get_value(iter2, sort_column)
            if data1 == "-1":
                data1 = "0 MiB"
            if data2 == "-1":
                data2 = "0 MiB"
            
            # Do not sort for iter1[2], iter1[3], because traffic is unique enough
            iter1 = data1.split(" ")
            number1 = float(iter1[0])
            byte1 = iter1[1]
            # MiB unchanged
            if byte1 == "GiB":
                number1 = number1 * 1024                
            elif byte1 == "TiB":
                number1 = number1 * 1048576
            
            iter2 = data2.split(" ")
            number2 = float(iter2[0])
            byte2 = iter2[1]
            # MiB unchanged
            if byte2 == "GiB":
                number2 = number2 * 1024                
            elif byte2 == "TiB":
                number2 = number2 * 1048576
            
            if float(number1) < float(number2):
                return -1
            elif float(number1) == float(number2):
                return 0
            else:
                return 1
        except Exception as e:
            self.debug(1,"def cell_sort_traffic: failed, exception = '%s'"%(e))
            return 0

    def cell_sort_mbps(self, treemodel, iter1, iter2, user_data):
        try:
            self.debug(16,"def cell_sort_mbps()")
            sort_column, _ = treemodel.get_sort_column_id()
            data1 = treemodel.get_value(iter1, sort_column)
            data2 = treemodel.get_value(iter2, sort_column)
            
            iter1 = data1.split(" ")
            iter2 = data2.split(" ")
            number1 = float(iter1[0])
            number2 = float(iter2[0])
            
            if float(number1) < float(number2):
                return -1
            elif float(number1) == float(number2):
                return 0
            else:
                return 1
        except Exception as e:
            self.debug(1,"def cell_sort_mbps: failed, exception = '%s'"%(e))
            return 0

    def mainwindow_ovpn_server(self):
        self.debug(1,"def mainwindow_ovpn_server()")
        try:
            self.mainwindow_vbox = Gtk.VBox(False,1)
            self.mainwindow.add(self.mainwindow_vbox)
            
            if self.VAR['OVPN']['CFGTYPE'] == "23x":
                mode = "IPv4"
            elif self.VAR['OVPN']['CFGTYPE'] == "23x46":
                mode = "IPv4 + IPv6"
            elif self.VAR['OVPN']['CFGTYPE'] == "23x64":
                mode = "IPv6 + IPv4"
            
            label = Gtk.Label(_("oVPN Server [ %s ]") % (mode))
            self.serverliststore = Gtk.ListStore(GdkPixbuf.Pixbuf,GdkPixbuf.Pixbuf,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,GdkPixbuf.Pixbuf,str)
            self.treeview = Gtk.TreeView(self.serverliststore)
            self.treeview.connect("button-release-event",self.on_right_click_mainwindow)
            self.scrolledwindow = Gtk.ScrolledWindow()
            self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            self.scrolledwindow.set_size_request(64,48)
            self.scrolledwindow.add(self.treeview)
            self.mainwindow_vbox.pack_start(self.scrolledwindow,True,True,0)
            
            try:
                cell = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(' ',cell, pixbuf=0)
                self.treeview.append_column(column)
                cell = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(' ',cell, pixbuf=1)
                column.set_fixed_width(30)
                self.treeview.append_column(column)
                
                try:
                    ## cell 0 == statusicon
                    ## cell 1 == flagicon
                    cellnumber = 2
                    for cellid,cellname in self.VAR['MAIN']['CELLINDEX'].items():
                        if not cellnumber == 26:
                            self.debug(2,"def cellname = '%s'" % (cellname))
                            align=0.5
                            if cellnumber in [ 9, 23, 24 ]:
                                align=1
                            if cellnumber in [ 3, 4, 11, 12, 13, 16 ]:
                                align=0
                            cell = Gtk.CellRendererText(xalign=align)
                            column = Gtk.TreeViewColumn(" %s " % (cellname), cell, text=cellnumber)
                            
                            # cell sorting stuff
                            if cellnumber in [ 2, 5, 6, 7, 9, 10, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25 ]:
                                column.set_sort_column_id(cellnumber)
                                # Add sort function for str cells
                                if not cellnumber in [ 2, 6, 9, 16, 25 ]: # sortable but text str, cannot convert to float, 9+16 needs own sort_func
                                    self.serverliststore.set_sort_func(cellnumber, self.cell_sort, None)
                                if cellnumber == 9:
                                    self.serverliststore.set_sort_func(cellnumber, self.cell_sort_mbps, None)
                                if cellnumber == 16:
                                    self.serverliststore.set_sort_func(cellnumber, self.cell_sort_traffic, None)
                            
                            # Hide colums in light server view
                            if self.LOAD_SRVDATA == False:
                                if cellnumber in [ 4, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25 ]:
                                    column.set_visible(False)
                            elif self.LOAD_SRVDATA == True:
                                if cellnumber in self.VAR['MAIN']['ALLOWCELLHIDE']:
                                    if not cellnumber in self.VAR['MAIN']['SHOWCELLS']:
                                        column.set_visible(False)
                                    else:
                                        column.set_visible(True)
                            self.treeview.append_column(column)
                            cellnumber = cellnumber + 1
                    try:
                        # RightFlagIcon
                        cell = Gtk.CellRendererPixbuf()
                        cellnumber = 26
                        column = Gtk.TreeViewColumn(' ',cell, pixbuf=cellnumber)
                        column.set_fixed_width(30)
                        if self.LOAD_SRVDATA == False:
                            column.set_visible(False)
                        else:
                            if cellnumber in self.VAR['MAIN']['ALLOWCELLHIDE']:
                                    if not cellnumber in self.VAR['MAIN']['SHOWCELLS']:
                                        column.set_visible(False)
                        self.treeview.append_column(column)
                        
                        # Spacer
                        cell = Gtk.CellRendererText()
                        cellnumber = 27
                        column = Gtk.TreeViewColumn(' ',cell, text=cellnumber)
                        column.set_fixed_width(1)
                        self.treeview.append_column(column)
                        
                        # statusbar
                        self.statusbar_text = Gtk.Label()
                        self.mainwindow_vbox.pack_start(self.statusbar_text,False,False,0)
                        
                        if self.LOAD_SRVDATA == True:
                            WIDTH = self.SRV_WIDTH
                            HEIGHT = self.SRV_HEIGHT
                            self.mainwindow.resize(int(WIDTH),int(HEIGHT))
                        else:
                            WIDTH = self.SRV_LIGHT_WIDTH
                            HEIGHT = self.SRV_LIGHT_HEIGHT
                            self.mainwindow.resize(int(WIDTH),int(HEIGHT))
                        
                        return True
                    except Exception as e:
                        self.debug(1,"def mainwindow_ovpn_server: final failed , exception = '%s'"%(e))
                except Exception as e:
                    self.debug(1,"def mainwindow_ovpn_server: for cellid,cellname in failed , exception = '%s'"%(e))
            except Exception as e:
                self.debug(1,"def mainwindow_ovpn_server: Gtk.CellRendererPixbuf failed, exception = '%s'"%(e))
        except Exception as e:
            self.debug(1,"def mainwindow_ovpn_server: server-window failed, exception = '%s'"%(e))
        return False

    def fill_mainwindow_with_server(self):
        try:
            if len(self.VAR['OVPN']['SERVERLIST']) == 0:
                self.debug(1,"def fill_mainwindow_with_server: 0 server in self.VAR['OVPN']['SERVERLIST'], return False")
                return False
            for server in self.VAR['OVPN']['SERVERLIST']:
                countrycode = server[:2]
                servershort = server.split(".")[0].upper()
                statusimg = self.decode_icon("bullet_white")
                countryimg = self.decode_flag(countrycode)
                serverip4  = self.VAR['OVPN']['CONFIGDATA'][servershort][0]
                serverport = self.VAR['OVPN']['CONFIGDATA'][servershort][1]
                serverproto = self.VAR['OVPN']['CONFIGDATA'][servershort][2]
                servercipher = self.VAR['OVPN']['CONFIGDATA'][servershort][3]
                try:
                    servermtu = self.VAR['OVPN']['CONFIGDATA'][servershort][4]
                except Exception as e:
                    servermtu = 1500
                self.serverliststore.append([statusimg,countryimg,str(server),str(serverip4),str("-1"),str(serverport),str(serverproto),str(servermtu),str(servercipher),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str(servershort),countryimg,str("")])
                self.debug(1,"def fill_mainwindow_with_server: server = '%s'"%(server))
            return True
        except Exception as e:
            self.debug(1,"def fill_mainwindow_with_server: failed, exception = '%s'"%(e))
        return False

    def destroy_mainwindow(self):
        self.debug(1,"def destroy_mainwindow()")
        GLib.idle_add(self.mainwindow.destroy)
        self.VAR['MAIN']['OPEN'] = False
        self.VAR['MAIN']['HIDE'] = False
        self.statusbar_text = False

    def destroy_debugwindow(self):
        self.debug(1,"def destroy_debugwindow()")
        GLib.idle_add(self.debug_window.destroy)
        self.DEBUGWINDOW_OPEN = False
        
    def call_redraw_accwindow(self):
        self.debug(1,"def call_redraw_accwindow()")
        if self.ACCWINDOW_OPEN == True:
            try:
                self.accwindow.remove(self.accwindow_accinfo_vbox)
                self.accwindow_accinfo()
                self.debug(1,"def call_redraw_accwindow: True")
            except Exception as e:
                self.debug(1,"def call_redraw_accwindow: False")

    def show_accwindow(self,widget,event):
        self.debug(1,"def show_accwindow()")
        self.destroy_systray_menu()
        if self.ACCWINDOW_OPEN == False:
            try:
                self.accwindow = Gtk.Window(Gtk.WindowType.TOPLEVEL)
                self.accwindow.set_position(Gtk.WindowPosition.CENTER)
                self.accwindow.connect("destroy",self.cb_destroy_accwindow)
                self.accwindow.connect("key-release-event",self.cb_reset_load_remote_timer)
                self.accwindow.set_title(_("Account"))
                try:
                    self.accwindow.set_icon(self.app_icon)
                except Exception as e:
                    pass
                self.accwindow.set_default_size(370,480)
                self.accwindow_accinfo()
                self.ACCWINDOW_OPEN = True
                self.reset_load_remote_timer()
                return True
            except Exception as e:
                self.ACCWINDOW_OPEN = False
                self.debug(1,"def show_accwindow: accwindow failed, exception = '%s'"%(e))
                return False
        else:
            self.destroy_accwindow()

    def accwindow_accinfo(self):
        self.debug(1,"def accwindow_accinfo()")
        self.accwindow_accinfo_vbox = Gtk.VBox(False,0)
        self.accwindow.add(self.accwindow_accinfo_vbox)
        if len(self.OVPN_ACC_DATA) == 0:
            if self.LOAD_ACCDATA == False:
                text = _("Settings -> Updates: 'Load Account Info' [disabled]")
            else:
                text = _("No data loaded!\nRetry in few seconds...")
            entry = Gtk.Label()
            entry.set_text(text)
            self.accwindow_accinfo_vbox.pack_start(entry,True,True,0)
        elif len(self.OVPN_ACC_DATA) > 0:
            try:
                self.debug(10,"def accwindow_accinfo: try get values")
                for key, value in sorted(self.OVPN_ACC_DATA.items()):
                    #print key
                    value1 = False
                    if key == "001":
                        head = "User-ID"
                    elif key == "002":
                        head = "Service"
                        if int(value) == ((2**31)-1):
                            value1 = "Lifetime"
                        else:
                            value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S [CE(S)T]')
                    elif key == "003":
                        head = "Balance EUR"
                        value1 = round(int(value),0) / 100
                    elif key == "004":
                        head = "Saved Days"
                    elif key == "005":
                        head = "Last Login"
                        value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S [CE(S)T]')
                    elif key == "006":
                        head = "Login Count"
                    elif key == "007":
                        head = "Login Fail Count"
                    elif key == "008":
                        head = "Last Failed Login"
                        value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S [CE(S)T]')
                    elif key == "009":
                        head = "eMail verified"
                    elif key == "010":
                        head = "Last eMail sent"
                        value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S [CE(S)T]')
                    elif key == "020":
                        head = "Last Update Request"
                        value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S [CE(S)T]')
                    elif key == "022":
                        head = "API Counter WIN"
                    elif key == "021":
                        head = "API Counter LIN"
                    elif key == "023":
                        head = "API Counter MAC"
                    elif key == "024":
                        head = "API Counter AND"
                    elif key == "030":
                        head = "IPv6 enabled"
                    elif key == "999":
                        for coin,addr in sorted(value.items()):
                            try:
                                text = "%s: '%s'" % (coin.upper(),addr)
                                #print text
                                entry = Gtk.Entry()
                                entry.set_max_length(128)
                                entry.set_editable(0)
                                entry.set_text(text)
                                self.accwindow_accinfo_vbox.pack_start(entry,True,True,0)
                            except Exception as e:
                                self.debug(1,"def accwindow_accinfo: coin '%s' failed" % (coin))
                        break
                    else:
                        head = key
                    if value1 == False:
                        value1 = value
                    text = "%s: %s" % (head,value1)
                    self.debug(10,"def accwindow_accinfo: key [%s] = '%s' value = '%s'" % (key,head,value))
                    try:
                        entry = Gtk.Entry()
                        entry.set_max_length(128)
                        entry.set_editable(0)
                        entry.set_text(text)
                        self.accwindow_accinfo_vbox.pack_start(entry,True,True,0)
                    except Exception as e:
                        self.debug(1,"def accwindow_accinfo: accdata vbox.pack_start entry failed!")
            except Exception as e:
                self.debug(1,"def accwindow_accinfo: self.OVPN_ACC_DATA failed, exception = '%s'"%(e))
        GLib.idle_add(self.accwindow.show_all)
        return

    def destroy_accwindow(self):
        self.debug(1,"def destroy_accwindow()")
        GLib.idle_add(self.accwindow.destroy)
        self.ACCWINDOW_OPEN = False
        self.debug(1,"def destroy_accwindow")

    def show_settingswindow(self,widget,event):
        self.destroy_systray_menu()
        if self.SETTINGSWINDOW_OPEN == False:
            try:
                self.settingswindow = Gtk.Window(Gtk.WindowType.TOPLEVEL)
                self.settingswindow.set_position(Gtk.WindowPosition.CENTER)
                self.settingswindow.connect("destroy",self.cb_destroy_settingswindow)
                self.settingswindow.set_title(_("Settings"))
                try:
                    self.settingswindow.set_icon(self.app_icon)
                except Exception as e:
                    pass
                self.settingsnotebook = Gtk.Notebook()
                self.settingswindow.add(self.settingsnotebook)
                
                self.show_hide_security_window()
                self.show_hide_options_window()
                self.show_hide_updates_window()
                
                self.UPDATE_SWITCH = True
                GLib.idle_add(self.settingswindow.show_all)
                self.SETTINGSWINDOW_OPEN = True
                return True
            except Exception as e:
                self.SETTINGSWINDOW_OPEN = False
                self.debug(1,"def show_settingswindow: settingswindow failed, exception = '%s'"%(e))
                return False
        else:
            self.destroy_settingswindow()

    def show_hide_security_window(self):
        try:
            self.nbpage0 = Gtk.VBox(False,spacing=2)
            self.nbpage0.set_border_width(8)
            
            self.settings_firewall_switch_nofw(self.nbpage0)
            self.settings_firewall_switch_fwblockonexit(self.nbpage0)
            self.settings_firewall_switch_fwdontaskonexit(self.nbpage0)
            self.settings_firewall_switch_fwresetonconnect(self.nbpage0)
            self.settings_firewall_switch_fwbackupmode(self.nbpage0)
            self.settings_network_switch_nodns(self.nbpage0)
            self.settings_firewall_switch_tapblockoutbound(self.nbpage0)
            self.settings_network_switch_disableextifondisco(self.nbpage0)
            
            self.settingsnotebook.append_page(self.nbpage0, Gtk.Label(_(" Security ")))
        except Exception as e:
            self.debug(1,"def show_settingswindow: nbpage0 failed, exception = '%s'"%(e))

    def show_hide_options_window(self):
        try:
            self.nbpage1 = Gtk.VBox(False,spacing=2)
            self.nbpage1.set_border_width(8)
            
            ##
            self.nbpage1_h0 = Gtk.HBox(False, spacing=2)
            
            self.nbpage1_h0_v1 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h0.pack_start(self.nbpage1_h0_v1,True,True,0)
            self.settings_options_switch_autostart(self.nbpage1_h0_v1)
            
            self.nbpage1_h0_v2 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h0.pack_start(self.nbpage1_h0_v2,True,True,0)
            self.settings_options_combobox_time(self.nbpage1_h0_v2)
            
            self.nbpage1.pack_start(self.nbpage1_h0,False,False,0)
            ##
            
            ##
            self.settings_options_switch_updateovpnonstart(self.nbpage1)
            
            ##
            self.nbpage1_h3 = Gtk.HBox(False, spacing=2)
            
            self.nbpage1_h3_v1 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h3.pack_start(self.nbpage1_h3_v1,True,True,0)
            self.settings_options_switch_accinfo(self.nbpage1_h3_v1)
            
            self.nbpage1_h3_v2 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h3.pack_start(self.nbpage1_h3_v2,True,True,0)
            self.settings_options_switch_srvinfo(self.nbpage1_h3_v2)
            
            self.nbpage1.pack_start(self.nbpage1_h3,False,False,0)
            ##
            
            self.settings_options_switch_winnotify(self.nbpage1)
            self.settings_options_switch_disablequit(self.nbpage1)
            self.settings_options_switch_debugmode(self.nbpage1)
            ##
            
            ##
            self.nbpage1_h1 = Gtk.HBox(False, spacing=2)
            
            self.nbpage1_h1_v1 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h1.pack_start(self.nbpage1_h1_v1,True,True,0)
            self.settings_options_combobox_theme(self.nbpage1_h1_v1)
            
            self.nbpage1_h1_v2 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h1.pack_start(self.nbpage1_h1_v2,True,True,0)
            self.settings_options_combobox_icons(self.nbpage1_h1_v2)
            
            self.nbpage1.pack_start(self.nbpage1_h1,False,False,0)
            ##
            
            ##
            self.nbpage1_h2 = Gtk.HBox(False, spacing=2)
            
            self.nbpage1_h2_v1 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h2.pack_start(self.nbpage1_h2_v1,True,True,0)
            self.settings_options_combobox_fontsize(self.nbpage1_h2_v1)
            
            self.nbpage1_h2_v2 = Gtk.VBox(False, spacing=0)
            self.nbpage1_h2.pack_start(self.nbpage1_h2_v2,True,True,0)
            self.settings_options_combobox_language(self.nbpage1_h2_v2)
            
            self.nbpage1.pack_start(self.nbpage1_h2,False,False,0)
            ##
            
            self.settingsnotebook.append_page(self.nbpage1, Gtk.Label(_(" Options ")))
        except Exception as e:
            self.debug(1,"def show_settingswindow: nbpage1 failed, exception = '%s'"%(e))

    def show_hide_updates_window(self):
        try:
            self.nbpage2 = Gtk.VBox(False,spacing=2)
            self.nbpage2.set_border_width(8)
            
            self.settings_updates_button_clientupdate(self.nbpage2)
            self.settings_updates_button_normalconf(self.nbpage2)
            self.settings_updates_button_forceconf(self.nbpage2)
            self.settings_options_button_ipv6(self.nbpage2)
            self.settings_options_button_networkadapter(self.nbpage2)
            self.settings_updates_button_apireset(self.nbpage2)
            
            self.settingsnotebook.append_page(self.nbpage2, Gtk.Label(_(" Updates ")))
        except Exception as e:
            self.debug(1,"def show_settingswindow: nbpage2 failed, exception = '%s'"%(e))

    def show_hide_backup_window(self):
        try:
            self.load_firewall_backups()
            if len(self.FIREWALL_BACKUPS) > 0 and self.NO_WIN_FIREWALL == False and self.state_openvpn() == False:
                self.nbpage3 = Gtk.VBox(False,spacing=2)
                self.nbpage3.set_border_width(8)
                self.nbpage3.pack_start(Gtk.Label(label=_("Restore Firewall Backups\n")),False,False,0)
                self.settings_firewall_switch_backuprestore(self.nbpage3)
                self.settingsnotebook.append_page(self.nbpage3, Gtk.Label(_(" Backups ")))
        except Exception as e:
            self.debug(1,"def show_hide_backup_window: nbpage3 failed, exception = '%s'"%(e))

    def settings_firewall_switch_nofw(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_fw = switch
            checkbox_title = Gtk.Label(label=_("Use Windows Firewall (default: ON) "))
            if self.NO_WIN_FIREWALL == True:
                switch.set_active(False)
            else:
                switch.set_active(True)
            switch.connect("notify::state", self.cb_settings_firewall_switch_nofw)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_firewall_switch_nofw: failed, exception = '%s'"%(e))

    def cb_settings_firewall_switch_nofw(self,switch,gparam):
        if self.state_openvpn() == True:
            self.UPDATE_SWITCH = True
            return
        self.debug(1,"def cb_settings_firewall_switch_nofw()")
        if switch.get_active():
            self.NO_WIN_FIREWALL = False
            self.WIN_DONT_ASK_FW_EXIT = True
        else:
            self.NO_WIN_FIREWALL = True
        self.write_options_file()
        self.ask_loadorunload_fw()
        self.UPDATE_SWITCH = True

    def settings_firewall_switch_tapblockoutbound(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_tapblockoutbound = switch
            checkbox_title = Gtk.Label(label=_("TAP-Adapter block outbound (default: OFF)"))
            if self.TAP_BLOCKOUTBOUND == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_firewall_switch_tapblockoutbound)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_firewall_switch_tapblockoutbound: failed, exception = '%s'"%(e))

    def cb_settings_firewall_switch_tapblockoutbound(self,switch,gparam):
        if self.NO_WIN_FIREWALL == True or self.inThread_jump_server_running == True or self.win_firewall_tap_blockoutbound_running == True:
            self.UPDATE_SWITCH = True
            return
        self.debug(1,"def cb_settings_firewall_switch_tapblockoutbound()")
        if switch.get_active():
            self.TAP_BLOCKOUTBOUND = True
        else:
            self.TAP_BLOCKOUTBOUND = False
        thread = threading.Thread(target=self.win_firewall_tap_blockoutbound)
        thread.daemon = True
        thread.start()
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_firewall_switch_fwblockonexit(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_fwblockonexit = switch
            checkbox_title = Gtk.Label(label=_("Block Internet on Disconnect or Quit (default: ON)"))
            if self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_firewall_switch_fwblockonexit)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_firewall_switch_fwblockonexit: failed, exception = '%s'"%(e))

    def cb_settings_firewall_switch_fwblockonexit(self,switch,gparam):
        if self.NO_WIN_FIREWALL == True or self.state_openvpn() == True:
            self.UPDATE_SWITCH = True
            return
        self.debug(1,"def cb_settings_firewall_switch_fwblockonexit()")
        if switch.get_active():
            self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = True
        else:
            self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = False
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_firewall_switch_fwdontaskonexit(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_fwdontaskonexit = switch
            checkbox_title = Gtk.Label(label=_("Disable FW question on Quit (default: OFF)"))
            if self.WIN_DONT_ASK_FW_EXIT == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_firewall_switch_fwdontaskonexit)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_firewall_switch_fwblockonexit: failed, exception = '%s'"%(e))

    def cb_settings_firewall_switch_fwdontaskonexit(self,switch,gparam):
        if self.NO_WIN_FIREWALL == True or self.state_openvpn() == True:
            self.UPDATE_SWITCH = True
            return
        self.debug(1,"def cb_settings_firewall_switch_fwdontaskonexit()")
        if switch.get_active():
            self.WIN_DONT_ASK_FW_EXIT = True
        else:
            self.WIN_DONT_ASK_FW_EXIT = False
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_firewall_switch_fwresetonconnect(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_fwresetonconnect = switch
            checkbox_title = Gtk.Label(label=_("Clear Rules on Connect (default: OFF)"))
            if self.WIN_RESET_FIREWALL == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_firewall_switch_fwresetonconnect)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_firewall_switch_fwresetonconnect: failed, exception = '%s'"%(e))

    def cb_settings_firewall_switch_fwresetonconnect(self,switch,gparam):
        if self.NO_WIN_FIREWALL == True or self.state_openvpn() == True:
            self.UPDATE_SWITCH = True
            return
        self.debug(1,"def cb_settings_firewall_switch_fwresetonconnect()")
        if switch.get_active():
            self.WIN_RESET_FIREWALL = True
            if not self.win_firewall_export_on_start():
                self.msgwarn(_("Could not export Windows Firewall Backup!"),_("Error"))
        else:
            self.WIN_RESET_FIREWALL = False
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_firewall_switch_fwbackupmode(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_fwbackupmode = switch
            checkbox_title = Gtk.Label(label=_("Backup on Start / Restore on Quit (default: OFF)"))
            if self.WIN_BACKUP_FIREWALL == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_firewall_switch_fwbackupmode)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_firewall_switch_fwbackupmode: failed, exception = '%s'"%(e))

    def cb_settings_firewall_switch_fwbackupmode(self,switch,gparam):
        if self.NO_WIN_FIREWALL == True or self.state_openvpn() == True:
            self.UPDATE_SWITCH = True
            return
        self.debug(1,"def cb_settings_firewall_switch_fwbackupmode()")
        if switch.get_active():
            self.WIN_BACKUP_FIREWALL = True
            if not self.win_firewall_export_on_start():
                self.msgwarn(_("Could not export Windows Firewall Backup!"),_("Error"))
        else:
            self.WIN_BACKUP_FIREWALL = False
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_network_switch_nodns(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_nodns = switch
            checkbox_title = Gtk.Label(label=_("DNS Leak Protection (default: ON)"))
            if self.NO_DNS_CHANGE == True:
                switch.set_active(False)
            else:
                switch.set_active(True)
            switch.connect("notify::state", self.cb_switch_nodns)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_network_switch_nodns: failed, exception = '%s'"%(e))

    def cb_switch_nodns(self,switch,gparam):
        if self.state_openvpn() == True:
            self.UPDATE_SWITCH = True
            return
        self.debug(1,"def cb_switch_nodns()")
        if switch.get_active():
            self.NO_DNS_CHANGE = False
        else:
            self.win_netsh_restore_dns()
            self.NO_DNS_CHANGE = True
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_network_switch_disableextifondisco(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_disableextifondisco = switch
            checkbox_title = Gtk.Label(label=_("Disable '%s' on Disconnect (default: OFF)")%(self.WIN_EXT_DEVICE))
            self.settings_network_switch_disableextifondisco_checkbox_title = checkbox_title
            if self.WIN_DISABLE_EXT_IF_ON_DISCO == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_network_switch_disableextifondisco)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_network_switch_disableextifondisco: failed, exception = '%s'"%(e))

    def cb_settings_network_switch_disableextifondisco(self,switch,gparam):
        self.debug(1,"def cb_settings_network_switch_disableextifondisco()")
        if switch.get_active():
            self.WIN_DISABLE_EXT_IF_ON_DISCO = True
            if self.state_openvpn() == False:
                self.win_disable_ext_interface()
        else:
            self.WIN_DISABLE_EXT_IF_ON_DISCO = False
            if self.state_openvpn() == False:
                self.win_enable_ext_interface()
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_firewall_switch_backuprestore(self, page):
        for file in self.FIREWALL_BACKUPS:
            button = Gtk.Button(label=("%s")%(file))
            button.connect('clicked', self.cb_restore_firewallbackup, file)
            page.pack_start(button,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)

    def settings_options_switch_updateovpnonstart(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_updateovpnonstart = switch
            checkbox_title = Gtk.Label(label=_("Update Configs on Start (default: OFF)"))
            if self.UPDATEOVPNONSTART == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_switch_updateovpnonstart)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_switch_updateovpnonstart: failed, exception = '%s'"%(e))

    def cb_switch_updateovpnonstart(self,switch,gparam):
        self.debug(1,"def cb_switch_updateovpnonstart()")
        if switch.get_active():
            self.UPDATEOVPNONSTART = True
        else:
            self.UPDATEOVPNONSTART = False
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_options_switch_autostart(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_autostart = switch
            checkbox_title = Gtk.Label(label=_("Client autostart (default: OFF)"))
            if self.VAR['CFG']['AUTOSTART'] == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_switch_autostart)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_switch_autostart: failed, exception = '%s'"%(e))

    def cb_switch_autostart(self,switch,gparam):
        self.debug(1,"def cb_switch_autostart()")
        if switch.get_active():
            self.VAR['CFG']['AUTOSTART'] = True
            schedule_task.set_task(self.DEBUG,self.VAR['CFG']['AS_DELAY_TIME'])
        else:
            self.VAR['CFG']['AUTOSTART'] = False
            schedule_task.delete_task(self.DEBUG)
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_options_combobox_time(self,page):
        try:
            self.debug(1,"def settings_options_combobox_time()")
            combobox_title = Gtk.Label(label=_("Delay in seconds"))
            combobox = Gtk.ComboBoxText.new()
            self.combobox_time = combobox
            for time in self.VAR['CFG']['AS_LIST_DELAY']:
                combobox.append_text("%s"%(time))
            if self.VAR['CFG']['AS_DELAY_TIME'] == 10:
                active_item = 0
            if self.VAR['CFG']['AS_DELAY_TIME'] == 20:
                active_item = 1
            if self.VAR['CFG']['AS_DELAY_TIME'] == 30:
                active_item = 2
            if self.VAR['CFG']['AS_DELAY_TIME'] == 40:
                active_item = 3
            if self.VAR['CFG']['AS_DELAY_TIME'] == 50:
                active_item = 4
            if self.VAR['CFG']['AS_DELAY_TIME'] == 60:
                active_item = 5
            combobox.set_active(active_item)
            combobox.connect('changed',self.cb_time_switcher_changed)
            page.pack_start(combobox_title,False,False,0)
            page.pack_start(combobox,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_combobox_time: failed, exception = '%s'"%(e))

    def cb_time_switcher_changed(self, combobox):
        self.debug(1,"def cb_time_switcher_changed()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.VAR['CFG']['AS_DELAY_TIME'] = combobox.get_active_text()
            self.write_options_file()
            self.UPDATE_SWITCH = True
            self.debug(1,"def cb_time_switcher_changed: selected Time = '%s'" % (self.VAR['CFG']['AS_DELAY_TIME']))
        return

    def settings_options_switch_accinfo(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_accinfo = switch
            checkbox_title = Gtk.Label(label=_("Account Info"))
            if self.LOAD_ACCDATA == True and not self.APIKEY == False:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_switch_accinfo)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_switch_accinfo: failed, exception = '%s'"%(e))

    def cb_switch_accinfo(self,switch,gparam):
        self.debug(1,"def cb_switch_accinfo()")
        if switch.get_active():
            if self.APIKEY == False:
                self.LOAD_ACCDATA = False
                self.request_LOAD_ACCDATA = True
                GLib.idle_add(self.dialog_apikey)
                return
            else:
                self.LOAD_ACCDATA = True
        else:
            self.LOAD_ACCDATA = False
        reopen = False
        if self.ACCWINDOW_OPEN == True:
            reopen = True
        if self.LOAD_ACCDATA == True:
            self.LOAD_ACCDATA = True
            self.LAST_OVPN_ACC_DATA_UPDATE = 0
            self.OVPN_ACC_DATA = {}
        self.write_options_file()
        if reopen == True:
            GLib.idle_add(self.call_redraw_accwindow)
        self.UPDATE_SWITCH = True

    def settings_options_switch_srvinfo(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_srvinfo = switch
            checkbox_title = Gtk.Label(label=_("Server Info"))
            if self.LOAD_SRVDATA == True and not self.APIKEY == False:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_switch_srvinfo)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_switch_srvinfo: failed, exception = '%s'"%(e))

    def cb_switch_srvinfo(self,switch,gparam):
        self.debug(1,"def cb_switch_srvinfo()")
        if switch.get_active():
            if self.APIKEY == False:
                self.LOAD_SRVDATA = False
                self.request_LOAD_SRVDATA = True
                GLib.idle_add(self.dialog_apikey)
                return
            else:
                self.LOAD_SRVDATA = True
        else:
            self.LOAD_SRVDATA = False
        if self.LOAD_SRVDATA == True:
            self.LAST_OVPN_SRV_DATA_UPDATE = 0
            self.VAR['OVPN']['SERVERDATA'] = {}
        self.write_options_file()
        self.rebuild_mainwindow()
        self.UPDATE_SWITCH = True

    def settings_options_switch_debugmode(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_debugmode = switch
            checkbox_title = Gtk.Label(label=_("Debug Mode (default: OFF)"))
            if self.DEBUG == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_switch_debugmode)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_switch_debugmode: failed, exception = '%s'"%(e))

    def cb_switch_debugmode(self,switch,gparam):
        self.debug(1,"def cb_switch_debugmode()")
        if switch.get_active():
            self.DEBUG = True
            self.debug(1,"DEBUG Logfile = '%s'"% (self.DEBUG_LOGFILE))
            self.show_debug_window()
        else:
            self.DEBUG = False
            self.show_debug_window()
            if os.path.isfile(self.DEBUG_LOGFILE):
                os.remove(self.DEBUG_LOGFILE)
        self.write_options_file()
        self.UPDATE_SWITCH = True

    def settings_options_button_networkadapter(self,page):
        button = Gtk.Button(label=_("Select Network Adapter"))
        self.button_switch_network_adapter = button
        button.connect('clicked', self.cb_settings_options_button_networkadapter)
        page.pack_start(button,False,False,0)
        page.pack_start(Gtk.Label(label=""),False,False,0)

    def cb_settings_options_button_networkadapter(self,event):
        GLib.idle_add(self.cb_resetextif)

    def settings_options_button_ipv6(self,page):
        if self.VAR['OVPN']['CFGTYPE'] == "23x":
            button_title = Gtk.Label(label=_("Current: IPv4 Entry Server with Exit to IPv4 (standard)"))
            button = Gtk.Button(label=_("Use IPv4 Entry Server with Exits to IPv4 + IPv6"))
            button.connect('clicked', self.cb_settings_options_button_ipv6)
        elif self.VAR['OVPN']['CFGTYPE']  == "23x46":
            button_title = Gtk.Label(label=_("Current: IPv4 Entry Server with Exits to IPv4 + IPv6"))
            button = Gtk.Button(label=_("Use IPv4 Entry Server with Exit to IPv4 (standard)"))
            button.connect('clicked', self.cb_settings_options_button_ipv6)
        self.button_ipmode = button
        self.button_title = button_title
        page.pack_start(button_title,False,False,0)
        page.pack_start(button,False,False,0)
        page.pack_start(Gtk.Label(label=""),False,False,0)

    def cb_settings_options_button_ipv6(self,event):
        if not self.VAR['OVPN']['CFGTYPE'] == "23x":
            GLib.idle_add(self.cb_change_ipmode1)
        if not self.VAR['OVPN']['CFGTYPE']  == "23x46":
            GLib.idle_add(self.cb_change_ipmode2)
        """
         *** fixme need isValueIPv6 first! ***
        if not self.VAR['OVPN']['CFGTYPE'] == "23x64":
            GLib.idle_add(self.cb_change_ipmode3)
        """

    def settings_options_combobox_theme(self,page):
        try:
            self.debug(1,"def settings_options_combobox_theme()")
            combobox_title = Gtk.Label(label=_("Change App Theme"))
            combobox = Gtk.ComboBoxText.new()
            item = 0
            THEME_DIR_CHECK = "%s\\share\\themes" % (self.BIN_DIR)
            if not os.path.isdir(THEME_DIR_CHECK):
                THEME_DIR_CHECK = "%s\\includes\\themes" % (DEV_DIR)
            for theme in self.INSTALLED_THEMES:
                THEME_DIR = "%s\\%s" % (THEME_DIR_CHECK, theme)
                if os.path.isdir(THEME_DIR):
                    combobox.append_text(theme)
                    if self.APP_THEME == theme:
                        combobox.set_active(item)
                    item = item + 1
            combobox.connect('changed',self.cb_theme_switcher_changed)
            page.pack_start(combobox_title,False,False,0)
            page.pack_start(combobox,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_combobox_theme: failed, exception = '%s'"%(e))

    def cb_theme_switcher_changed(self, combobox):
        self.debug(1,"def cb_theme_switcher_changed()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.APP_THEME = combobox.get_active_text()
            get_settings = Gtk.Settings.get_default()
            get_settings.set_property("gtk-theme-name", self.APP_THEME)
            self.write_options_file()
            self.UPDATE_SWITCH = True
            self.debug(1,"def cb_theme_switcher_changed: selected Theme = '%s'" % (self.APP_THEME))
        return

    def settings_options_combobox_icons(self,page):
        try:
            self.debug(1,"def settings_options_combobox_icons()")
            combobox_title = Gtk.Label(label=_("Change App Icons"))
            combobox = Gtk.ComboBoxText.new()
            self.combobox_icons = combobox
            item = 0
            for icons in self.INSTALLED_ICONS:
                combobox.append_text(icons)
                if self.ICONS_THEME == icons:
                    combobox.set_active(item)
                item = item + 1
            combobox.connect('changed',self.cb_icons_switcher_changed)
            page.pack_start(combobox_title,False,False,0)
            page.pack_start(combobox,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_combobox_icons: failed, exception = '%s'"%(e))

    def cb_icons_switcher_changed(self, combobox):
        self.debug(1,"def cb_icons_switcher_changed()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.VAR['CACHE']['icontheme'] = self.ICONS_THEME
            self.ICONS_THEME = combobox.get_active_text()
            if self.load_icons():
                self.write_options_file()
                self.debug(1,"def cb_icons_switcher_changed: selected Icons = '%s'" % (self.ICONS_THEME))
                self.ICON_CACHE_PIXBUF = {}
            else:
                self.debug(1,"def cb_icons_switcher_changed: failed icon theme = '%s', revert to '%s'" % (self.ICONS_THEME,self.VAR['CACHE']['icontheme']))
                self.ICONS_THEME = self.VAR['CACHE']['icontheme']
            self.UPDATE_SWITCH = True
        return

    def settings_options_combobox_fontsize(self,page):
        try:
            self.debug(1,"def settings_options_combobox_fontsize()")
            combobox_title = Gtk.Label(label=_("Change App Font Size"))
            combobox = Gtk.ComboBoxText.new()
            item = 0
            for size in self.APP_FONT_SIZE_AVAIABLE:
                combobox.append_text(size)
                if self.APP_FONT_SIZE == size:
                    combobox.set_active(item)
                item = item + 1
            combobox.connect('changed',self.cb_settings_options_combobox_fontsize)
            page.pack_start(combobox_title,False,False,0)
            page.pack_start(combobox,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_combobox_theme: failed, exception = '%s'"%(e))

    def cb_settings_options_combobox_fontsize(self, combobox):
        self.debug(1,"def cb_settings_options_combobox_fontsize()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.APP_FONT_SIZE = combobox.get_active_text()
            get_settings = Gtk.Settings.get_default()
            get_settings.set_property("gtk-font-name", self.APP_FONT_SIZE)
            self.write_options_file()
            self.UPDATE_SWITCH = True
            self.LANG_FONT_CHANGE = True
            self.debug(1,"def cb_settings_options_combobox_fontsize: selected Size = '%s'" % (self.APP_FONT_SIZE))
        return

    def settings_options_combobox_language(self,page):
        try:
            i=0; 
            self.debug(1,"def settings_options_combobox_theme()")
            combobox_title = Gtk.Label(label=_("Change App Language"))
            combobox = Gtk.ComboBoxText.new()
            item = 0
            LANGUAGE_DIR_CHECK = "%s\\locale" % (self.BIN_DIR)
            if not os.path.isdir(LANGUAGE_DIR_CHECK):
                LANGUAGE_DIR_CHECK = "%s\\locale" % (DEV_DIR)
            for lang in self.INSTALLED_LANGUAGES:
                if lang == "en":
                    combobox.append_text(lang)
                    if self.APP_LANGUAGE == lang:
                        combobox.set_active(item)
                    item = item + 1
                else:
                    LANGUAGE_DIR = "%s\\%s" % (LANGUAGE_DIR_CHECK, lang)
                    if os.path.isdir(LANGUAGE_DIR):
                        combobox.append_text(lang)
                        if self.APP_LANGUAGE == lang:
                            combobox.set_active(item)
                        item = item + 1
            combobox.connect('changed',self.cb_settings_options_combobox_language)
            page.pack_start(combobox_title,False,False,0)
            page.pack_start(combobox,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
            self.debug(1,"def settings_options_combobox_language()")
        except Exception as e:
            self.debug(1,"def settings_options_combobox_language: failed, exception = '%s'"%(e))

    def cb_settings_options_combobox_language(self, combobox):
        self.debug(1,"def cb_settings_options_combobox_language()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.APP_LANGUAGE = combobox.get_active_text()
            self.write_options_file()
            self.UPDATE_SWITCH = True
            self.LANG_FONT_CHANGE = True
            if self.init_localization(self.APP_LANGUAGE) == True:
                self.debug(1,"def cb_settings_options_combobox_language: selected lang = '%s'" % (self.APP_LANGUAGE))
        return

    def settings_options_switch_winnotify(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_winnotify = switch
            checkbox_title = Gtk.Label(label=_("Use Windows Notification System (default: ON)"))
            if self.WIN_ENABLE_NOTIFICATIONS == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_options_switch_winnotify)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_switch_winnotify: failed, exception = '%s'"%(e))

    def cb_settings_options_switch_winnotify(self,switch,gparam ):
        self.debug(1,"def cb_settings_options_switch_winnotify()")
        if switch.get_active():
            self.WIN_ENABLE_NOTIFICATIONS = True
        else:
            self.WIN_ENABLE_NOTIFICATIONS = False
        self.write_options_file()

    def settings_options_switch_disablequit(self,page):
        try:
            switch = Gtk.Switch()
            self.switch_disablequit = switch
            checkbox_title = Gtk.Label(label=_("Disable About and Quit on Connection (default: ON)"))
            if self.DISABLE_QUIT_ENTRY == True:
                switch.set_active(True)
            else:
                switch.set_active(False)
            switch.connect("notify::state", self.cb_settings_options_switch_disablequit)
            page.pack_start(checkbox_title,False,False,0)
            page.pack_start(switch,False,False,0)
            page.pack_start(Gtk.Label(label=""),False,False,0)
        except Exception as e:
            self.debug(1,"def settings_options_switch_disablequit: failed, exception = '%s'"%(e))

    def cb_settings_options_switch_disablequit(self,switch,gparam ):
        self.debug(1,"def cb_settings_options_switch_disablequit()")
        if switch.get_active():
            self.DISABLE_QUIT_ENTRY = True
        else:
            self.DISABLE_QUIT_ENTRY = False
        self.write_options_file()

    def settings_updates_button_clientupdate(self,page):
        button = Gtk.Button(label=_("Check Client Update"))
        button.connect('clicked', self.cb_settings_updates_button_clientupdate)
        page.pack_start(button,False,False,0)
        page.pack_start(Gtk.Label(label=""),False,False,0)

    def cb_settings_updates_button_clientupdate(self,event):
        diff = int((time.time()-self.LAST_CHECK_CFG_UPDATE))
        if self.timer_check_certdl_running == False and diff > 30:
            self.LAST_CHECK_CFG_UPDATE = time.time()
            self.cb_check_client_update()
        else:
            self.msgwarn(_("Retry in few seconds..."),_("Please wait..."))

    def settings_updates_button_normalconf(self,page):
        button = Gtk.Button(label=_("Normal Config Update"))
        button.connect('clicked', self.cb_settings_updates_button_normalconf)
        page.pack_start(button,False,False,0)
        page.pack_start(Gtk.Label(label=""),False,False,0)

    def cb_settings_updates_button_normalconf(self,event):
        diff = int((time.time()-self.LAST_CHECK_CFG_UPDATE))
        if self.timer_check_certdl_running == False and diff > 30:
            self.LAST_CHECK_CFG_UPDATE = time.time()
            self.cb_check_normal_update()
        else:
            self.msgwarn(_("Retry in few seconds..."),_("Please wait..."))

    def settings_updates_button_forceconf(self,page):
        button = Gtk.Button(label=_("Forced Config Update"))
        button.connect('clicked', self.cb_settings_updates_button_forceconf)
        page.pack_start(button,False,False,0)
        page.pack_start(Gtk.Label(label=""),False,False,0)

    def cb_settings_updates_button_forceconf(self,event):
        diff1 = int((time.time()-self.LAST_CHECK_CFG_UPDATE_FORCE))
        diff2 = int((time.time()-self.LAST_CHECK_CFG_UPDATE))
        if self.timer_check_certdl_running == False and diff1 > 60 and diff2 > 15:
            self.LAST_CHECK_CFG_UPDATE_FORCE = time.time()
            self.cb_force_update()
        else:
            self.msgwarn(_("Retry in few seconds..."),_("Please wait..."))

    def settings_updates_button_apireset(self,page):
        button = Gtk.Button(label=_("Reset API-Login"))
        button.connect('clicked', self.cb_settings_updates_button_apireset)
        page.pack_start(button,False,False,0)
        page.pack_start(Gtk.Label(label=""),False,False,0)

    def cb_settings_updates_button_apireset(self,event):
        diff = int((time.time()-self.LAST_HIT_UPDATE_BUTTON5))
        if diff > 15:
            self.LAST_HIT_UPDATE_BUTTON5 = int(time.time())
            GLib.idle_add(self.dialog_apikey)
        else:
            self.msgwarn(_("Retry in few seconds..."),_("Please wait..."))

    def destroy_settingswindow(self):
        self.debug(1,"def destroy_settingswindow()")
        GLib.idle_add(self.settingswindow.destroy)
        self.SETTINGSWINDOW_OPEN = False
        self.debug(1,"def destroy_settingswindow")

    def cb_destroy_settingswindow(self,event):
        self.debug(1,"def cb_destroy_settingswindow")
        self.SETTINGSWINDOW_OPEN = False

    def cb_destroy_mainwindow(self,event):
        self.debug(1,"def cb_destroy_mainwindow")
        self.VAR['MAIN']['OPEN'] = False
        self.VAR['MAIN']['HIDE'] = False

    def cb_destroy_debugwindow(self,event):
        self.DEBUGWINDOW_OPEN = False
        GLib.idle_add(self.debug_window.destroy)

    def cb_destroy_hidecellswindow(self,event):
        self.debug(1,"def cb_destroy_hidecellswindow")
        self.HIDECELLSWINDOW_OPEN = False

    def cb_destroy_accwindow(self,event):
        self.debug(1,"def cb_destroy_accwindow")
        self.ACCWINDOW_OPEN = False

    def cb_del_dns(self,widget,event,data):
        if event.button == 1:
            self.debug(1,"def cb_del_dns()")
            self.destroy_context_menu_servertab()
            print("def cb_del_dns: cbdata = '%s'" % (data))
            for name,value in data.items():
                try:
                    if value["primary"]["ip4"] == self.MYDNS[name]["primary"]["ip4"]:
                        try:
                            if self.isValueIPv4(self.MYDNS[name]["secondary"]["ip4"]):
                                self.MYDNS[name]["primary"] = self.MYDNS[name]["secondary"]
                                self.MYDNS[name]["secondary"] = {}
                        except Exception as e:
                            self.MYDNS[name]["primary"] = {}
                except Exception as e:
                    pass
                
                try:
                    if value["secondary"]["ip4"] == self.MYDNS[name]["secondary"]["ip4"]:
                        self.MYDNS[name]["secondary"] = {}
                except Exception as e:
                    pass
            self.write_options_file()
            if self.VAR['OVPN']['CONN']['SERVER'] == name:
                self.debug(1,"def cb_set_dns: self.VAR['OVPN']['CONN']['SERVER'] = %s , name = %s" % (self.VAR['OVPN']['CONN']['SERVER'],name))
                self.win_netsh_set_dns_ovpn()
            return True

    def cb_set_dns(self,widget,event,data):
        if event.button == 1:
            self.debug(1,"def cb_set_dns()")
            self.destroy_context_menu_servertab()
            for name,value in data.items():
                self.debug(1,"def cb_set_dns: name '%s' value: '%s'" % (name,value))
                try:
                    newpridns = value["primary"]["ip4"]
                    if self.isValueIPv4(newpridns):
                        print(" set primary dns")
                        try:
                            print('try: if newpridns == self.MYDNS[name]["secondary"]["ip4"]')
                            if newpridns == self.MYDNS[name]["secondary"]["ip4"]:
                                self.MYDNS[name]["secondary"] = {}
                                self.debug('self.MYDNS[name]["secondary"] = {}')
                        except Exception as e:
                            #print "except1a"
                            pass
                except Exception as e:
                    #print "except1b"
                    pass
                
                try:
                    newsecdns = value["secondary"]["ip4"]
                    if self.isValueIPv4(newsecdns):
                        print( " set secondary dns")
                        try:
                            print('try: if newsecdns == self.MYDNS[name]["primary"]["ip4"]')
                            if newsecdns == self.MYDNS[name]["primary"]["ip4"]:
                                return False
                        except Exception as e:
                            #print "except2a"
                            pass
                except Exception as e:
                    #print "except2b"
                    pass
                
                try:
                    self.MYDNS[name].update(value)
                except Exception as e:
                    self.MYDNS[name] = value
                self.write_options_file()
                if self.VAR['OVPN']['CONN']['SERVER'] == name:
                    self.debug(1,"def cb_set_dns: self.VAR['OVPN']['CONN']['SERVER'] = %s , name = %s" % (self.VAR['OVPN']['CONN']['SERVER'],name))
                    self.win_netsh_set_dns_ovpn()
                    return True

    def destroy_context_menu_servertab(self):
        self.debug(1,"def destroy_context_menu_servertab()")
        try:
            self.context_menu_servertab.hide()
            self.debug(1,"def destroy_context_menu_servertab: 0x0003")
        except Exception as e:
            pass

    def destroy_systray_menu(self):
        self.debug(2,"def destroy_systray_menu()")
        try:
            GLib.idle_add(self.systray_menu.destroy)
            self.systray_menu = False
            self.MOUSE_IN_TRAY = 0
            self.debug(2,"def destroy_systray_menu: true")
        except Exception as e:
            self.debug(7,"def destroy_systray_menu: failed, exception = '%s'"%(e))
            self.systray_menu = False

    def set_statusbar_text(self,text):
        self.debug(9,"def set_statusbar_text()")
        try:
            if not self.statusbar_text == False:
                GLib.idle_add(self.statusbar_text.set_label,text)
        except Exception as e:
            self.debug(1,"def set_statusbar_text: text = '%s' failed" % (text))

    def cb_set_ovpn_favorite_server(self,widget,event,server):
        if event.button == 1:
            self.destroy_context_menu_servertab()
            self.debug(1,"def cb_set_ovpn_favorite_server()")
            try:
                self.VAR['OVPN']['FAVSRV'] = server
                self.write_options_file()
                self.call_redraw_mainwindow()
                return True
            except Exception as e:
                self.debug(1,"def cb_set_ovpn_favorite_server: failed, exception = '%s'"%(e))

    def cb_del_ovpn_favorite_server(self,widget,event,server):
        if event.button == 1:
            self.destroy_context_menu_servertab()
            self.debug(1,"def cb_del_ovpn_favorite_server()")
            try:
                self.VAR['OVPN']['FAVSRV'] = False
                self.write_options_file()
                self.call_redraw_mainwindow()
                return True
            except Exception as e:
                self.debug(1,"def cb_del_ovpn_favorite_server: failed, exception = '%s'"%(e))

    def cb_reset_load_remote_timer(self,widget,event):
        if event.keyval == Gdk.KEY_F5:
            self.call_redraw_mainwindow()
            self.debug(1,"def cb_reset_load_remote_timer == F5")
            self.reset_load_remote_timer()

    def reset_load_remote_timer(self):
        if self.LOAD_SRVDATA == True and self.VAR['MAIN']['OPEN'] == True:
            if self.LAST_OVPN_SRV_DATA_UPDATE > 0 and self.LAST_OVPN_SRV_DATA_UPDATE < time.time()-60:
                self.LAST_OVPN_SRV_DATA_UPDATE = 0
                self.debug(1,"reset_load_remote_timer: SRV")
        if self.LOAD_ACCDATA == True and self.ACCWINDOW_OPEN == True:
            if self.LAST_OVPN_ACC_DATA_UPDATE > 0 and self.LAST_OVPN_ACC_DATA_UPDATE < time.time()-60:
                self.LAST_OVPN_ACC_DATA_UPDATE = 0
                self.debug(1,"reset_load_remote_timer: ACC")

    def cb_redraw_mainwindow_vbox(self,widget,event):
        if event.button == 1:
            self.debug(1,"def cb_redraw_mainwindow_vbox()")
            self.destroy_context_menu_servertab()
            self.reset_load_remote_timer()

    def cb_kill_openvpn(self,widget,event):
        if event.button == 1:
            self.VAR['OVPN']['STOP'] = True
            self.destroy_context_menu_servertab()
            self.destroy_systray_menu()
            self.debug(1,"def cb_kill_openvpn()")
            self.VAR['OVPN']['AUTOCONNECT'] = False
            self.debug(1,"def cb_kill_openvpn")
            killthread = threading.Thread(target=self.inThread_kill_openvpn)
            killthread.daemon = True
            killthread.start()

    def inThread_kill_openvpn(self):
        self.debug(1,"def inThread_kill_openvpn()")
        self.kill_openvpn()

    def cb_jump_openvpn(self,widget,event,server):
        if self.inThread_jump_server_running == True:
            self.debug(1,"def cb_jump_openvpn: inThread_jump_server() running ! return False")
            return False
        if (widget == 0 and event == 0) or event.button == 1:
            self.VAR['OVPN']['STOP'] = True
            self.VAR['OVPN']['CALL_SRV'] = server
            self.destroy_systray_menu()
            self.destroy_context_menu_servertab()
            jumpthread = threading.Thread(target=lambda server=server: self.inThread_jump_server(server))
            jumpthread.daemon = True
            jumpthread.start()
            self.debug(1,"def cb_jump_openvpn: %s" % (server))

    def inThread_jump_server(self,server):
        self.debug(1,"def inThread_jump_server()")
        if self.inThread_jump_server_running == True:
            self.debug(1,"def inThread_jump_server: running ! return")
            return False
        else:
            self.inThread_jump_server_running = True
            self.UPDATE_SWITCH = True
            self.debug(1,"def inThread_jump_server: server %s" % (server))
            if self.state_openvpn() == True:
                self.kill_openvpn()
            while not self.VAR['OVPN']['THREADID'] == False:
                self.debug(1,"def cb_jump_openvpn: sleep while self.VAR['OVPN']['THREADID']")
                time.sleep(0.1)
            while not self.timer_ovpn_ping_running == False:
                self.debug(1,"def cb_jump_openvpn: sleep while self.timer_ovpn_ping_running")
                time.sleep(0.5)
            self.inThread_jump_server_running = True
            self.call_openvpn(server)
            self.debug(1,"def inThread_jump_server: exit")

    def kill_openvpn(self):
        self.debug(1,"def kill_openvpn()")
        try:
            if self.state_openvpn() == False:
                return False
            try:
                self.del_ovpn_routes()
            except Exception as e:
                self.debug(1,"def kill_openvpn: self.del_ovpn_routes() failed, exception '%s'"%(e))
            if os.path.isfile(self.WIN_TASKKILL_EXE):
                ovpn_exe = self.OPENVPN_EXE.split("\\")[-1]
                cmdstring = '%s /F /IM %s' % (self.WIN_TASKKILL_EXE,ovpn_exe)
                exitcode = subprocess.check_call(cmdstring,shell=True)
                self.debug(1,"def kill_openvpn: exitcode = %s" % (exitcode))
        except Exception as e:
            self.debug(1,"def kill_openvpn: failed, exception '%s'"%(e))
            self.reset_ovpn_values()

    def call_openvpn(self,server):
        self.debug(1,"def call_openvpn()")
        try:
            thread_openvpn = threading.Thread(target=lambda server=server: self.openvpn(server))
            thread_openvpn.start()
            self.debug(1,"def call_openvpn: thread_openvpn.start()")
        except Exception as e:
            self.debug(1,"def call_openvpn: thread self.openvpn(server) failed, exception = '%s'"%(e))
            return False
        return True

    def state_openvpn(self):
        if self.STATE_OVPN == False and self.inThread_jump_server_running == False:
            return False
        if self.STATE_OVPN == True or self.inThread_jump_server_running == True:
            return True

    def openvpn(self,server):
        self.debug(1,"def openvpn: server = '%s'" % (server))
        try:
            if self.VAR['OVPN']['THREADID'] == False:
                self.inThread_jump_server_running = True
                OVPN_CONFIG_FILE = "%s\\%s.ovpn" % (self.VPN_CFG,server)
                servershort = server.split(".")[0].upper()
                if os.path.isfile(OVPN_CONFIG_FILE):
                    self.VAR['OVPN']['CONN']['IP'] = self.VAR['OVPN']['CONFIGDATA'][servershort][0]
                    self.VAR['OVPN']['CONN']['PORT'] = self.VAR['OVPN']['CONFIGDATA'][servershort][1]
                    self.VAR['OVPN']['CONN']['PROTO'] = self.VAR['OVPN']['CONFIGDATA'][servershort][2]
                else:
                    self.debug(1,"Error: Server Config not found: '%s'" % (OVPN_CONFIG_FILE))
                    self.reset_ovpn_values()
                    return False
                self.VAR['OVPN']['LOGFILE'] = "%s\\openvpn.log" % (self.VPN_DIR)
                try:
                    OVPN_STRING = '"%s" --config "%s" --dev-node "%s"' % (self.OPENVPN_EXE,OVPN_CONFIG_FILE,self.WIN_TAP_DEVICE)
                    if self.DEBUG == True:
                        self.OVPN_STRING = '%s --log "%s"' % (OVPN_STRING,self.VAR['OVPN']['LOGFILE'])
                    else:
                        self.OVPN_STRING = OVPN_STRING
                    thread_spawn_openvpn_process = threading.Thread(target=self.inThread_spawn_openvpn_process)
                    thread_spawn_openvpn_process.start()
                    self.VAR['OVPN']['THREADID'] = threading.currentThread()
                    self.debug(1,"def openvpn: server '%s', threadid '%s'" % (server,self.VAR['OVPN']['THREADID']))
                except Exception as e:
                    self.debug(1,"def openvpn: start thread failed, exception '%s'" % (server,e))
                    self.reset_ovpn_values()
                    return False
            else:
                self.debug(1,"def openvpn: self.VAR['OVPN']['THREADID'] = %s" % (self.VAR['OVPN']['THREADID']))
        except Exception as e:
            self.debug(1,"def openvpn: failed, exception = '%s'"%(e))

    def inThread_spawn_openvpn_process(self):
        try:
            self.debug(1,"def inThread_spawn_openvpn_process")
            
            # *fixme* def win_select_networkadapter() fails if anybody changes interface name between start and connect
            #if not self.win_read_interfaces():
            #   self.reset_ovpn_values()
            #   return False
            if not openvpn.check_files(self.DEBUG,self.OPENVPN_DIR) == True:
                return self.reset_ovpn_values()
            if not self.win_firewall_start():
                self.msgwarn(_("Could not start Windows Firewall!"),_("Error"))
                return self.reset_ovpn_values()
            self.win_firewall_clear_vcp_rules()
            self.win_firewall_modify_rule(option="add")
            self.win_clear_ipv6()
            self.VAR['OVPN']['CONN']['START'] = int(time.time())
            self.VAR['OVPN']['CONN']['SERVER'] = self.VAR['OVPN']['CALL_SRV']
            self.VAR['OVPN']['PING_STAT'] = -1
            self.VAR['OVPN']['PING_LAST'] = -1
            self.NEXT_PING_EXEC = 0
            self.reset_load_remote_timer()
            if self.TAP_BLOCKOUTBOUND == True:
                self.win_firewall_tap_blockoutbound()
            self.win_netsh_set_dns_ovpn()
            self.win_enable_ext_interface()
            self.STATE_OVPN = True
            self.inThread_jump_server_running = False
            if self.timer_ovpn_ping_running == False:
                self.debug(1,"def inThread_spawn_openvpn_process: self.inThread_timer_ovpn_ping")
                pingthread = threading.Thread(target=self.inThread_timer_ovpn_ping)
                pingthread.daemon = True
                pingthread.start()
            self.call_redraw_mainwindow()
            self.debug(1,"def inThread_spawn_openvpn_process: start")
            self.debug(2,"def inThread_spawn_openvpn_process: self.OVPN_STRING = '%s'"%(self.OVPN_STRING))
            """ launch openvpn in loop """
            while True:
                exitcode = False
                try:
                    exitcode = subprocess.check_call(self.OVPN_STRING,shell=True)
                except Exception as e:
                    if self.VAR['OVPN']['STOP'] == False:
                        time.sleep(0.1)
                        if not openvpn.check_files(self.DEBUG,self.OPENVPN_DIR) == True:
                            return self.reset_ovpn_values()
                        else:
                            self.debug(1,"def inThread_spawn_openvpn_process: subprocess.check_call failed, exception: '%s'"%(e))
                            self.VAR['OVPN']['CONN']['START'] = int(time.time())
                            self.VAR['OVPN']['PING_DEAD'] = 9
                            self.VAR['OVPN']['PING_LAST'] = -2
                            self.NEXT_PING_EXEC = 9
                            self.msgwarn(_("OpenVPN process crashed! Restarting..."),_("Error"))
                            """ no return loops daemon """
                    else:
                        break
            """ exited openvpn """
            self.win_disable_ext_interface()
            self.win_netsh_restore_dns()
            self.debug(1,"def inThread_spawn_openvpn_process: exitcode = '%s'"%(exitcode))
            return self.reset_ovpn_values()
        except Exception as e:
            self.reset_ovpn_values()
            self.debug(1,"def inThread_spawn_openvpn_process(): failed, exception: '%s'"%(e))

    def reset_ovpn_values(self):
        try:
            self.debug(1,"def reset_ovpn_values()")
            self.win_firewall_modify_rule(option="delete")
            self.win_clear_ipv6()
            self.VAR['OVPN']['STOP'] = False
            self.STATE_OVPN = False
            self.inThread_jump_server_running = False
            self.VAR['OVPN']['CONN']['SERVER'] = False
            self.VAR['OVPN']['CONN']['IP'] = False
            self.VAR['OVPN']['CONN']['START'] = 0
            self.VAR['OVPN']['CONN']['SECONDS'] = 0
            self.VAR['OVPN']['THREADID'] = False
            self.VAR['OVPN']['PING_STAT'] = 0
            self.VAR['OVPN']['PING_LAST'] = 0
            self.VAR['OVPN']['PINGS'] = list()
            self.UPDATE_SWITCH = True
            self.OVPN_STRING = False
            self.VAR['OVPN']['CONN']['OK'] = False
            self.LAST_OVPN_PING_DEAD_MESSAGE = 0
            self.delete_file(self.VAR['OVPN']['LOGFILE'],"def reset_ovpn_values")
            self.call_redraw_mainwindow()
            return False
        except Exception as e:
            self.debug(1,"def reset_ovpn_values: failed, exception: '%s'"%(e))

    def inThread_timer_ovpn_ping(self):
        self.debug(10,"def inThread_timer_ovpn_ping()")
        if self.timer_ovpn_ping_running == False:
            self.VAR['OVPN']['PING_STAT'] = -2
            self.timer_ovpn_ping_running = True
            self.debug(1,"def inThread_timer_ovpn_ping: start")
        
        if self.state_openvpn() == False:
            self.VAR['OVPN']['PING_STAT'] = -1
            self.VAR['OVPN']['PINGS'] = list()
            self.timer_ovpn_ping_running = False
            self.debug(1,"def inThread_timer_ovpn_ping: leaving")
            return
        
        elif self.STATE_OVPN == True:
            try:
                try:
                    if not self.win_check_dns() == True:
                        self.debug(1,"def inThread_timer_ovpn_ping: dns changed")
                        if self.win_netsh_set_dns_ovpn() == True:
                            if self.LAST_MSGWARN_WINDOW_DNS < int(time.time())-30:
                                self.LAST_MSGWARN_WINDOW_DNS = int(time.time())
                                self.msgwarn(_("DNS changed but reset ok!"),_("Success"))
                        else:
                            if self.LAST_MSGWARN_WINDOW_DNS < int(time.time())-30:
                                self.LAST_MSGWARN_WINDOW_DNS = int(time.time())
                                self.msgwarn(_("DNS changed and reseting failed!"),_("Error"))
                    if self.NEXT_PING_EXEC < int(time.time()) and self.VAR['OVPN']['CONN']['SECONDS'] > 5:
                        PING = self.get_ovpn_ping()
                        if PING > 0 and PING < 1:
                            PING = round(PING,3)
                        elif PING > 1:
                            PING = int(round(PING,0))
                        if PING > 0 and self.check_myip() == True:
                            randint = random.randint(10,20)
                            self.NEXT_PING_EXEC = int(time.time())+randint
                            pingsum = 0
                            if PING > 0:
                                self.VAR['OVPN']['PINGS'].append(PING)
                            if len(self.VAR['OVPN']['PINGS']) > 16:
                                self.VAR['OVPN']['PINGS'].pop(0)
                            if len(self.VAR['OVPN']['PINGS']) > 0:
                                for pingi in self.VAR['OVPN']['PINGS']:
                                    pingsum += int(pingi)
                                self.VAR['OVPN']['PING_STAT'] = pingsum/len(self.VAR['OVPN']['PINGS'])
                            self.VAR['OVPN']['PING_LAST'] = PING
                            self.VAR['OVPN']['PING_DEAD'] = 0
                            self.debug(7,"def inThread_timer_ovpn_ping: %s ms, next in %s s"%(PING,randint))
                        #else:
                        #   self.set_ovpn_ping_dead()
                except Exception as e:
                    self.set_ovpn_ping_dead()
            except Exception as e:
                self.set_ovpn_ping_dead()
                self.debug(1,"def inThread_timer_ovpn_ping: failed, exception = '%s'"%(e))
            time.sleep(0.5)
            try:
                pingthread = threading.Thread(target=self.inThread_timer_ovpn_ping)
                pingthread.daemon = True
                pingthread.start()
                return True
            except Exception as e:
                self.debug(1,"rejoin def inThread_timer_ovpn_ping() failed, exception = '%s'"%(e))

    def set_ovpn_ping_dead(self):
        self.VAR['OVPN']['PING_LAST'] = -2
        self.NEXT_PING_EXEC = int(time.time())+5
        self.VAR['OVPN']['CONN']['OK'] = False
        self.VAR['OVPN']['PING_DEAD'] += 1
        if self.VAR['OVPN']['CONN']['FAILEDTIME'] == 0:
            self.VAR['OVPN']['CONN']['FAILEDTIME'] = int(time.time())

    def get_ovpn_ping(self):
        self.debug(2,"def get_ovpn_ping()")
        try:
            ports = [ 53, 5353, 443, 1080, 8080 ]
            for port in ports:
                self.debug(2,"def get_ovpn_ping: try port %s"%(port))
                PING = self.try_socket(self.VAR['OVPN']['GW']['IP4A'],port,1)
                if not PING == False:
                    return PING
            self.set_ovpn_ping_dead()
            return self.VAR['OVPN']['PING_LAST']
        except Exception as e:
            self.debug(2,"def get_ovpn_ping: failed, exception = '%s'"%(e))

    def read_gateway_from_interface(self):
        if DEVMODE == True:
            return self.read_gateway_from_interface_devmode()
        
        try:
            GATEWAY_LOCAL = False
            DEVICE_GUID = winregs.get_networkadapter_guid(self.DEBUG,self.WIN_EXT_DEVICE,self.STATE_OVPN)
            DEVICE_DATA = winregs.get_interface_infos_from_guid(self.DEBUG,DEVICE_GUID,self.STATE_OVPN)
            try:
                GATEWAY_LOCAL = DEVICE_DATA["DefaultGateway"][0]
            except Exception as e:
                self.debug(1,"def read_gateway_from_interface: read DefaultGateway failed, try dhcp")
                try:
                    GATEWAY_LOCAL = DEVICE_DATA["DhcpServer"]
                except Exception as e:
                    self.debug(1,"def read_gateway_from_interface: try DhcpServer failed, exception = '%s'"%(e))
            self.debug(1,"def read_gateway_from_interface: GATEWAY_LOCAL = '%s'" % (GATEWAY_LOCAL))
            if not GATEWAY_LOCAL == False:
                if self.isValueIPv4(GATEWAY_LOCAL):
                    self.GATEWAY_LOCAL = GATEWAY_LOCAL
                    self.debug(1,"def read_gateway_from_interface: self.GATEWAY_LOCAL = '%s'" % (self.GATEWAY_LOCAL))
                    return True
        except Exception as e:
            self.debug(1,"def read_gateway_from_interface: failed, exception = '%s'"%(e))

    def read_gateway_from_interface_devmode(self):
        try:
            GATEWAY_LOCAL = False
            DEVICE_GUID = winregs.get_networkadapter_guid(self.DEBUG,self.WIN_EXT_DEVICE,self.STATE_OVPN)
            DEVICE_DATA = winregs.get_interface_infos_from_guid(self.DEBUG,DEVICE_GUID,self.STATE_OVPN)
            try:
                """ *fixme* """
                GATEWAY_LOCAL = DEVICE_DATA["DefaultGateway"][0]
                if GATEWAY_LOCAL == "255.255.255.255":
                    GATEWAY_LOCAL = False
            except Exception as e:
                GATEWAY_LOCAL = False
            if GATEWAY_LOCAL == False:
                self.debug(1,"def read_gateway_from_interface: read DefaultGateway failed, try dhcp")
                try:
                    GATEWAY_LOCAL = DEVICE_DATA["DhcpServer"]
                except Exception as e:
                    self.debug(1,"def read_gateway_from_interface: try DhcpServer failed, exception = '%s'"%(e))
            
            if not GATEWAY_LOCAL == False and not GATEWAY_LOCAL == "255.255.255.255":
                self.debug(1,"def read_gateway_from_interface: GATEWAY_LOCAL = '%s'" % (GATEWAY_LOCAL))
                if self.isValueIPv4(GATEWAY_LOCAL):
                    self.GATEWAY_LOCAL = GATEWAY_LOCAL
                    self.debug(1,"def read_gateway_from_interface: self.GATEWAY_LOCAL = '%s'" % (self.GATEWAY_LOCAL))
                    return True
                else:
                    self.debug(1,"def read_gateway_from_interface: GATEWAY_LOCAL not ipv4 = '%s'" % (GATEWAY_LOCAL))
        except Exception as e:
            self.debug(1,"def read_gateway_from_interface: failed, exception = '%s'"%(e))

    def del_ovpn_routes(self):
        self.debug(1,"def del_ovpn_routes()")
        try:
            if not self.GATEWAY_LOCAL == False:
                ROUTE_CMDLIST = list()
                ROUTE_CMDLIST.append("DELETE %s MASK 255.255.255.255 %s" % (self.VAR['OVPN']['CONN']['IP'],self.GATEWAY_LOCAL))
                ROUTE_CMDLIST.append("DELETE 0.0.0.0 MASK 128.0.0.0 %s" % (self.VAR['OVPN']['GW']['IP4']))
                ROUTE_CMDLIST.append("DELETE 128.0.0.0 MASK 128.0.0.0 %s" % (self.VAR['OVPN']['GW']['IP4']))
                return self.win_join_route_cmd(ROUTE_CMDLIST)
        except Exception as e:
            self.debug(1,"def del_ovpn_routes: failed, exception = '%s'"%(e))

    def win_clear_ipv6(self):
        self.debug(1,"def win_clear_ipv6()")
        self.win_clear_ipv6_dns()
        self.win_clear_ipv6_addr()
        self.win_clear_ipv6_routes()

    def win_clear_ipv6_dns(self):
        self.debug(1,"def win_clear_ipv6_dns()")
        try:
            NETSH_CMDLIST = list()
            netshcmd = 'interface ipv6 show dnsservers "%s"' % (self.WIN_TAP_DEVICE)
            output = self.win_return_netsh_cmd(netshcmd)
            if not output == False:
                for line in output:
                    #print line
                    if " fd48:8bea:68a5:" in line:
                        #print line
                        ipv6addr = line.split("    ")[2]
                        #print ipv6addr
                        if ipv6addr.startswith("fd48:8bea:68a5:"):
                            cmdstring = 'interface ipv6 delete dnsservers "%s" "%s"' % (self.WIN_TAP_DEVICE,ipv6addr)
                            NETSH_CMDLIST.append(netshcmd)
            if len(NETSH_CMDLIST) > 0:
                self.win_join_netsh_cmd(NETSH_CMDLIST)
        except Exception as e:
            self.debug(1,"def win_clear_ipv6_dns: failed, exception = '%s'"%(e))

    def win_clear_ipv6_addr(self):
        self.debug(1,"def win_clear_ipv6_addr()")
        try:
            NETSH_CMDLIST = list()
            netshcmd = 'interface ipv6 show addresses "%s"' % (self.WIN_TAP_DEVICE)
            output = self.win_return_netsh_cmd(netshcmd)
            if not output == False:
                try:
                    for line in output:
                        if " fd48:8bea:68a5:" in line or " fe80:" in line:
                            self.debug(1,"def win_clear_ipv6_addr: found: line = '%s'" % (line))
                            if not "%" in line:
                                ipv6addr = line.split()[1]
                                netshcmd = 'interface ipv6 delete address address="%s" interface="%s" store=active' % (ipv6addr,self.WIN_TAP_DEVICE)
                                NETSH_CMDLIST.append(netshcmd)
                    if len(NETSH_CMDLIST) > 0:
                        self.win_join_netsh_cmd(NETSH_CMDLIST)
                except Exception as e:
                    self.debug(1,"def win_clear_ipv6_addr: failed #2, exception = '%s'"%(e))
        except Exception as e:
            self.debug(1,"def win_clear_ipv6_addr: failed, exception = '%s'"%(e))

    def win_clear_ipv6_routes(self):
        self.debug(1,"def win_clear_ipv6_routes()")
        try:
            netshcmd = 'interface ipv6 show route'
            output = self.win_return_netsh_cmd(netshcmd)
            if not output == False:
                for line in output:
                    if " fd48:8bea:68a5:" in line or " fe80:" in line:
                        self.debug(1,"def win_clear_ipv6_routes: found: line = '%s'" % (line))
                        ipv6 = line.split()[3]
                        output = self.win_return_route_cmd("DELETE %s" % (ipv6))
                        self.debug(1,"def win_clear_ipv6_routes: %s %s" % (ipv6,output))
        except Exception as e:
            self.debug(1,"def win_clear_ipv6_routes: failed, exception = '%s'"%(e))

    def win_netsh_set_dns_ovpn(self,domaindns=False):
        self.debug(2,"def win_netsh_set_dns_ovpn()")
        if self.NO_DNS_CHANGE == True:
            return True
        if self.check_dns_is_whitelisted() == True:
            return True
        try:
            DNSS = self.select_dns(domaindns)
            NETSH_CMDLIST = list()
            if len(DNSS) == 1:
                NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_EXT_DEVICE,DNSS[0]))
                if self.state_openvpn() == True:
                    NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_TAP_DEVICE,DNSS[0]))
            if len(DNSS) == 2:
                NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_EXT_DEVICE,DNSS[0]))
                NETSH_CMDLIST.append('interface ip add dnsservers "%s" %s index=2 no' % (self.WIN_EXT_DEVICE,DNSS[1]))
                if self.state_openvpn() == True:
                    NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_TAP_DEVICE,DNSS[0]))
                    NETSH_CMDLIST.append('interface ip add dnsservers "%s" %s index=2 no' % (self.WIN_TAP_DEVICE,DNSS[1]))
            if self.win_join_netsh_cmd(NETSH_CMDLIST) == True:
                self.WIN_DNS_CHANGED = True
                self.debug(1,"def win_netsh_set_dns_ovpn: True")
                return True
            else:
                self.debug(1,"def win_netsh_set_dns_ovpn: False")
        except Exception as e:
            self.debug(1,"def win_netsh_set_dns_ovpn: failed, exception = '%s'"%(e))

    def win_netsh_restore_dns(self):
        self.debug(1,"def win_netsh_restore_dns()")
        try:
            if self.NO_DNS_CHANGE == True:
                return True
            if self.WIN_DNS_CHANGED == False:
                return True
            if self.check_dns_is_whitelisted() == True:
                return True
            NETSH_CMDLIST = list()
            try:
                
                if self.WIN_EXT_DHCP_DNS == True:
                    NETSH_CMDLIST.append('interface ip set dnsservers "%s" dhcp' % (self.WIN_EXT_DEVICE))
                    if self.win_join_netsh_cmd(NETSH_CMDLIST):
                        self.debug(1,"DNS restored to DHCP.")
                        return True
                    else:
                        return False
            except Exception as e:
                self.debug(1,"def win_netsh_restore_dns: restore DHCP on IF: '%s' failed " % (self.WIN_EXT_DEVICE))
            
            try:
                if not self.GATEWAY_DNS1 == self.VAR['OVPN']['GW']['IP4A']:
                    NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no'%(self.WIN_EXT_DEVICE,self.GATEWAY_DNS1))
                    if not self.GATEWAY_DNS2 == False:
                        NETSH_CMDLIST.append('interface ip add dnsservers "%s" %s index=2 no'%(self.WIN_EXT_DEVICE,self.GATEWAY_DNS2))
                    if self.win_join_netsh_cmd(NETSH_CMDLIST):
                        self.debug(1,"def win_netsh_restore_dns: restored to Primary = '%s', Secondary = '%s'" % (self.GATEWAY_DNS1,self.GATEWAY_DNS2))
                        return True
                else:
                    NETSH_CMDLIST.append('interface ip set dnsservers "%s" dhcp' % (self.WIN_EXT_DEVICE))
                    if self.win_join_netsh_cmd(NETSH_CMDLIST):
                        self.debug(1,"def win_netsh_restore_dns: restored to DHCP")
                        return True
                    else:
                        return False
            except Exception as e:
                self.debug(1,"def win_netsh_restore_dns: restore failed, exception = '%s'"%(e))
        except Exception as e:
            self.debug(1,"def win_netsh_restore_dns: failed, exception = '%s'"%(e))

    def win_read_dns_from_interface(self,adaptername):
        if self.STATE_OVPN == False:
            self.debug(1,"def win_read_dns_from_interface(adaptername='%s')"%(adaptername))
        DNS1 = False
        DNS2 = False
        try:
            DEVICE_GUID = winregs.get_networkadapter_guid(self.DEBUG,adaptername,self.STATE_OVPN)
            DEVICE_DATA = winregs.get_interface_infos_from_guid(self.DEBUG,DEVICE_GUID,self.STATE_OVPN)
            try:
                DNS1 = DEVICE_DATA['NameServer'].split(",")[0]
                if self.isValueIPv4(DNS1):
                    if self.STATE_OVPN == False:
                        self.debug(1,"def win_read_dns_from_interface(%s): 1st DNS '%s' backuped" % (adaptername,DNS1))
                    try:
                        DNS2 = DEVICE_DATA['NameServer'].split(",")[1]
                        if self.isValueIPv4(DNS2):
                            if self.STATE_OVPN == False:
                                self.debug(1,"def win_read_dns_from_interface(%s): 2nd DNS '%s' backuped" % (adaptername,DNS2))
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        except Exception as e:
            pass
        return { "DNS1":DNS1,"DNS2":DNS2 }

    def win_read_dns_to_backup(self):
        self.debug(1,"def win_read_dns_to_backup()")
        try:
            if not self.WIN_EXT_DEVICE == False:
                self.debug(1,"def win_read_dns_to_backup: self.WIN_EXT_DEVICE = '%s'"%(self.WIN_EXT_DEVICE))
                data = False
                data = self.win_read_dns_from_interface(self.WIN_EXT_DEVICE)
                if not data == False and len(data) == 2:
                    if self.isValueIPv4(data["DNS1"]):
                        self.GATEWAY_DNS1 = data["DNS1"]
                        if self.isValueIPv4(data["DNS2"]):
                            self.GATEWAY_DNS2 = data["DNS2"]
                    if not self.GATEWAY_DNS1 == False:
                        self.debug(1,"def win_read_dns_to_backup: set self.WIN_EXT_DHCP_DNS = False, self.GATEWAY_DNS1 = '%s', self.GATEWAY_DNS2 = '%s'" % (self.GATEWAY_DNS1,self.GATEWAY_DNS2))
                        self.WIN_EXT_DHCP_DNS = False
                    else:
                        self.debug(1,"def win_read_dns_to_backup: set self.WIN_EXT_DHCP_DNS = True")
                        self.WIN_EXT_DHCP_DNS = True
                    return True
            else:
                self.debug(1,"def win_read_dns_to_backup: self.WIN_EXT_DEVICE == False")
        except Exception as e:
            self.debug(1,"def win_read_dns_to_backup: failed, exception = '%s'"%(e))
            return False

    def win_check_dns(self):
        if self.VAR['OVPN']['STOP'] == True:
            return True
        if self.NO_DNS_CHANGE == True:
            return True
        if self.check_dns_is_whitelisted() == True:
            return True
        try:
            DNSI = self.win_read_dns_from_interface(self.WIN_EXT_DEVICE)
            DNSS = self.select_dns()
            self.debug(2,"def win_check_dns: DNSI = '%s', DNSS = '%s'"%(DNSI,DNSS))
            for key,DNS in DNSI.items():
                if key == "DNS2" and DNS == False:
                    continue
                if not DNS in DNSS:
                    self.debug(1,"def win_check_dns: DNS '%s' not in DNSS '%s'"%(DNS,DNSS))
                    return False
            return True
        except Exception as e:
            self.debug(1,"def win_check_dns: failed, exception = '%s'"%(e))

    def select_dns(self,domaindns=False):
        self.debug(2,"def select_dns()")
        try:
            if self.GATEWAY_DNS1 == "127.0.0.1":
                return ["127.0.0.1"]
            dnslist = list()
            if domaindns == False:
                servername = self.VAR['OVPN']['CONN']['SERVER']
                try:
                    pridns = self.MYDNS[servername]["primary"]["ip4"]
                    dnslist.append(pridns)
                    try:
                        secdns = self.MYDNS[servername]["secondary"]["ip4"]
                        dnslist.append(secdns)
                    except Exception as e:
                        if self.STATE_OVPN == False:
                            self.debug(1,"def select_dns: secdns not found")
                except Exception as e:
                    if self.STATE_OVPN == False:
                        self.debug(1,"def select_dns: pridns not found")
            elif domaindns == True:
                DNSS = release_version.org_data()["DNS_SRV1"]
                rand1, rand2 = 0, 0
                while rand1 == rand2:
                    rand1 = random.randint(0,len(DNSS)-1)
                    rand2 = random.randint(0,len(DNSS)-1)
                DOMAIN_DNS1 = DNSS[rand1]
                DOMAIN_DNS2 = DNSS[rand2]
                dnslist.append(DOMAIN_DNS1)
                dnslist.append(DOMAIN_DNS2)
            if len(dnslist) == 0:
                dnslist.append(self.VAR['OVPN']['GW']['IP4A'])
            return dnslist
        
        except Exception as e:
            self.debug(1,"def select_dns, failed exception = '%s'"%(e))

    def load_ca_cert(self):
        self.debug(1,"def load_ca_cert()")
        if os.path.isfile(self.CA_FILE):
            self.CA_FILE_HASH = hashings.hash_sha512_file(self.DEBUG,self.CA_FILE)
            if self.CA_FILE_HASH == self.CA_FIXED_HASH:
                try:
                    os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), self.CA_FILE)
                    return True
                except Exception as e:
                    self.msgwarn(_("Error:\nSSL Root Certificate for %s not loaded %s") % (VCP_DOMAIN,self.CA_FILE),_("Error"))
                    return False
            else:
                self.msgwarn(_("Error:\nInvalid SSL Root Certificate for %s in:\n'%s'\nhash is:\n'%s'\nbut should be '%s'") % (VCP_DOMAIN,self.CA_FILE,self.CA_FILE_HASH,self.CA_FIXED_HASH),_("Error: SSL CA Cert #2"))
                return False
        else:
            self.msgwarn(_("Error:\nSSL Root Certificate for %s not found in:\n'%s'!") % (VCP_DOMAIN,self.CA_FILE),_("Error"))
            return False

    def win_firewall_start(self):
        self.debug(1,"def win_firewall_start()")
        if self.NO_WIN_FIREWALL == True:
            return True
        if self.NO_DNS_CHANGE == False:
            self.win_ipconfig_flushdns()
        NETSH_CMDLIST = list()
        if self.WIN_RESET_FIREWALL == True:
            NETSH_CMDLIST.append("advfirewall reset")
        #NETSH_CMDLIST.append("advfirewall set privateprofile logging filename \"%s\"" % (self.pfw_private_log))
        #NETSH_CMDLIST.append("advfirewall set publicprofile logging filename \"%s\"" % (self.pfw_public_log))
        #NETSH_CMDLIST.append("advfirewall set domainprofile logging filename \"%s\"" % (self.pfw_domain_log))
        NETSH_CMDLIST.append("advfirewall set allprofiles state on")
        NETSH_CMDLIST.append("advfirewall set privateprofile firewallpolicy blockinbound,blockoutbound")
        NETSH_CMDLIST.append("advfirewall set domainprofile firewallpolicy blockinbound,blockoutbound")
        if self.TAP_BLOCKOUTBOUND == True:
            opt = "blockoutbound"
        else:
            opt = "allowoutbound"
        NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,%s" % (opt))
        if self.win_join_netsh_cmd(NETSH_CMDLIST):
            self.WIN_FIREWALL_STARTED = True
            return True

    def win_firewall_tap_blockoutbound(self):
        self.win_firewall_tap_blockoutbound_running = True
        self.debug(1,"def win_firewall_tap_blockoutbound()")
        NETSH_CMDLIST = list()
        try:
            if self.NO_WIN_FIREWALL == True:
                self.win_firewall_tap_blockoutbound_running = False
                return
            if self.TAP_BLOCKOUTBOUND == True:
                self.win_firewall_whitelist_ovpn_on_tap(option="delete")
                self.win_firewall_whitelist_ovpn_on_tap(option="add")
                NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,blockoutbound")
            else:
                self.win_firewall_whitelist_ovpn_on_tap(option="delete")
                NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,allowoutbound")
            self.win_join_netsh_cmd(NETSH_CMDLIST)
            self.debug(1,"Block outbound on TAP!\n\nAllow Whitelist to Internal oVPN Services\n\n'%s'\n\nSee all Rules:\n Windows Firewall with Advanced Security\n --> Outgoing Rules" % (self.WHITELIST_PUBLIC_PROFILE))
        except Exception as e:
            self.debug(1,"def win_firewall_tap_blockoutbound: failed!")
        self.win_firewall_tap_blockoutbound_running = False

    def win_firewall_allowout(self):
        self.debug(1,"def win_firewall_allowout()")
        if self.NO_WIN_FIREWALL == True:
            return True
        NETSH_CMDLIST = list()
        NETSH_CMDLIST.append("advfirewall set allprofiles state on")
        NETSH_CMDLIST.append("advfirewall set privateprofile firewallpolicy blockinbound,allowoutbound")
        NETSH_CMDLIST.append("advfirewall set domainprofile firewallpolicy blockinbound,allowoutbound")
        NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,allowoutbound")
        if self.win_join_netsh_cmd(NETSH_CMDLIST):
            self.WIN_FIREWALL_STARTED = True
            return True

    def win_firewall_block_on_exit(self):
        self.debug(1,"def win_firewall_block_on_exit()")
        if self.NO_WIN_FIREWALL == True:
            return True
        NETSH_CMDLIST = list()
        NETSH_CMDLIST.append("advfirewall set allprofiles state on")
        NETSH_CMDLIST.append("advfirewall set privateprofile firewallpolicy blockinbound,blockoutbound")
        NETSH_CMDLIST.append("advfirewall set domainprofile firewallpolicy blockinbound,blockoutbound")
        NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,blockoutbound")
        return self.win_join_netsh_cmd(NETSH_CMDLIST)

    def win_firewall_whitelist_ovpn_on_tap(self,option):
        self.debug(1,"def win_firewall_whitelist_ovpn_on_tap()")
        if self.NO_WIN_FIREWALL == True:
            self.debug(1,"def win_firewall_whitelist_ovpn_on_tap: self.NO_WIN_FIREWALL == True")
            return True
        if option == "add":
            actionstring = "action=allow"
        elif option == "delete":
            actionstring = ""
        NETSH_CMDLIST = list()
        for entry,value in self.WHITELIST_PUBLIC_PROFILE.items():
            ip = value["ip"]
            port = value["port"]
            protocol = value["proto"]
            rule_name = "(oVPN) Allow OUT on TAP: %s %s:%s %s" % (entry,ip,port,protocol)
            rule_string = "advfirewall firewall %s rule name=\"%s\" remoteip=\"%s\" remoteport=\"%s\" protocol=\"%s\" profile=public dir=out %s" % (option,rule_name,ip,port,protocol,actionstring)
            NETSH_CMDLIST.append(rule_string)
            self.debug(1,"Whitelist: %s %s %s %s" % (entry,ip,port,protocol))
        return self.win_join_netsh_cmd(NETSH_CMDLIST)
    
    def win_firewall_clear_vcp_rules(self):
        if self.WIN_FIREWALL_ADDED_RULE_TO_VCP == True:
            while self.win_firewall_set_vcp_rules(option="delete"):
                pass
    
    def win_firewall_set_vcp_rules(self,option):
        if self.NO_WIN_FIREWALL == True:
            self.debug(1,"def win_firewall_set_vcp_rules: self.NO_WIN_FIREWALL == True, return True")
            return True
        if option == "add" and self.state_openvpn() == True:
            self.debug(1,"def win_firewall_set_vcp_rules: option == add and state_openvpn() == True, return True")
            return True
        if option == "add" and self.WIN_FIREWALL_ADDED_RULE_TO_VCP == True:
            self.debug(1,"def win_firewall_set_vcp_rules: option == add and self.WIN_FIREWALL_ADDED_RULE_TO_VCP == True, return True")
            return True
        if option == "delete" and self.WIN_FIREWALL_ADDED_RULE_TO_VCP == False:
            self.debug(1,"def win_firewall_set_vcp_rules: option == del and self.WIN_FIREWALL_ADDED_RULE_TO_VCP == False, return False")
            return False
        self.debug(1,"def win_firewall_set_vcp_rules(%s)"%(option))
        try:
            NETSH_CMDLIST = list()
            
            if option == "add":
                actionstring = "action=allow"
            elif option == "delete":
                actionstring = ""
            
            program = 'program="%s\\ovpn_client.exe"' % (self.BIN_DIR)
            rule_name1 = "oVPN.to Client Allow OUT SSL"
            rule_name2 = "oVPN.to Client Allow OUT DNS"
            rule_string1 = 'advfirewall firewall %s rule name="%s" %s remoteport=443 protocol=tcp profile=any dir=out %s' % (option,rule_name1,program,actionstring)
            NETSH_CMDLIST.append(rule_string1)
            #rule_string2 = 'advfirewall firewall %s rule name="%s" %s remoteport=53 protocol=udp profile=any dir=out %s' % (option,rule_name2,program,actionstring)
            #NETSH_CMDLIST.append(rule_string2)
            
            DNSS = release_version.org_data()["DNS_SRV1"]
            for DNSIP in DNSS:
                rule_name_udp = "oVPN.to Client Allow Domain DNS udp %s" % (DNSIP)
                rule_name_tcp = "oVPN.to Client Allow Domain DNS tcp %s" % (DNSIP)
                rule_dns_udp = 'advfirewall firewall %s rule name="%s" remoteport=53 remoteip=%s protocol=udp profile=any dir=out %s' % (option,rule_name_udp,DNSIP,actionstring)
                rule_dns_tcp = 'advfirewall firewall %s rule name="%s" remoteport=53 remoteip=%s protocol=tcp profile=any dir=out %s' % (option,rule_name_tcp,DNSIP,actionstring)
                NETSH_CMDLIST.append(rule_dns_udp)
                NETSH_CMDLIST.append(rule_dns_tcp)
            if self.win_join_netsh_cmd(NETSH_CMDLIST):
                if option == "add":
                    domaindns = True
                    if self.win_netsh_set_dns_ovpn(domaindns) == True:
                        self.WIN_FIREWALL_ADDED_RULE_TO_VCP = True
                        return True
                elif option == "delete":
                    if self.win_netsh_restore_dns() == True:
                        self.WIN_FIREWALL_ADDED_RULE_TO_VCP = False
                        return True
            return False
        except Exception as e:
            self.debug(1,"def win_firewall_set_vcp_rules: failed, exception = '%s'"%(e))

    def win_firewall_export_on_start(self):
        self.debug(1,"def win_firewall_export_on_start()")
        if self.NO_WIN_FIREWALL == True:
            self.debug(1,"def win_firewall_export_on_start: return NO_WIN_FIREWALL == True")
            return True
        if self.WIN_BACKUP_FIREWALL == False:
            self.debug(1,"def win_firewall_export_on_start: return WIN_BACKUP_FIREWALL == False")
            return True
        self.debug(1,"def win_firewall_export_on_start() call")
        if os.path.isfile(self.pfw_bak):
            os.remove(self.pfw_bak)
        NETSH_CMDLIST = list()
        NETSH_CMDLIST.append('advfirewall export "%s"' % (self.pfw_bak))
        return self.win_join_netsh_cmd(NETSH_CMDLIST)

    def win_firewall_restore_on_exit(self):
        self.debug(1,"def win_firewall_restore_on_exit()")
        if self.NO_WIN_FIREWALL == True:
            self.debug(1,"def win_firewall_restore_on_exit: return NO_WIN_FIREWALL == True")
            return True
        if self.WIN_BACKUP_FIREWALL == False:
            self.debug(1,"def win_firewall_restore_on_exit: return WIN_BACKUP_FIREWALL == False")
            return True
        if self.WIN_FIREWALL_STARTED == True:
            self.debug(1,"def win_firewall_restore_on_exit() call")
            NETSH_CMDLIST = list()
            NETSH_CMDLIST.append("advfirewall reset")
            if os.path.isfile(self.pfw_bak):
                NETSH_CMDLIST.append('advfirewall import "%s"' % (self.pfw_bak))
            return self.win_join_netsh_cmd(NETSH_CMDLIST)

    def win_enable_tap_interface(self):
        self.debug(1,"def win_enable_tap_interface()")
        NETSH_CMDLIST = list()
        NETSH_CMDLIST.append('interface set interface "%s" ENABLED'%(self.WIN_TAP_DEVICE))
        return self.win_join_netsh_cmd(NETSH_CMDLIST)

    def win_disable_ext_interface(self):
        self.debug(1,"def win_disable_ext_interface()")
        if self.WIN_DISABLE_EXT_IF_ON_DISCO == True:
            NETSH_CMDLIST = list()
            NETSH_CMDLIST.append('interface set interface "%s" DISABLED'%(self.WIN_EXT_DEVICE))
            return self.win_join_netsh_cmd(NETSH_CMDLIST)

    def win_enable_ext_interface(self):
        self.debug(1,"def win_enable_ext_interface()")
        NETSH_CMDLIST = list()
        NETSH_CMDLIST.append('interface set interface "%s" ENABLED'%(self.WIN_EXT_DEVICE))
        return self.win_join_netsh_cmd(NETSH_CMDLIST)

    def win_firewall_analyze(self):
        return
        netshcmd = "advfirewall firewall show rule name=all"
        netsh_output = self.win_return_netsh_cmd(netshcmd)
        for line in netsh_output:
            line1 = line.split(":")[-1].lstrip()
            for entry in [ "pidgin","firefox","chrome","icq","skype","commander","github" ]:
                if entry in line1.lower():
                    self.debug(1,"def win_firewall_dumprules: '%s'" % (line1))

    def win_firewall_modify_rule(self,option):
        try:
            self.debug(1,"def win_firewall_modify_rule()")
            if self.NO_WIN_FIREWALL == True:
                return True
            if self.VAR['OVPN']['CONN']['SERVER'] == False and option == "delete":
                return True
            rule_name = "Allow OUT oVPN-IP %s to Port %s Protocol %s" % (self.VAR['OVPN']['CONN']['IP'],self.VAR['OVPN']['CONN']['PORT'],self.VAR['OVPN']['CONN']['PROTO'])
            if option == "add":
                rule_string = "advfirewall firewall %s rule name=\"%s\" remoteip=\"%s\" remoteport=\"%s\" protocol=\"%s\" profile=private dir=out action=allow" % (option,rule_name,self.VAR['OVPN']['CONN']['IP'],self.VAR['OVPN']['CONN']['PORT'],self.VAR['OVPN']['CONN']['PROTO'])
            if option == "delete":
                rule_string = "advfirewall firewall %s rule name=\"%s\"" % (option,rule_name)
            self.debug(1,"def win_firewall_modify_rule: rule_string = '%s'"%(rule_string))
            NETSH_CMDLIST = list()
            NETSH_CMDLIST.append(rule_string)
            return self.win_join_netsh_cmd(NETSH_CMDLIST)
        except Exception as e:
            self.debug(1,"def win_firewall_modify_rule: option = '%s' failed, exception = '%s'" % (option,e))

    def win_return_netsh_cmd(self,cmd):
        self.debug(1,"def win_return_netsh_cmd()")
        if os.path.isfile(self.WIN_NETSH_EXE):
            netshcmd = '%s %s' % (self.WIN_NETSH_EXE,cmd)
            try: 
                self.debug(2,"win_return_netsh_cmd: netshcmd = '%s'"%(netshcmd))
                output = subprocess.check_output(netshcmd,shell=True)
                self.debug(2,"win_return_netsh_cmd: output = '%s'"%(output))
                output0 = encodes.code_fiesta(self.DEBUG,'decode',output,'win_return_netsh_cmd').strip().splitlines()
                self.debug(2,"def win_return_netsh_cmd: output0 = '%s'" % (output0))
                return output0
            except Exception as e:
                self.debug(1,"def win_return_netsh_cmd: '%s' failed, exception = '%s'" % (netshcmd,e))
            return False
        else:
            self.errorquit(text=_("Error: netsh.exe not found!"))

    def win_join_netsh_cmd(self,NETSH_CMDLIST):
        self.debug(1,"def win_join_netsh_cmd()")
        if os.path.isfile(self.WIN_NETSH_EXE):
            i=0
            for cmd in NETSH_CMDLIST:
                netshcmd = '%s %s' % (self.WIN_NETSH_EXE,cmd)
                try: 
                    exitcode = subprocess.check_call(netshcmd,shell=True)
                    if exitcode == 0:
                        self.debug(1,"netshOK: '%s': exitcode = %s" % (netshcmd,exitcode))
                        i+=1
                    else:
                        self.debug(1,"netshERROR: '%s': exitcode = %s" % (netshcmd,exitcode))
                except Exception as e:
                    self.debug(1,"def win_join_netsh_cmd: '%s' failed, exception = '%s'" % (netshcmd,e))
            if len(NETSH_CMDLIST) == i:
                return True
        else:
            self.errorquit(text=_("Error: netsh.exe not found!"))

    def win_return_route_cmd(self,cmd):
        self.debug(1,"def win_return_route_cmd()")
        if os.path.isfile(self.WIN_ROUTE_EXE):
            routecmd = '%s %s' % (self.WIN_ROUTE_EXE,cmd)
            try: 
                self.debug(2,"win_return_route_cmd: routecmd = '%s'"%(routecmd))
                output = subprocess.check_output(routecmd,shell=True)
                self.debug(2,"win_return_route_cmd: output = '%s'"%(output))
                output0 = encodes.code_fiesta(self.DEBUG,'decode',output,'win_return_route_cmd').strip().splitlines()
                self.debug(2,"win_return_route_cmd: output0 = '%s'"%(output0))
                return output0
            except Exception as e:
                self.debug(1,"def win_return_route_cmd: '%s' failed, exception = '%s'" % (routecmd,e))
                return False
        else:
            self.errorquit(text=_("Error: route.exe not found!"))

    def win_join_route_cmd(self,ROUTE_CMDLIST):
        self.debug(1,"def win_join_route_cmd()")
        if os.path.isfile(self.WIN_ROUTE_EXE):
            i=0
            for cmd in ROUTE_CMDLIST:
                routecmd = '%s %s' % (self.WIN_ROUTE_EXE,cmd)
                try:
                    exitcode = subprocess.check_call(routecmd,shell=True)
                    if exitcode == 0:
                        self.debug(1,"routeOK: '%s': exitcode = %s" % (routecmd,exitcode))
                        i+=1
                    else:
                        self.debug(1,"routeERROR: '%s': exitcode = %s" % (routecmd,exitcode))
                except Exception as e:
                    self.debug(1,"def win_join_route_cmd: '%s' failed, exception = '%s'" % (routecmd,e))
            if len(ROUTE_CMDLIST) == i:
                ROUTE_CMDLIST = list()
                return True
        else:
            self.errorquit(text=_("Error: route.exe not found!"))

    def win_ipconfig_flushdns(self):
        self.debug(1,"def win_ipconfig_flushdns()")
        if os.path.isfile(self.WIN_IPCONFIG_EXE):
            try: 
                cmdstring = '%s /flushdns' % (self.WIN_IPCONFIG_EXE)
                exitcode = subprocess.check_call(cmdstring,shell=True)
                if exitcode == 0:
                    self.debug(1,"%s: exitcode = %s" % (cmdstring,exitcode))
                    return True
                else:
                    self.debug(1,"%s: exitcode = %s" % (cmdstring,exitcode))
            except Exception as e:
                self.debug(1,"def win_join_ipconfig_cmd: '%s' failed" % (cmdstring))
        else:
            self.errorquit(text=_("ipconfig.exe not found!"))

    def win_ipconfig_displaydns(self):
        self.debug(1,"def win_ipconfig_displaydns()")
        if os.path.isfile(self.WIN_IPCONFIG_EXE):
            try: 
                cmdstring = '"%s" /displaydns' % (self.WIN_IPCONFIG_EXE)
                out = subprocess.check_output(cmdstring,shell=True)
                return out
            except Exception as e:
                self.debug(1,"def win_ipconfig_displaydns: failed" % (cmdstring))
        else:
            self.errorquit(text=_("ipconfig.exe not found!"))

    def isValueIPv4(self,value):
        self.debug(111,"def isValueIPv4()")
        try:
            if len(value.split('.')) == 4:
                for n in value.split('.'):
                    ni = int(n)
                    #if ni.isdigit():
                    self.debug(111,"def isValueIPv4: n = %s"%(n))
                    if not ni >= 0 and not ni <= 255:
                        return False
                return True
        except Exception as e:
            self.debug(1,"def isValueIPv4: failed, exception = '%s'"%(e))
            return False

    # *** fixme ***
    def isValueIPv6(self,value):
        self.debug(1,"def isValueIPv6()")
        return True

    def form_ask_userid(self):
        self.debug(1,"def form_ask_userid()")
        try:
            self.dialog_form_ask_userid.destroy()
        except Exception as e:
            pass
        try:
            dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK_CANCEL)
            dialogWindow.set_position(Gtk.WindowPosition.CENTER)
            self.dialog_form_ask_userid = dialogWindow
            try:
                dialogWindow.set_icon(self.app_icon)
            except Exception as e:
                pass
            dialogWindow.set_transient_for(self.window)
            dialogWindow.set_border_width(8)
            dialogWindow.set_title(_("oVPN.to Setup"))
            dialogWindow.set_markup(_("Enter your oVPN.to Details"))
            dialogBox = dialogWindow.get_content_area()
            useridEntry = Gtk.Entry()
            if self.USERID == False:
                useridEntry.set_visibility(True)
                useridEntry.set_max_length(9)
                useridEntry.set_size_request(200,24)
                useridLabel = Gtk.Label(label=_("User-ID:"))
                dialogBox.pack_start(useridLabel,False,False,0)
                dialogBox.pack_start(useridEntry,False,False,0)
            else:
                useridLabel1 = Gtk.Label(label=_("User-ID:"))
                useridLabel2 = Gtk.Label(label=" %s"%(self.USERID))
                dialogBox.pack_start(useridLabel1,False,False,0)
                dialogBox.pack_start(useridLabel2,False,False,0)
            apikeyEntry = Gtk.Entry()
            apikeyEntry.set_visibility(False)
            apikeyEntry.set_max_length(128)
            apikeyEntry.set_invisible_char("*")
            apikeyEntry.set_size_request(200,24)
            apikeyLabel = Gtk.Label(label=_("API-Key:"))
            dialogBox.pack_start(apikeyLabel,False,False,0)
            dialogBox.pack_start(apikeyEntry,False,False,0)
            
            checkbox = Gtk.Switch()
            checkbox_title = Gtk.Label(label=_("Save Passphrase in File?"))
            checkbox.set_active(False)
            dialogBox.pack_start(checkbox_title,False,False,0)
            dialogBox.pack_start(checkbox,False,False,0)
            
            dialogWindow.show_all()
            dialogWindow.connect("response", self.response_dialog_apilogin, useridEntry, apikeyEntry, checkbox)
            dialogWindow.connect("close", self.response_dialog_apilogin, None, None, None)
            dialogWindow.run()
        except Exception as e:
            self.debug(1,"def form_ask_userid: failed, exception = '%s'"%(e))

    def response_dialog_apilogin(self, dialog, response_id, useridEntry, apikeyEntry, checkbox):
        self.debug(1,"response_dialog_apilogin()")
        if response_id == Gtk.ResponseType.CANCEL:
            self.debug(1,"def response_dialog_apilogin: response_id == Gtk.ResponseType.CANCEL")
            dialog.destroy()
            return
        elif response_id == Gtk.ResponseType.OK:
            self.debug(1,"def response_dialog_apilogin: Gtk.ResponseType.OK self.USERID = '%s'"%(self.USERID))
            if self.USERID == False:
                userid = int(useridEntry.get_text().rstrip())
            else:
                userid = int(self.USERID)
            apikey = apikeyEntry.get_text().rstrip()
            self.debug(1,"def response_dialog_apilogin: Gtk.ResponseType.OK userid = '%s'"%(userid))
            if userid > 1 and (len(apikey) == 0 or (len(apikey) == 128 and apikey.isalnum())) and (self.USERID == False or self.USERID == userid):
                dialog.destroy()
                saveph = checkbox.get_active()
                if saveph == True:
                    self.SAVE_APIKEY_INFILE = True
                else:
                    self.SAVE_APIKEY_INFILE = False
                if self.USERID == False:
                    self.debug(1,"def response_dialog_apilogin: self.USERID == False")
                    api_dir = "%s\\%s" % (self.APP_DIR,userid)
                    if not os.path.isdir(api_dir):
                        os.mkdir(api_dir)
                        if os.path.isdir(api_dir):
                            self.API_DIR = api_dir
                            self.USERID = userid
                            if len(apikey) == 0:
                                self.APIKEY = False
                            else:
                                # don't ask if 'auth' is true or false, or expired user have to enter apikey on upgrade again...
                                self.APIKEY = apikey
                                self.API_REQUEST("auth")
                                
                            self.debug(1,"def response_dialog_apilogin: return True #1")
                            return True
                elif not self.API_DIR == False and os.path.isdir(self.API_DIR):
                    if len(apikey) == 0:
                        self.APIKEY = False
                    else:
                        self.APIKEY = apikey
                        # don't ask if 'auth' is true or false, or expired user have to enter apikey on upgrade again...
                        self.API_REQUEST("auth")
                    if not self.write_options_file() == True:
                        self.APIKEY = False
                        return False
                    self.INIT_FIRST_UPDATE = True
                    self.debug(1,"def response_dialog_apilogin: return True #2")
                    return True
        elif dialog:
            dialog.destroy()

    def dialog_apikey(self):
        self.debug(1,"def dialog_apikey()")
        self.form_ask_userid()
        if not self.APIKEY == False:
            self.debug(1,"def dialog_apikey: self.APIKEY '-NOT_FALSE-'")
            if self.request_LOAD_SRVDATA == True:
                self.LOAD_SRVDATA = True
                self.request_LOAD_SRVDATA = False
            if self.request_LOAD_ACCDATA == True:
                self.LOAD_ACCDATA = True
                self.request_LOAD_ACCDATA = False
            if self.request_UPDATE == True:
                self.request_UPDATE = False
                self.check_remote_update("config")
        self.UPDATE_SWITCH = True

    def cb_interface_selector_changed(self, combobox):
        self.debug(1,"def cb_interface_selector_changed()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.WIN_EXT_DEVICE = model[index][0]
            self.debug(1,"def cb_interface_selector_changed: selected IF = '%s'" % (self.WIN_EXT_DEVICE))
        return

    def cb_select_userid(self, combobox):
        self.debug(1,"def cb_select_userid()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1 and model[index][0].isdigit() and model[index][0] > 1:
            self.USERID = model[index][0]
            self.debug(1,"def cb_select_userid: selected USERID = '%s'" % (self.USERID))
        return

    def cb_tap_interface_selector_changed(self, combobox):
        self.debug(1,"def cb_tap_interface_selector_changed()")
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.WIN_TAP_DEVICE = model[index][0]
            self.debug(1,"def cb_tap_interface_selector_changed: selected tap IF = '%s'" % (self.WIN_TAP_DEVICE))
        return

    def check_last_server_update(self,remote_lastupdate):
        self.debug(1,"def check_last_server_update(): self.LAST_CFG_UPDATE = '%s', remote_lastupdate = '%s'" % (self.LAST_CFG_UPDATE,remote_lastupdate))
        if self.LAST_CFG_UPDATE < int(remote_lastupdate):
            self.remote_lastupdate = remote_lastupdate
            self.debug(1,"def check_last_server_update: requesting update")
            return True
        else:
            self.debug(1,"def check_last_server_update: no update")
            return False

    def write_last_update(self):
        self.debug(1,"def write_last_update()")
        self.LAST_CFG_UPDATE = self.remote_lastupdate
        if self.write_options_file():
            return True

    def reset_last_update(self):
        self.debug(1,"def reset_last_update()")
        self.LAST_CFG_UPDATE = 0
        if self.write_options_file():
            return True

    def cb_check_normal_update(self):
        # call with GLib.idle_add !
        self.debug(1,"def cb_check_normal_update()")
        if self.check_remote_update("config") == True:
            self.debug(1,"def cb_check_normal_update: self.check_remote_update() == True")
            return True

    def cb_check_client_update(self):
        # call with GLib.idle_add !
        self.debug(1,"def cb_check_client_update()")
        if self.check_remote_update("client") == True:
            self.debug(1,"def cb_check_client_update: self.cb_check_client_update() == True")
            return True

    def cb_force_update(self):
        # call with GLib.idle_add !
        self.debug(1,"def cb_force_update()")
        if self.reset_last_update() == True:
            self.debug(1,"def cb_force_update: self.reset_last_update")
            self.cb_check_normal_update()

    def cb_resetextif(self):
        self.debug(1,"def cb_resetextif()")
        self.WIN_EXT_DEVICE = False
        self.WIN_TAP_DEVICE = False
        self.WIN_RESET_EXT_DEVICE = True
        self.read_interfaces()
        self.write_options_file()
        self.settings_network_switch_disableextifondisco_checkbox_title.set_text("Disable '%s' on Disconnect (default: OFF)"%(self.WIN_EXT_DEVICE))

    def cb_extserverview(self,widget,event):
        if event.button == 1:
            self.debug(1,"def cb_extserverview()")
            if self.LOAD_SRVDATA == False and not self.APIKEY == False:
                self.LOAD_SRVDATA = True
                self.LAST_OVPN_SRV_DATA_UPDATE = 0
                self.VAR['OVPN']['SERVERDATA'] = {}
            elif self.APIKEY == False:
                self.request_LOAD_SRVDATA = True
                GLib.idle_add(self.dialog_apikey)
            else:
                self.LOAD_SRVDATA = False
            self.write_options_file()
            self.rebuild_mainwindow()
        self.UPDATE_SWITCH = True

    def cb_extserverview_size(self,widget,event):
        if event.button == 1:
            self.debug(1,"def cb_extserverview_size()")
            dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK_CANCEL)
            dialogWindow.set_border_width(8)
            try:
                actualwidth = self.mainwindow.get_size()[0]
                actualheigt = self.mainwindow.get_size()[1]
            except Exception as e:
                actualwidth = 0
                actualheigt = 0
            dialogWindow.set_position(Gtk.WindowPosition.CENTER)
            dialogWindow.set_transient_for(self.window)
            dialogWindow.set_border_width(8)
            try:
                dialogWindow.set_icon(self.app_icon)
            except Exception as e:
                pass
            text = _("Server Window Size")
            dialogWindow.set_title(text)
            dialogWindow.set_markup(_("Enter width and height\n\nLeave blank for default"))
            dialogBox = dialogWindow.get_content_area()
            widthLabel = Gtk.Label(label=_("Width (pixel):"))
            widthEntry = Gtk.Entry()
            widthEntry.set_visibility(True)
            widthEntry.set_size_request(40,24)
            if not actualwidth == 0:
                widthEntry.set_text(str(actualwidth))
            heightLabel = Gtk.Label(label=_("Height (pixel):"))
            heightEntry = Gtk.Entry()
            heightEntry.set_visibility(True)
            heightEntry.set_size_request(40,24)
            if not actualheigt == 0:
                heightEntry.set_text(str(actualheigt))
            dialogBox.pack_start(widthLabel,False,False,0)
            dialogBox.pack_start(widthEntry,False,False,0)
            dialogBox.pack_start(heightLabel,False,False,0)
            dialogBox.pack_start(heightEntry,False,False,0)
            dialogWindow.show_all()
            response = dialogWindow.run()
            if response == Gtk.ResponseType.CANCEL:
                dialogWindow.destroy()
                #print "response: btn cancel %s" % (response)
                return False
            elif response == Gtk.ResponseType.OK:
                WIDTH = widthEntry.get_text().rstrip()
                HEIGHT = heightEntry.get_text().rstrip()
                dialogWindow.destroy()
                if self.LOAD_SRVDATA == True:
                    if WIDTH == "": WIDTH = self.SRV_WIDTH_DEFAULT;
                    if HEIGHT == "": HEIGHT = self.SRV_HEIGHT_DEFAULT;
                    self.SRV_WIDTH = WIDTH
                    self.SRV_HEIGHT = HEIGHT
                    self.debug(1,"def cb_extserverview_size(): %sx%s" % (self.SRV_WIDTH,self.SRV_HEIGHT))
                else:
                    if WIDTH == "": WIDTH = self.SRV_LIGHT_WIDTH_DEFAULT;
                    if HEIGHT == "": HEIGHT = self.SRV_LIGHT_HEIGHT_DEFAULT;
                    self.SRV_LIGHT_WIDTH = WIDTH
                    self.SRV_LIGHT_HEIGHT = HEIGHT
                    self.debug(1,"def cb_extserverview_size(): %sx%s" % (self.SRV_LIGHT_WIDTH,self.SRV_LIGHT_HEIGHT))
                self.write_options_file()
                WIDTH = int(WIDTH)
                HEIGHT = int(HEIGHT)
                GLib.idle_add(self.mainwindow.resize,int(WIDTH),int(HEIGHT))
                return True
            else:
                return False

    def cb_set_loaddataevery(self,widget,event):
        if event.button == 1:
            self.debug(1,"def cb_set_loaddataevery()")
            dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK_CANCEL)
            dialogWindow.set_position(Gtk.WindowPosition.CENTER)
            dialogWindow.set_transient_for(self.window)
            dialogWindow.set_border_width(8)
            dialogWindow.set_icon(self.app_icon)
            text = _("Load Data every X seconds")
            dialogWindow.set_title(text)
            dialogWindow.set_markup(text)
            dialogBox = dialogWindow.get_content_area()
            Label = Gtk.Label(label=_("seconds:"))
            adjustment = Gtk.Adjustment(0, 66, 86400, 1, 10, 0)
            Entry = Gtk.SpinButton()
            Entry.set_adjustment(adjustment)
            Entry.set_visibility(True)
            Entry.set_size_request(40,24)
            dialogBox.pack_start(Label,False,False,0)
            dialogBox.pack_start(Entry,False,False,0)
            dialogWindow.show_all()
            response = dialogWindow.run()
            if response == Gtk.ResponseType.CANCEL:
                dialogWindow.destroy()
                #print "response: btn cancel %s" % (response)
                return False
            elif response == Gtk.ResponseType.OK:
                try:
                    seconds = int(Entry.get_text().rstrip())
                except Exception as e:
                    dialogWindow.destroy()
                    return
                dialogWindow.destroy()
                if seconds <= 66:
                    seconds = 66
                self.LOAD_DATA_EVERY = seconds
                self.write_options_file()
                return True
            else:
                dialogWindow.destroy()
                return False

    def cb_hide_cells(self,widget,event):
        self.debug(1,"def cb_hide_cells()")
        try:
            if self.HIDECELLSWINDOW_OPEN == False:
                self.HIDECELLSWINDOW_OPEN = True
                hidecellswindow = Gtk.Window(Gtk.WindowType.TOPLEVEL)
                vbox = Gtk.VBox(False,spacing=2)
                vbox.set_border_width(8)
                hidecellswindow.add(vbox)
                hidecellswindow.connect("destroy",self.cb_destroy_hidecellswindow)
                hidecellswindow.set_position(Gtk.WindowPosition.CENTER)
                hidecellswindow.set_size_request(600,100)
                hidecellswindow.set_transient_for(self.window)
                hidecellswindow.set_icon(self.app_icon)
                text = _("Hide unwanted cells")
                hidecellswindow.set_title(text)
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
                vbox.pack_start(scrolledwindow, True, True, 0)
                grid = Gtk.Grid()
                grid.set_column_homogeneous(True)
                grid.set_row_homogeneous(False)
                grid.set_row_spacing(5)
                grid.set_column_spacing(5)
                grid.props.halign = Gtk.Align.CENTER
                scrolledwindow.add(grid)
                i = 0
                x = 0
                for cellid in self.VAR['MAIN']['ALLOWCELLHIDE']:
                    cellname = self.VAR['MAIN']['CELLINDEX'][cellid]
                    #print cellname
                    button = Gtk.ToggleButton(label=cellname)
                    if cellid in self.VAR['MAIN']['SHOWCELLS']:
                        button.set_active(True)
                    else:
                        button.set_active(False)
                    button.connect("toggled",self.cb_hide_cells2,cellid)
                    grid.attach(button,x,i,1,1)
                    if x >= 7:
                        i += 1
                        x = 0
                    else:
                        x += 1
                hidecellswindow.show_all()
                hidecellswindow.resize(grid.get_allocation().width + 20, grid.get_allocation().height + 20)
        except Exception as e:
            self.debug(1,"def cb_hide_cells: failed, exception = '%s'"%(e))
            self.HIDECELLSWINDOW_OPEN = False

    def cb_hide_cells2(self,button,cellid):
        self.debug(1,"def cb_hide_cells2() cellid = '%s'"%(cellid))
        if cellid in self.VAR['MAIN']['ALLOWCELLHIDE']:
            if cellid in self.VAR['MAIN']['SHOWCELLS']:
                self.VAR['MAIN']['SHOWCELLS'].remove(cellid)
                self.debug(1,"def cb_hide_cells2: remove cellid = '%s'"%(cellid))
            else:
                self.VAR['MAIN']['SHOWCELLS'].append(cellid)
                self.debug(1,"def cb_hide_cells2: append cellid = '%s'"%(cellid))
            self.write_options_file()
            self.rebuild_mainwindow()

    def cb_change_ipmode1(self):
        self.debug(1,"def cb_change_ipmode1() *GLib*")
        self.VAR['OVPN']['CFGTYPE'] = "23x"
        self.write_options_file()
        self.read_options_file()
        self.VAR['OVPN']['SERVERLIST'] = {}
        self.load_ovpn_server()
        if len(self.VAR['OVPN']['SERVERLIST']) == 0:
            self.msgwarn(_("Changed Option:\n\nUse 'Forced Config Update' to get new configs!"),_("Switched to IPv4"))
            self.cb_force_update()
        self.rebuild_mainwindow()
        self.UPDATE_SWITCH = True

    def cb_change_ipmode2(self):
        self.debug(1,"def cb_change_ipmode2() *GLib*")
        self.VAR['OVPN']['CFGTYPE'] = "23x46"
        self.write_options_file()
        self.read_options_file()
        self.VAR['OVPN']['SERVERLIST'] = {}
        self.load_ovpn_server()
        if len(self.VAR['OVPN']['SERVERLIST']) == 0:
            self.msgwarn(_("Changed Option:\n\nUse 'Forced Config Update' to get new configs!"),_("Switched to IPv4+6"))
            self.cb_force_update()
        self.rebuild_mainwindow()
        self.UPDATE_SWITCH = True

    # *** fixme: need isValueIPv6 first! ***
    def cb_change_ipmode3(self):
        self.debug(1,"def cb_change_ipmode3() *GLib*")
        return True
        self.VAR['OVPN']['CFGTYPE'] = "23x64"
        self.write_options_file()
        self.read_options_file()
        self.VAR['OVPN']['SERVERLIST'] = {}
        self.load_ovpn_server()
        if len(self.VAR['OVPN']['SERVERLIST']) == 0:
            self.msgwarn(_("Changed Option:\n\nUse 'Forced Config Update' to get new configs!"),_("Switched to IPv6+4"))
            self.cb_check_normal_update()
        self.rebuild_mainwindow()
        self.UPDATE_SWITCH = True

    def cb_restore_firewallbackup(self,page,file):
        self.debug(1,"def cb_restore_firewallbackup()")
        fwbak = "%s\\%s" % (self.pfw_dir,file)
        if os.path.isfile(fwbak):
            self.debug(1,"def cb_restore_firewallbackup: %s" % (fwbak))
            self.win_firewall_export_on_start()
            NETSH_CMDLIST = list()
            NETSH_CMDLIST.append('advfirewall import "%s"' % (fwbak))
            return self.win_join_netsh_cmd(NETSH_CMDLIST)

    def delete_dir(self,path):
        self.debug(1,"def delete_dir()")
        if self.OS == "win32":
            cmdstring = 'rmdir /S /Q "%s"' % (path)
            self.debug(1,"def delete_dir: %s" % (cmdstring))
            subprocess.check_output(cmdstring,shell=True)

    """ *fixme* move to openvpn.py """
    def extract_ovpn(self):
        self.debug(1,"def extract_ovpn()")
        try:
            if os.path.isfile(self.zip_cfg):
                z1file = zipfile.ZipFile(self.zip_cfg)
                if os.path.isdir(self.VPN_CFG):
                    self.debug(1,"def extract_ovpn: os.path.isdir(%s), delete"%(self.VPN_CFG))
                    self.delete_dir(self.VPN_CFG)
                if not os.path.isdir(self.VPN_CFG):
                    try:
                        os.mkdir(self.VPN_CFG)
                        self.debug(1,"def extract_ovpn: os.mkdir(%s)"%(self.VPN_CFG))
                    except Exception as e:
                        self.debug(1,"def extract_ovpn: %s not found, create failed."%(self.VPN_CFG))
                try:
                    z1file.extractall(self.VPN_CFG)
                    if self.write_last_update():
                        self.debug(1,"def extract_ovpn: write_last_update() return True")
                        return True
                except Exception as e:
                    self.debug(1,"Error on extracting Certificates and Configs!")
                    return False
        except Exception as e:
            self.debug(1,"def extract_ovpn: failed, exception = '%s'"%(e))

    def API_REQUEST(self,API_ACTION):
        self.debug(1,"def API_REQUEST(%s)"%(API_ACTION))
        if self.APIKEY == False:
            self.msgwarn(_("No API Key!"),_("Error"))
            return False
        
        if not self.load_ca_cert():
            self.debug(1,"def API_REQUEST: load_ca_cert() failed, exception = '%s'"%(e))
            return False
            
        try:
            HEADERS = request_api.useragent(self.DEBUG)
            if API_ACTION == "auth" or API_ACTION == "lastupdate" or API_ACTION == "winrelease" or API_ACTION == "winrelease_url":
                if API_ACTION == "winrelease" or API_ACTION == "winrelease_url":
                    MYBITS = int(BUILT_STRING.split()[7])
                    values = { 'action' : API_ACTION, 'bits' : MYBITS }
                else:
                    values = { 'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION }
                r = requests.post(url=self.APIURL,data=values,headers=HEADERS)
                response = r.text
                if response == "AUTHERROR":
                    self.msgwarn(_("Invalid User-ID or API-Key or Account expired!"),_("Error"))
                    self.timer_check_certdl_running = False
                    return False
                elif response == "AUTHOK:True":
                    self.msgwarn(_("API Login OK!"),_("Success"))
                    return True
                elif response.startswith("AUTHOK:1"):
                    data = response.split(":")
                    if data[0] == "AUTHOK":
                        self.curldata = int(data[1])
                        return True
                elif API_ACTION == "winrelease_url":
                    MYRELEASETIME = int(BUILT_STRING.split()[6].split('(')[1].split(')')[0])
                    data = json.loads(str(response))
                    self.debug(1,"def API_REQUEST: winrelease_url data = '%s'"%(data))
                    UPDATE_FILE = data["FILE"]
                    UPDATE_HASH = data["HASH"]
                    UPDATE_SIZE = int(data["SIZE"])
                    UPDATE_URL = data["URL"]
                    UPDATE_RELEASE = int(data["RELEASE"])
                    if UPDATE_RELEASE > self.VAR["RELEASE"]:
                        clistring1 = "ovpn_client_v"
                        clistring2 = "-gtk3_win%s_setup.exe" % (MYBITS)
                        if len(UPDATE_HASH) == 128:
                            if UPDATE_URL.startswith("https://") and UPDATE_URL.endswith("/files/ovpn_cli/"):
                                if UPDATE_FILE.startswith(clistring1) and UPDATE_FILE.endswith(clistring2):
                                    self.VAR["UPDATE"]["HASH"] = UPDATE_HASH
                                    self.VAR["UPDATE"]["FILE"] = UPDATE_FILE
                                    self.VAR["UPDATE"]["SIZE"] = UPDATE_SIZE
                                    self.VAR["UPDATE"]["URL"] = UPDATE_URL
                                    return self.download_client_update()
                                else:
                                    self.debug(1,"def API_REQUEST: winrelease_url invalid update filename")
                            else:
                                self.debug(1,"def API_REQUEST: winrelease_url invalid update url")
                        else:
                            self.debug(1,"def API_REQUEST: winrelease_url invalid update hash")
                    self.msgwarn(_("No Client Update available!"), _("Success"))
                    return True
                else:
                    self.debug(1,"def API_REQUEST: unknown response = '%s'"%(response))
            
            elif API_ACTION == "getconfigs":
                if os.path.isfile(self.zip_cfg):
                    os.remove(self.zip_cfg)
                values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION, 'version' : self.VAR['OVPN']['CFGTYPE'], 'type' : 'win' }
                r = requests.post(url=self.APIURL,data=values,headers=HEADERS)
                try:
                    fp = open(self.zip_cfg, "wb")
                    fp.write(r.content)
                    fp.close()
                    return True
                except Exception as e:
                    self.debug(1,"def API_REQUEST: failed write config, exception = '%s'"%(e))
                    return False
        except Exception as e:
            self.debug(1,"def API_REQUEST: failed, exception = '%s'"%(e))

    def download_client_update(self):
        try:
            user_dl_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
            self.debug(1,"def download_client_update: user_dl_dir = '%s'"%(user_dl_dir))
            if os.path.isdir(user_dl_dir):
                localfile = str(user_dl_dir+"\\"+self.VAR["UPDATE"]["FILE"])
                if not os.path.isfile(localfile):
                    self.debug(1,"def download_client_update: localfile = '%s' not found"%(localfile))
                    self.msgwarn(_("Client Update: Downloading ~15 MB!"),_("Info"))
                    self.STATE_CERTDL = "clientupdatedl"
                    try:
                        HEADERS = request_api.useragent(self.DEBUG)
                        cli_dl_url = str(self.VAR["UPDATE"]["URL"]+self.VAR["UPDATE"]["FILE"])
                        r1 = requests.get(cli_dl_url,headers=HEADERS)
                        if len(r1.content) == self.VAR["UPDATE"]["SIZE"]:
                            fp1 = open(localfile, "wb")
                            fp1.write(r1.content)
                            fp1.close()
                        else:
                            self.debug(1,"def download_client_update: invalid download size, len(r1.content) = '%s'"%(len(r1.content)))
                    except Exception as e:
                        self.debug(1,"def download_client_update: download failed, exception = '%s'"%(e))
                if os.path.isfile(localfile):
                    if hashings.hash_sha512_file(self.DEBUG,localfile) == self.VAR["UPDATE"]["HASH"]:
                        self.msgwarn(_("Client Update: Download verified!"),_("Success"))
                        return True
                    else:
                        os.remove(localfile)
                        self.msgwarn(_("Client Update: Download failed!"),_("Error"))
                return False
        except Exception as e:
            self.debug(1,"def download_client_update: failed, exception = '%s'"%(e))

    def check_inet_connection(self):
        self.debug(1,"def check_inet_connection()")
        try:
            if self.LAST_CHECK_INET_FALSE > int(time.time())-15:
                return False
            if not self.try_socket(API_DOMAIN,443,2) == False:
                return True
            else:
                self.debug(1,"def check_inet_connection: failed #1")
                self.win_firewall_set_vcp_rules("add")
                if not self.try_socket(API_DOMAIN,443,3) == False:
                    self.debug(1,"def check_inet_connection: True")
                    return True
                self.win_firewall_clear_vcp_rules()
                self.LAST_CHECK_INET_FALSE = int(time.time())
                self.debug(1,"def check_inet_connection: failed #2")
            return False
        except Exception as e:
            self.debug(1,"def check_inet_connection: failed, exception = '%s'"%(e))

    def try_socket(self,host,port,tries,i=1):
        while i <= tries:
            if self.VAR['OVPN']['STOP'] == True:
                return False
            self.debug(2,"def try_socket: host = '%s', port = '%s', i = '%s'" % (host,port,i))
            systraytext = _("Testing internet connection!")
            self.tray.set_tooltip_markup(systraytext)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    t1 = time.time()
                    s.connect((host, port))
                    t2 = time.time()
                    PING = (t2-t1)*1000
                    self.VAR['CACHE']['systraytext'] = False
                    self.debug(2,"def try_socket: %s ms" % (PING))
                    s.close()
                    return PING
            except Exception as e:
                self.debug(1,"def try_socket: port %s failed, exception = '%s'"%(port,e))
            if self.VAR['OVPN']['STOP'] == True:
                return False
            time.sleep(3)
            i += 1
        self.VAR['CACHE']['systraytext'] = False
        return False

    def check_myip(self):
        self.debug(2,"def check_myip()")
        # *** fixme *** missing ipv6 support
        if self.VAR['OVPN']['CFGTYPE'] == "23x" or self.VAR['OVPN']['CFGTYPE'] == "23x46":
            if self.LAST_CHECK_MYIP > int(time.time())-random.randint(120,300) and self.VAR['OVPN']['PING_LAST'] > 0:
                return True
            try:
                url = "http://%s/myip4" % (self.VAR['OVPN']['GW']['IP4A'])
                HEADERS = request_api.useragent(self.DEBUG)
                r = requests.get(url,timeout=5,headers=HEADERS)
                rip = r.content.strip().split()[0].decode(decoding)
                self.LAST_CHECK_MYIP = int(time.time())
                if rip == self.VAR['OVPN']['CONN']['IP']:
                    if self.VAR['OVPN']['CONN']['OK'] == False:
                        self.VAR['OVPN']['CONN']['OK'] = True
                        self.VAR['OVPN']['PING_DEAD'] = 0
                        self.VAR['OVPN']['CONN']['FAILEDTIME'] = 0
                        self.send_notify(_("Connection established!"),_("oVPN"))
                    return True
            except Exception as e:
                self.debug(1,"def check_myip: failed, exception = '%s'"%(e))
        else:
            self.debug(1,"def check_myip: invalid self.VAR['OVPN']['CFGTYPE']")
        return False

    def load_firewall_backups(self):
        self.debug(1,"def load_firewall_backups()")
        try:
            if os.path.exists(self.pfw_dir):
                content = os.listdir(self.pfw_dir)
                content.reverse()
                self.FIREWALL_BACKUPS = list()
                x = 0
                for file in content:
                    if x < 10:
                        if file.endswith('.bak.wfw'):
                            filepath = "%s\\%s" % (self.pfw_dir,file)
                            self.FIREWALL_BACKUPS.append(file)
                            x = x + 1
        except Exception as e:
            self.debug(1,"def load_firewall_backups: failed, exception = '%s'"%(e))

    def sort_ovpn_server(self,content):
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        content.sort(key=alphanum_key)
        return content

    def load_ovpn_server(self):
        self.debug(1,"def load_ovpn_server()")
        if len(self.VAR['OVPN']['SERVERLIST']) > 0:
            return
        try:
            if os.path.exists(self.VPN_CFG):
                self.debug(1,"def load_ovpn_server: self.VPN_CFG = '%s'" % (self.VPN_CFG))
                content = os.listdir(self.VPN_CFG)
                content = self.sort_ovpn_server(content)
                self.VAR['OVPN']['SERVERLIST'] = list()
                self.VAR['OVPN']['CONFIGDATA'] = {}
                m, n = 0, 0
                for file in content:
                    if file.endswith('.ovpn.to.ovpn'):
                        filepath = "%s\\%s" % (self.VPN_CFG,file)
                        servername = file[:-5]
                        servershort = servername.split(".")[0].upper()
                        ca, crt, key, tls, i, lines = 0, 0, 0, 0, 0, 0
                        if os.path.isfile(filepath):
                            self.debug(2,"def load_ovpn_server: filepath = '%s'"%(filepath))
                            serverinfo = list()
                            mtu = 0
                            for line in open(filepath):
                                lines += 1
                                if "<ca>" in line or "</ca>" in line:
                                    ca += 1
                                if "<cert>" in line or "</cert>" in line:
                                    crt += 1
                                if "<key>" in line or "</key>" in line:
                                    key += 1
                                if "<tls-auth>" in line or "</tls-auth>" in line:
                                    tls += 1
                                if "remote " in line:
                                    try:
                                        ip = line.split()[1]
                                        port = int(line.split()[2])
                                        # *** fixme need isValueIPv6 first! ***
                                        if self.isValueIPv4(ip) and port > 0 and port <= 65535:
                                            serverinfo.append(ip)
                                            serverinfo.append(port)
                                            i += 1
                                    except Exception as e:
                                        self.errorquit(text=_("Could not read Servers Remote-IP:Port from config: %s") % (file))
                                elif "proto " in line:
                                    #print line
                                    try:
                                        proto = line.split()[1]
                                        if proto.lower()  == "tcp" or proto.lower() == "udp":
                                            proto = proto.upper()
                                            serverinfo.append(proto)
                                            i += 1
                                    except Exception as e:
                                        self.errorquit(text=_("Could not read Servers Protocol from config: %s") % (file))
                                elif line.startswith("cipher "):
                                    #print line
                                    try:
                                        cipher = line.split()[1]
                                        if cipher == "CAMELLIA-256-CBC":
                                            cipher = "CAM-256"
                                        elif cipher == "AES-256-CBC":
                                            cipher = "AES-256"
                                        serverinfo.append(cipher)
                                        i += 1
                                    except Exception as e:
                                        self.errorquit(text=_("Could not read Servers Cipher from config: %s") % (file))
                                if ("fragment " in line or "link-mtu " in line):
                                    #print line
                                    i += 1
                                    try:
                                        mtu = line.split()[1]
                                        serverinfo.append(mtu)
                                    except Exception as e:
                                        mtu = 1500
                                        serverinfo.append(mtu)
                                        self.debug(1,"Could not read mtu from config: %s" % (file))
                                    
                            # end: for line in open(filepath)
                            checks = [ca, crt, key, tls ]
                            for value in checks:
                                if not value == 2:
                                    self.msgwarn(_("Please update your configurations!"),_("Error"))
                                    self.reset_ovpn_values()
                                    self.cb_force_update
                                    return False
                            
                            if mtu == 0:
                                serverinfo.append(1500)
                                i += 1
                            if i == 4:
                                self.VAR['OVPN']['CONFIGDATA'][servershort] = serverinfo
                                self.VAR['OVPN']['SERVERLIST'].append(servername)
                                #self.debug(2,"def load_ovpn_server: file = '%s'" % (file))
                                m += 1
                            else:
                                n += 1
                        else:
                            self.debug(1,"def load_ovpn_server: file = '%s' NOT FOUND" % (file))
                    else:
                        self.debug(1,"def load_ovpn_server: file = '%s' INVALID NAME" % (file))
                self.debug(1,"def load_ovpn_server: loaded %s of %s, error %s" % (m,len(content),n))
                return True
            else:
                self.debug(1,"def load_ovpn_server: no servers found")
                self.reset_last_update()
        except Exception as e:
            self.debug(1,"def load_ovpn_server: failed, exception = '%s'"%(e))

    def load_remote_data(self):
        if self.timer_load_remote_data_running == True:
            return False
        self.timer_load_remote_data_running = True
        if self.APIKEY == False:
            self.debug(6,"def load_remote_data: no api data")
            self.timer_load_remote_data_running = False
            return False
        elif self.state_openvpn() == True and self.VAR['OVPN']['CONN']['SECONDS'] > 0 and self.VAR['OVPN']['PING_LAST'] <= 0:
            self.debug(6,"def load_remote_data: waiting for ovpn connection")
            self.timer_load_remote_data_running = False
            return False
        elif self.state_openvpn() == True and self.VAR['OVPN']['CONN']['SECONDS'] > 0 and self.VAR['OVPN']['PING_LAST'] > 999:
            self.debug(6,"def load_remote_data: high ping")
            self.timer_load_remote_data_running = False
            return False
        elif self.LOAD_SRVDATA == True and self.LOAD_ACCDATA == True:
            if self.load_serverdata_from_remote() == True:
                self.call_redraw_mainwindow()
            if self.load_accinfo_from_remote() == True:
                GLib.idle_add(self.call_redraw_accwindow)
        elif self.LOAD_SRVDATA == True and self.LOAD_ACCDATA == False:
            if self.load_serverdata_from_remote() == True:
                self.call_redraw_mainwindow()
        elif self.LOAD_SRVDATA == False and self.LOAD_ACCDATA == True:
            if self.load_accinfo_from_remote() == True:
                GLib.idle_add(self.call_redraw_accwindow)
        self.timer_load_remote_data_running = False

    def check_hash_dictdata(self,newdata,olddata):
        self.debug(2,"def check_hash_dictdata()")
        try:
            texta = ""
            textb = ""
            for key,value in sorted(newdata.items()):
                texta = "%s %s %s" % (texta,key,value)
            for key,value in sorted(olddata.items()):
                textb = "%s %s %s" % (textb,key,value)
            hasha = hashlib.sha256(texta.encode(locale.getpreferredencoding())).hexdigest()
            hashb = hashlib.sha256(textb.encode(locale.getpreferredencoding())).hexdigest()
            self.debug(2,"def check_hash_dictdata: hasha newdata = '%s'" % (hasha))
            self.debug(2,"def check_hash_dictdata: hashb olddata = '%s'" % (hashb))
            if hasha == hashb:
                return True
        except Exception as e:
            self.debug(1,"def check_hash_dictdata: failed, exception = '%s'"%(e))

    def load_serverdata_from_remote(self):
        updatein = self.LAST_OVPN_SRV_DATA_UPDATE + self.LOAD_DATA_EVERY
        now = int(time.time())
        self.debug(46,"def load_serverdata_from_remote: ?")
        if self.LOAD_SRVDATA == False:
            self.debug(46,"def load_serverdata_from_remote: disabled")
            return False
        elif self.VAR['MAIN']['OPEN'] == False:
            self.debug(46,"def load_serverdata_from_remote: mainwindow not open")
            return False
        elif self.VAR['MAIN']['HIDE'] == True:
            self.debug(46,"def load_serverdata_from_remote: mainwindow is hide")
            return False
        elif updatein > now:
            diff = updatein - now
            self.debug(46,"def load_serverdata_from_remote: time = %s update_in = %s (%s)" % (now,updatein,diff))
            return False
        elif self.check_inet_connection() == False:
            self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time()) - self.LOAD_DATA_EVERY + 15
            self.debug(46,"def load_serverdata_from_remote: no inet connection")
            return False
        try:
            API_ACTION = "loadserverdata"
            values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION }
            HEADERS = request_api.useragent(self.DEBUG)
            r = requests.post(self.APIURL,data=values,headers=HEADERS,timeout=(3,3))
            self.debug(1,"def load_serverdata_from_remote: posted")
            try:
                if not r.text == "AUTHERROR":
                    #self.debug(1,"r.content = '%s'" % (r.content))
                    OVPN_SRV_DATA = json.loads(str(r.text))
                    self.debug(9,"OVPN_SRV_DATA = '%s'" % (OVPN_SRV_DATA))
                    if len(OVPN_SRV_DATA) > 1:
                        if not self.check_hash_dictdata(OVPN_SRV_DATA,self.VAR['OVPN']['SERVERDATA']):
                            self.VAR['OVPN']['SERVERDATA'] = OVPN_SRV_DATA
                            self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
                            self.debug(1,"def load_serverdata_from_remote: loaded, len = %s" % (len(self.VAR['OVPN']['SERVERDATA'])))
                            return True
                        else:
                            self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
                            self.debug(1,"def load_serverdata_from_remote: loaded, hash match")
                            return False
                    else:
                        self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
                        self.debug(1,"def load_serverdata_from_remote: failed! len = %s"%(len(OVPN_SRV_DATA)))
                        return False
                else:
                    self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
                    self.debug(1,"def load_serverdata_from_remote: AUTH ERROR")
                    self.msgwarn(_("Invalid User-ID or API-Key or Account expired!"),_("Error"))
                    return False
            except Exception as e:
                self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
                self.debug(1,"def load_serverdata_from_remote: json decode failed, exception = '%s'"%(e))
                return False
        except Exception as e:
            self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
            self.debug(1,"def load_serverdata_from_remote: api request failed, exception = '%s'"%(e))
            return False

    def load_accinfo_from_remote(self):
        updatein = self.LAST_OVPN_ACC_DATA_UPDATE + self.LOAD_DATA_EVERY
        now = int(time.time())
        self.debug(46,"def load_accinfo_from_remote: ?")
        if self.LOAD_ACCDATA == False:
            self.debug(46,"def load_accinfo_from_remote: disabled")
            return False
        elif self.ACCWINDOW_OPEN == False:
            self.debug(46,"def load_remote_data: mainwindow not open")
            return False
        elif updatein > now:
            diff = updatein - now
            self.debug(46,"def load_accinfo_from_remote: time = %s update_in = %s (%s)" % (now,updatein,diff))
            return False
        elif self.check_inet_connection() == False:
            self.LAST_OVPN_ACC_DATA_UPDATE = now - self.LOAD_DATA_EVERY + 15
            self.debug(46,"def load_accinfo_from_remote: no inet connection")
            return False
        try:
            API_ACTION = "accinfo"
            values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION }
            HEADERS = request_api.useragent(self.DEBUG)
            r = requests.post(self.APIURL,data=values,headers=HEADERS,timeout=(3,3))
            self.debug(1,"def load_accinfo_from_remote: posted")
            try:
                if not r.text == "AUTHERROR":
                    #self.debug(1,"r.content = '%s'" % (r.content))
                    OVPN_ACC_DATA = json.loads(str(r.text))
                    self.debug(9,"OVPN_ACC_DATA = '%s'" % (OVPN_ACC_DATA))
                    if len(OVPN_ACC_DATA) > 1:
                        if not self.check_hash_dictdata(OVPN_ACC_DATA,self.OVPN_ACC_DATA):
                            self.OVPN_ACC_DATA = OVPN_ACC_DATA
                            self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
                            self.debug(1,"def load_accinfo_from_remote: loaded, len = %s"%(len(self.OVPN_ACC_DATA)))
                            self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
                            return True
                        else:
                            self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
                            self.debug(1,"def load_accinfo_from_remote: loaded, hash match")
                            return False
                    else:
                        self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
                        self.debug(1,"def load_accinfo_from_remote: failed! len = %s"%(len(OVPN_ACC_DATA)))
                        return False
                else:
                    self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
                    self.debug(1,"def load_accinfo_from_remote: AUTH ERROR")
                    self.msgwarn(_("Invalid User-ID or API-Key or Account expired!"),_("Error"))
                    return False
            except Exception as e:
                self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
                self.debug(1,"def load_accinfo_from_remote: json decode error")
                return False
        except Exception as e:
            self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
            self.debug(1,"def load_accinfo_from_remote: api request failed, exception = '%s'"%(e))
            return False

    """ *fixme* move to openvpn.py """
    def upgrade_openvpn(self):
        self.debug(1,"def upgrade_openvpn()")
        if self.load_openvpnbin_from_remote():
            print("debug 4.1.1")
            return self.win_install_openvpn()

    """ *fixme* move to openvpn.py """
    def load_openvpnbin_from_remote(self):
        self.debug(1,"def load_openvpnbin_from_remote()")
        self.OPENVPN_SAVE_BIN_TO = "%s\\%s" % (self.VPN_DIR,openvpn.values(DEBUG)["SETUP_FILENAME"])
        self.OPENVPN_ASC_FILE = "%s.asc" % (self.OPENVPN_SAVE_BIN_TO)
        if os.path.isfile(self.OPENVPN_SAVE_BIN_TO):
            print("debug 4.1.2")
            return self.verify_openvpnbin_dl()
        else:
            if self.check_inet_connection() == False:
                self.msgwarn(_("Failed to download openVPN Update!\n\nPlease install manually:\n'%s'")%(openvpn.values(DEBUG)["OPENVPN_DL_URL"]),_("Error"))
                return False

            self.tray.set_tooltip_markup(_("%s - Downloading openVPN (1.8 MB)") % (CLIENT_STRING))
            try:
                HEADERS = request_api.useragent(self.DEBUG)
                r1 = requests.get(openvpn.values(DEBUG)["OPENVPN_DL_URL"],headers=HEADERS)
                if len(r1.content) == openvpn.values(self.DEBUG)["F_SIZES"][self.ARCH]:
                    fp1 = open(self.OPENVPN_SAVE_BIN_TO, "wb")
                    fp1.write(r1.content)
                    fp1.close()
                    ascfile = "%s.asc" % (openvpn.values(DEBUG)["OPENVPN_DL_URL"])
                    if os.path.isfile(ascfile):
                        os.remove(ascfile)
                    HEADERS = request_api.useragent(self.DEBUG)
                    r2 = requests.get(ascfile,headers=HEADERS)
                    fp2 = open(self.OPENVPN_ASC_FILE, "wb")
                    fp2.write(r2.content)
                    fp2.close()
                else:
                    self.debug(1,"Invalid filesize len(r1.content) = '%s' but !== self.OPENVPN_FILESIZE"%(len(r1.content)))
                return self.verify_openvpnbin_dl()
            except Exception as e:
                self.msgwarn(_("Failed to download openVPN Update!\n\nPlease install manually:\n'%s'")%(openvpn.values(DEBUG)["OPENVPN_DL_URL"]),_("Error"))
                self.debug(1,"def load_openvpnbin_from_remote: failed, exception = '%s'"%(e))
                return False

    """ *fixme* move to openvpn.py """
    def verify_openvpnbin_dl(self):
        self.debug(1,"def verify_openvpnbin_dl()")
        if os.path.isfile(self.OPENVPN_SAVE_BIN_TO):
            localhash = hashings.hash_sha512_file(self.DEBUG,self.OPENVPN_SAVE_BIN_TO)
            storehash = openvpn.values(DEBUG)["SHA_512"][self.ARCH]
            if storehash == localhash:
                self.debug(1,"def verify_openvpnbin_dl: file = '%s' localhash = '%s' OK" % (self.OPENVPN_SAVE_BIN_TO,localhash))
                return True
            else:
                self.msgwarn(_("Invalid File hash: %s !\nlocalhash = '%s'\nbut should be = '%s'") % (self.OPENVPN_SAVE_BIN_TO,localhash,self.OPENVPN_FILEHASH),_("Error"))
                try:
                    os.remove(self.OPENVPN_SAVE_BIN_TO)
                except Exception as e:
                    self.msgwarn(_("Failed remove file: %s") % (self.OPENVPN_SAVE_BIN_TO),_("Error"))
                self.tray.set_tooltip_markup(_("%s - Verify openVPN failed!") % (CLIENT_STRING))
                return False
        else:
            return False

    """ *fixme* move to openvpn.py """
    def win_install_openvpn(self):
        self.debug(1,"def win_install_openvpn()")
        self.tray.set_tooltip_markup(_("%s - Install openVPN") % (CLIENT_STRING))
        if self.OPENVPN_SILENT_SETUP == True:
            # silent install
            installtodir = "%s\\runtime" % (self.VPN_DIR)
            options = "/S /SELECT_SHORTCUTS=0 /SELECT_OPENVPN=1 /SELECT_SERVICE=0 /SELECT_TAP=1 /SELECT_OPENVPNGUI=0 /SELECT_ASSOCIATIONS=0 /SELECT_OPENSSL_UTILITIES=0 /SELECT_EASYRSA=0 /SELECT_PATH=1"
            parameters = '%s /D=%s' % (options,installtodir)
            netshcmd = '"%s" %s' % (self.OPENVPN_SAVE_BIN_TO,parameters)
            self.debug(1,"def win_install_openvpn: silent cmd =\n'%s'" % (netshcmd))
            self.OPENVPN_DIR = installtodir
        else:
            # popup install
            netshcmd = '"%s"' % (self.OPENVPN_SAVE_BIN_TO)
        self.debug(1,"def win_install_openvpn: '%s'" % (self.OPENVPN_SAVE_BIN_TO))
        try: 
            exitcode = subprocess.call(netshcmd,shell=True)
            if exitcode == 0:
                if self.OPENVPN_SILENT_SETUP == True:
                    self.debug(1,"def win_install_openvpn: silent OK!")
                else:
                    self.debug(1,"def win_install_openvpn:\n\n'%s'\n\nexitcode = %s" % (netshcmd,exitcode))
                return True
            else:
                self.debug(1,"def win_install_openvpn: '%s' exitcode = %s" % (netshcmd,exitcode))
                return False
        except Exception as e:
            self.debug(1,"def win_install_openvpn: '%s' failed" % (netshcmd))
            return False

    """ *fixme* move to openvpn.py """
    def win_dialog_select_openvpn(self):
        self.debug(1,"def win_dialog_select_openvpn()")
        self.msgwarn(_("OpenVPN not found!\n\nPlease select openvpn.exe on next window!\n\nIf you did not install openVPN yet: click cancel on next window!"),_("Setup: openVPN"))
        dialogWindow = Gtk.FileChooserDialog(_("Select openvpn.exe or Cancel to install openVPN"),None,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialogWindow.set_position(Gtk.WindowPosition.CENTER)
        dialogWindow.set_default_response(Gtk.ResponseType.OK)
        filter = Gtk.FileFilter()
        filter.set_name("openvpn.exe")
        filter.add_pattern("openvpn.exe")
        dialogWindow.add_filter(filter)
        try:
            response = dialogWindow.run()
            if response == Gtk.ResponseType.OK:
                self.OPENVPN_EXE = dialogWindow.get_filename()
                dialogWindow.destroy()
                self.debug(1,"def win_dialog_select_openvpn: selected = '%s'" % (self.OPENVPN_EXE))
                return True
            else:
                dialogWindow.destroy()
                self.debug(1,"def win_dialog_select_openvpn: Closed, no files selected")
                return False
        except Exception as e:
            self.debug(1,"def win_dialog_select_openvpn: response failed, exception = '%s'"%(e))
            return False

    def win_detect_openvpn(self):
        try:
            print("debug 1")
            values = openvpn.win_detect_openvpn(self.DEBUG,self.OPENVPN_EXE)
            print("debug 2")
            if not values == False:
                print("debug 3")
                self.OPENVPN_DIR = values["OPENVPN_DIR"]
                self.OPENVPN_EXE = values["OPENVPN_EXE"]
                self.debug(1,"def win_detect_openvpn: DIR = '%s', EXE = '%s'"%(self.OPENVPN_DIR,self.OPENVPN_EXE))
                
                if openvpn.check_files(self.DEBUG,self.OPENVPN_DIR) == True:
                    if openvpn.win_detect_openvpn_version(self.DEBUG,self.OPENVPN_DIR) == True:
                        return True
            else:
                if self.win_dialog_select_openvpn() == True:
                    if self.win_detect_openvpn == True:
                        return True
            print("debug 4")
            if self.upgrade_openvpn() == True:
                print("debug 4.1")
                if self.win_detect_openvpn() == True:
                    print("debug 4.2")
                    return True
                print("debug 4.3")
            else:
                if self.verify_openvpnbin_dl() == True:
                    self.msgwarn(_("openVPN Setup downloaded and hash verified OK!\n\nPlease start setup from file:\n'%s'\n\nVerify GPG with:\n'%s'") % (self.OPENVPN_SAVE_BIN_TO,self.OPENVPN_ASC_FILE),_("Info"))
                else:
                    self.msgwarn(_("openVPN Setup downloaded but hash verify failed!\nPlease install openVPN!\nURL1: %s\nURL2: %s") % (openvpn.values(DEBUG)["OPENVPN_DL_URL"],openvpn.values(DEBUG)["OPENVPN_DL_URL_ALT"]),_("Error"))
            print("debug 5")
            if openvpn.check_files(self.DEBUG,self.OPENVPN_DIR) == True:
                print("debug 6")
                return True
        except Exception as e:
           self.debug(1,"def win_detect_openvpn: failed, exception = '%s'"%(e))
        return False

    def check_dns_is_whitelisted(self):
        self.debug(2,"def check_dns_is_whitelisted()")
        #if self.GATEWAY_DNS1 == "127.0.0.1" or self.GATEWAY_DNS1 == self.VAR['OVPN']['GW']['IP4'] or self.GATEWAY_DNS1 == "8.8.8.8" or self.GATEWAY_DNS1 == "8.8.4.4" or self.GATEWAY_DNS1 == "208.67.222.222" or self.GATEWAY_DNS1 == "208.67.220.220" or self.GATEWAY_DNS1 in self.d0wns_DNS:
        if self.GATEWAY_DNS1 == "127.0.0.1":
            self.debug(2,"def check_dns_is_whitelisted: True")
            return True
        else:
            self.debug(2,"def check_dns_is_whitelisted: False")
            return False

    def load_d0wns_dns(self):
        self.debug(1,"def load_d0wns_dns()")
        try:
            dnsdata = False
            dnsdata = self.d0wn_dns_entrys()
            if not dnsdata == False and len(dnsdata) > 0:
                #self.debug(76,"def load_d0wns_dns: len(dnsdata) = '%s'" % (len(dnsdata)))
                #self.debug(76,"def load_d0wns_dns: len(dnsdata) = '%s', dnsdata='%s'" % (len(dnsdata),dnsdata))
                self.d0wns_DNS = {}
                for entry in dnsdata:
                    if len(entry) > 0:
                        data = entry.split(",")
                        name = data[0]
                        ip4 = data[1]
                        ip6 = data[2]
                        country = data[3]
                        dnscryptfingerprint = data[4]
                        dnscryptcertname = data[5]
                        dnscryptports = data[6]
                        #dnscryptvalidto = data[7]
                        dnscryptpubkey = data[8]
                        active = data[12]
                        if name.endswith("any.dns.d0wn.biz") or country.lower() == "anycast":
                            self.debug(1,"def load_d0wns_dns: for continue, name '%s' invalid"%(name))
                            continue
                        if active == "1" and self.check_d0wns_names(name) == True and self.isValueIPv4(ip4) == True and self.check_d0wns_dnscountry(country) == True and self.check_d0wns_dnscryptfingerprint(dnscryptfingerprint) == True and self.check_d0wns_names(dnscryptcertname) == True and self.check_d0wns_dnscryptports(dnscryptports) == True:
                            self.d0wns_DNS[name].update({"ip4":ip4,"ip6":ip6,"country":country,"dnscryptfingerprint":dnscryptfingerprint,"dnscryptcertname":dnscryptcertname,"dnscryptports":dnscryptports,"dnscryptpubkey":dnscryptpubkey})
                        elif active == "0":
                            self.debug(1,"def load_d0wns_dns: offline '%s'" % (name))
                        else:
                            self.debug(1,"def load_d0wns_dns: failed '%s'" % (data))
                #self.debug(1,"def load_d0wns_dns: True len(self.d0wns_DNS) = %s" % (len(self.d0wns_DNS)))
                self.debug(0,"def load_d0wns_dns: len(self.d0wns_DNS) = '%s'\n#\n#self.d0wns_DNS = %s\n#" % (len(self.d0wns_DNS),self.d0wns_DNS))
                self.debug(1,"def load_d0wns_dns: len(self.d0wns_DNS)= '%s' content written to DEBUGLOG" % (len(self.d0wns_DNS)))
                return True
        except Exception as e:
            self.debug(1,"def load_d0wns_dns: failed, exception = '%s'"%(e))

    def d0wn_dns_entrys(self):
        dnsdata = False
        if D0WNDNS == True:
            if not os.path.isfile(self.dns_d0wntxt):
                if not self.load_d0wns_dns_from_remote():
                    self.debug(1,"def d0wn_dns_entrys: self.load_d0wns_dns_from_remote() failed!")
            if os.path.isfile(self.dns_d0wntxt):
                self.debug(1,"self.d0wn_dns_entrys() DEVMODE")
                fp = open(self.dns_d0wntxt,'rt')
                dnsdata = fp.read().splitlines()
                fp.close()
            else:
                self.debug(1,"def d0wn_dns_entrys: self.dns_d0wntxt = '%s' not found"%(self.dns_d0wntxt))
        return dnsdata

    def check_d0wns_dnscryptports(self,value):
        self.debug(59,"def check_d0wns_dnscryptports()")
        try:
            data = value.split()
            for entry in data:
                entry = int(entry)
                if entry > 0 and entry <= 65535:
                    pass
                else:
                    self.debug(1,"def check_d0wns_dnscryptports: failed value '%s'" % (value))
                    return False
            return True
        except Exception as e:
            return False

    def check_d0wns_names(self,name):
        self.debug(59,"def check_d0wns_names()")
        try:
            data = name.split('.')
            self.debug(59,"def check_d0wns_names: data = '%s' len(data)='%s'" % (data,len(data)))
            if len(data) == 5:
                if data[0].startswith("ns") and data[0].isalnum() and data[1].isalnum() and data[2].isalnum() and data[3].isalnum() and data[4].isalnum():
                    self.d0wns_DNS[name] = {"countrycode":data[1]}
                    return True
                elif data[0] == "2" and data[1] == "dnscrypt-cert" and data[2].isalnum() and data[3].isalnum() and data[4].isalnum():
                    return True
                else:
                    self.debug(1,"def check_d0wns_names: name failed value '%s'" % (name))
        except Exception as e:
            return False

    def check_d0wns_dnscountry(self,value):
        self.debug(59,"def check_d0wns_dnscountry()")
        try:
            if not value.isalnum():
                data = value.split()
                for entry in data:
                    if not entry.isalnum():
                        self.debug(1,"def check_d0wns_dnscountry: '%s' failed" % (value))
                        return False
            return True
        except Exception as e:
            return False

    def check_d0wns_dnscryptfingerprint(self,value):
        self.debug(59,"def check_d0wns_dnscryptfingerprint()")
        try:
            if len(value) == 79:
                for toc in value.split(':'):
                    if not len(toc) == 4 or not toc.isalnum():
                        self.debug(1,"def check_d0wns_dnscryptfingerprint: value = '%s' toc '%s'"%(value,toc))
                        return False
                self.debug(59,"def check_d0wns_dnscryptfingerprint: True")
                return True
            else:
                self.debug(1,"def check_d0wns_dnscryptfingerprint: len value = %s" % (len(value)))
        except Exception as e:
            return False

    def load_d0wns_dns_from_remote(self):
        if D0WNDNS == True:
            self.debug(1,"def load_d0wns_dns_from_remote()")
            try:
                if os.path.isfile(self.dns_d0wntxt):
                    os.remove(self.dns_d0wntxt)
                if not os.path.isfile(self.dns_d0wntxt):
                    try:
                        url = "https://%s/files/dns/d0wns_dns.static.txt" % (VCP_DOMAIN)
                        HEADERS = request_api.useragent(self.DEBUG)
                        r = requests.get(url,headers=HEADERS)
                        fp = open(self.dns_d0wntxt,'wb')
                        fp.write(r.content)
                        fp.close()
                        self.debug(1,"def load_d0wns_dns_from_remote: True")
                        return True
                    except Exception as e:
                        debug(1,"def load_d0wns_dns_from_remote: failed #2, exception = '%s'"%(e))
                        return False
                else:
                    return True
            except Exception as e:
                debug(1,"def load_d0wns_dns_from_remote: failed #1, exception = '%s'"%(e))
                return False

    def show_about_dialog(self,widget,event):
        self.debug(1,"def show_about_dialog()")
        self.destroy_systray_menu()
        if self.WINDOW_ABOUT_OPEN == True:
            self.about_dialog.destroy()
            return True
        try:
            self.WINDOW_ABOUT_OPEN = True
            self.about_dialog = Gtk.AboutDialog()
            self.about_dialog.set_position(Gtk.WindowPosition.CENTER)
            try:
                self.about_dialog.set_icon(self.app_icon)
            except Exception as e:
                pass
            self.about_dialog.set_logo(self.app_icon)
            self.about_dialog.set_program_name(release_version.version_data()["NAME"])
            # *** Dont work on Windows atm ***
            #self.about_dialog.set_website(release_version.org_data()["SITE"])
            self.about_dialog.set_website_label(release_version.org_data()["ORG"])
            self.about_dialog.set_transient_for(self.window)
            self.about_dialog.set_destroy_with_parent (True)
            self.about_dialog.set_name(release_version.org_data()["ORG"])
            self.about_dialog.set_version(BUILT_STRING)
            self.about_dialog.set_copyright(release_version.setup_data()["copyright"])
            self.about_dialog.set_comments((ABOUT_TEXT))
            self.about_dialog.set_authors(["%s [ %s ]"%(release_version.org_data()["ORG"],release_version.org_data()["EMAIL"])])
            response = self.about_dialog.run()
            self.about_dialog.destroy()
            if not response == None:
                self.debug(1,"def show_about_dialog: response = '%s'" % (response))
                self.WINDOW_ABOUT_OPEN = False
        except Exception as e:
            self.debug(1,"def show_about_dialog: failed, exception = '%s'"%(e))

    def on_closing(self,widget,event):
        self.debug(1,"def on_closing()")
        self.destroy_systray_menu()
        if self.WINDOW_QUIT_OPEN == True:
            self.QUIT_DIALOG.destroy()
            return False
        self.WINDOW_QUIT_OPEN = True
        if self.state_openvpn() == True:
            return False
        else:
            try: 
                self.about_dialog.destroy()
                self.WINDOW_ABOUT_OPEN = False
            except Exception as e:
                pass
            try:
                self.dialogWindow_form_ask_passphrase.destroy()
            except Exception as e:
                pass
            try:
                self.destroy_mainwindow()
            except Exception as e:
                pass
            try:
                self.destroy_accwindow()
            except Exception as e:
                pass
            try:
                self.destroy_settingswindow()
            except Exception as e:
                pass
            try:
                dialog = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.set_title(_("Quit oVPN.to Client"))
                try:
                    dialog.set_icon(self.app_icon)
                except Exception as e:
                    pass
                dialog.set_transient_for(self.window)
                dialog.set_border_width(8)
                self.QUIT_DIALOG = dialog
                dialog.set_markup(_("Do you really want to quit?"))
                response = dialog.run()
                dialog.destroy()
                if response == Gtk.ResponseType.NO:
                    self.WINDOW_QUIT_OPEN = False
                    return False
                elif response == Gtk.ResponseType.YES:
                    if self.ask_loadorunload_fw() == False:
                        dialog.destroy()
                        self.WINDOW_QUIT_OPEN = False
                        return False
                    dialog.destroy()
                else:
                    dialog.destroy()
                    self.WINDOW_QUIT_OPEN = False
                    return False
            except Exception as e:
                pass
            if self.TAP_BLOCKOUTBOUND == True:
                self.win_firewall_whitelist_ovpn_on_tap(option="delete")
            if self.WIN_FIREWALL_ADDED_RULE_TO_VCP == True:
                self.win_firewall_clear_vcp_rules()
            self.debug(1,"close app")
            self.stop_systray_timer = True
            self.remove_lock()
            Gtk.main_quit()
            sys.exit()

    def ask_loadorunload_fw(self):
        self.debug(1,"def ask_loadorunload_fw()")
        if self.NO_WIN_FIREWALL == True:
            return True
        try:
            if self.WIN_DONT_ASK_FW_EXIT == True:
                self.win_enable_ext_interface()
                if self.WIN_BACKUP_FIREWALL == True and self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == True:
                    self.win_firewall_restore_on_exit()
                    self.win_firewall_block_on_exit()
                    #self.win_netsh_restore_dns()
                    self.debug(1,"Firewall rules restored and block outbound!")
                    return True
                elif self.WIN_BACKUP_FIREWALL == True and self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == False:
                    self.win_firewall_restore_on_exit()
                    #self.win_netsh_restore_dns()
                    self.debug(1,"Firewall: rules restored!")
                    return True
                elif self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == True:
                    self.win_firewall_block_on_exit()
                    #self.win_netsh_restore_dns()
                    self.debug(1,"Firewall: block outbound!")
                    return True
                elif self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == False:
                    self.win_firewall_allowout()
                    #self.win_netsh_restore_dns()
                    self.debug(1,"Firewall: allow outbound!")
                    return True
            else:
                try:
                    self.dialog_ask_loadorunload_fw.destroy()
                except Exception as e:
                    pass
                try:
                    dialog = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
                    self.dialog_ask_loadorunload_fw = dialog
                    dialog.set_position(Gtk.WindowPosition.CENTER)
                    dialog.set_title(_("Firewall Settings"))
                    try:
                        dialog.set_icon(self.app_icon)
                    except Exception as e:
                        pass
                    dialog.set_transient_for(self.window)
                    dialog.set_border_width(8)
                    if self.WIN_BACKUP_FIREWALL == True:
                        text = _("Restore previous firewall settings?\n\nPress 'YES' to restore your previous firewall settings!\nPress 'NO' to set profiles to 'blockinbound,blockoutbound'!")
                    else:
                        text = _("Allow outgoing connection to internet?\n\nPress 'YES' to set profiles to 'blockinbound,allowoutbound'!\nPress 'NO' to set profiles to 'blockinbound,blockoutbound'!")
                    dialog.set_markup(text)
                    self.debug(1,"def ask_loadorunload_fw: text = '%s'" % (text))
                    response = dialog.run()
                    self.debug(1,"def ask_loadorunload_fw: dialog response = '%s'" % (response))
                    if response == Gtk.ResponseType.NO:
                        dialog.destroy()
                        self.debug(1,"def ask_loadorunload_fw: dialog response = NO '%s'" % (response))
                        self.win_firewall_block_on_exit()
                        #self.win_netsh_restore_dns()
                        return True
                    elif response == Gtk.ResponseType.YES:
                        dialog.destroy()
                        self.debug(1,"def ask_loadorunload_fw: dialog response = YES '%s'" % (response))
                        if self.WIN_BACKUP_FIREWALL == True:
                            self.win_firewall_restore_on_exit()
                        else:
                            self.win_firewall_allowout()
                        #self.win_netsh_restore_dns()
                        return True
                    else:
                        dialog.destroy()
                        self.debug(1,"def ask_loadorunload_fw: dialog response = ELSE '%s'" % (response))
                        return False
                except Exception as e:
                    self.debug(1,"def ask_loadorunload_fw: dialog failed, exception = '%s'"%(e))
                    return False
        except Exception as e:
            self.debug(1,"def ask_loadorunload_fw: failed, exception = '%s'"%(e))
            return False

    def remove_lock(self):
        self.debug(1,"def remove_lock()")
        try:
            LOCKFILE = self.lock_file
        except Exception as e:
            return True
        if os.path.isfile(LOCKFILE):
            self.LOCK.close()
            self.debug(1,"def remove_lock: self.LOCK.close()")
            try:
                os.remove(LOCKFILE)
                self.debug(1,"def remove_lock: os.remove(LOCKFILE)")
                return True
            except Exception as e:
                self.debug(1,"def remove_lock: remove lock failed!")
                return False
        else:
            self.debug(1,"def remove_lock: lock not found!")
            return False

    def errorquit(self,text):
        if self.DEBUG == False:
            self.DEBUG = True
        self.debug(1,"errorquit: %s" % (text))
        try:
            message = Gtk.MessageDialog(type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK)
            message.set_position(Gtk.WindowPosition.CENTER)
            message.set_title(_("Error"))
            message.set_border_width(8)
            try:
                message.set_icon(self.app_icon)
            except Exception as e:
                pass
            message.set_markup("%s"%(text))
            message.run()
            message.destroy()
        except Exception as e:
            self.debug(1,"%s failed" % (text))
        sys.exit()

    def init_theme(self):
        get_settings = Gtk.Settings.get_default()
        get_settings.set_property("gtk-theme-name", self.APP_THEME)
        get_settings.set_property("gtk-font-name", self.APP_FONT_SIZE)
        return True

    def init_localization(self,LANG):
        try:
            if not LANG == None:
                loc = LANG
                os.environ['LANGUAGE'] = loc
                os.environ['LANG'] = loc
                os.putenv(loc, 'LANG')
            else:
                try:
                    loc = locale.getdefaultlocale()[0][0:2]
                    self.debug(1,"def init_localization: OS LANGUAGE %s"% (loc))
                except Exception as e:
                    self.debug(1,"def init_localization: locale.getdefaultlocale() failed, exception = '%s'"%(e))
                    loc = False
            
            filename1 = "%s\\locale\\%s\\ovpn_client.mo" % (os.getcwd(),loc)
            filename2 = "%s\\locale\\%s\\ovpn_client.mo" % (DEV_DIR,loc)
            
            if not loc == "en" and os.path.isfile(filename1):
                filename = filename1
            elif not loc == "en" and os.path.isfile(filename2):
                filename = filename2
            else:
                filename = False
            self.debug(1,"def init_localization: filename = '%s'"% (filename))
            translation = False
            try:
                if not filename == False:
                    translation = gettext.GNUTranslations(open(filename, "rb"))
            except Exception as e:
                self.debug(1,"def init_localization: %s not found, fallback to en"% (filename))
            if translation == False or filename == False:
                translation = gettext.NullTranslations()
            try:
                translation.install()
            except Exception as e:
                self.debug(1,"def init_localization: translation.install() failed, exception = '%s'"%(e))
                return False
            self.APP_LANGUAGE = loc
            self.debug(1,"def init_localization: return self.APP_LANGUAGE = '%s'"% (self.APP_LANGUAGE))
            return True
        except Exception as e:
            self.debug(1,"def init_localization: failed, exception = '%s'"%(e))

    def msgwarn(self,text,title):
        if self.DISABLE_ALL_NOTIFICATIONS == True:
            self.debug(1,"def msgwarn('%s','%s')"%(text,title))
            return True

        if WIN_NOTIFY == False or self.WIN_ENABLE_NOTIFICATIONS == False:
            GLib.idle_add(self.msgwarn_glib,text,title)
        else:
            self.send_notify(text,title)

    def send_notify(self,text,title):
        self.debug(1,"def send_notify('%s','%s')"%(text,title))
        if self.DISABLE_ALL_NOTIFICATIONS == True or self.WIN_ENABLE_NOTIFICATIONS == False:
            return True
        try:
            notethread = threading.Thread(target=lambda text=text,title=title: self.send_notify_glib(text,title))
            notethread.daemon = True
            notethread.start()
        except Exception as e:
            self.debug(1,"def send_notify: failed, exception = '%s'"%(e))

    def send_notify_glib(self,text,title):
        try:
            self.notification.send_notify(self.DEBUG,DEV_DIR,text,title)
        except Exception as e:
            self.debug(1,"def send_notify_glib: failed, exception = '%s'"%(e))

    def msgwarn_glib(self,text,title):
        self.debug(1,"def msgwarn: %s"% (text))
        if self.MSGWARN_WINDOW_OPEN == True:
            try:
                self.msgwarn_window.destroy()
            except Exception as e:
                self.debug(1,"def msgwarn_glib: failed #1, exception = '%s'"%(e))
                return False
        try:
            self.MSGWARN_WINDOW_OPEN = True
            self.LAST_MSGWARN_WINDOW = int(time.time())
            self.msgwarn_window = Gtk.MessageDialog(type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK)
            self.msgwarn_window.connect("key_release_event", lambda w, e: GLib.idle_add(self.msgwarn_window.destroy) if e.keyval == 65307 else None)
            self.msgwarn_window.set_position(Gtk.WindowPosition.CENTER)
            self.msgwarn_window.set_title(title)
            self.msgwarn_window.set_transient_for(self.window)
            self.msgwarn_window.set_border_width(8)
            self.msgwarn_window.set_markup("%s"%(text))
            try:
                self.msgwarn_window.set_icon(self.app_icon)
            except Exception as e:
                pass
            self.msgwarn_window.run()
            self.msgwarn_window.destroy()
        except Exception as e:
            self.debug(1,"def msgwarn_glib: failed #2, exception = '%s'"%(e))

    def decode_icon(self,icon):
        #self.debug(49,"def decode_icon()")
        try:
            try:
                imgpixbuf = self.ICON_CACHE_PIXBUF[icon]
                if isinstance(imgpixbuf, GdkPixbuf.Pixbuf):
                    self.debug(49,"def decode_icon: isinstance self.ICON_CACHE_PIXBUF[%s]"%(icon))
                    return imgpixbuf
            except Exception as e:
                try:
                    self.debug(49,"def decode_icon(%s)" % (icon))
                    base64_data = base64.b64decode(self.base64_icons(icon))
                    base64_stream = Gio.MemoryInputStream.new_from_data(base64_data)
                    imgpixbuf = GdkPixbuf.Pixbuf.new_from_stream(base64_stream)
                    self.ICON_CACHE_PIXBUF[icon] = imgpixbuf
                    return imgpixbuf
                except Exception as e:
                    return False
        except Exception as e:
            self.debug(1,"def decode_icon: '%s' failed"%(icon))

    def decode_flag(self,flag):
        #self.debug(48,"def decode_flag()")
        try:
            flag = flag.lower()
            try:
                imgpixbuf = self.FLAG_CACHE_PIXBUF[flag]
                if isinstance(imgpixbuf, GdkPixbuf.Pixbuf):
                    self.debug(48,"def decode_flag: isinstance self.FLAG_CACHE_PIXBUF[%s] return"%(flag))
                    return imgpixbuf
            except Exception as e:
                try:
                    self.debug(48,"def decode_flag(%s)" % (flag))
                    flagfile = "%s.png" % (flag)
                    base64_flag = self.FLAGS_B64[flagfile]
                except Exception as e:
                    base64_flag = self.FLAGS_B64["00.png"]
                base64_data = base64.b64decode(base64_flag)
                base64_stream = Gio.MemoryInputStream.new_from_data(base64_data)
                imgpixbuf = GdkPixbuf.Pixbuf.new_from_stream(base64_stream)
                self.FLAG_CACHE_PIXBUF[flag] = imgpixbuf
                return imgpixbuf
        except Exception as e:
            self.debug(1,"def decode_flag: '%s' failed"%(flag))

    def base64_icons(self, icon):
        self.debug(2,"def base64_icons(%s)"%(icon))
        return icons_b64.base64_icons(icon)

    def delete_file(self,file,sourcef):
        try:
            if not file == False:
                if os.path.isfile(file):
                    os.remove(file)
                if not os.path.isfile(file):
                    return True
            return False
        except Exception as e:
            self.debug(1,"def delete_file: file = '%s', sourcef = '%s', failed, exception = '%s'"%(file,sourcef,e))

    def debug(self,level,text):
        #print("def debug()")
        try:
            istrue = self.DEBUG
        except Exception as e:
            istrue = False
        
        try:
            bindir = self.BIN_DIR
        except Exception as e:
            bindir = False
        CDEBUG(level,text,istrue,bindir)
        
        if self.DEBUGWINDOW_OPEN == True:
            cache = debug.debug_cache(False,'get')
            cachesize = len(cache)
            if not cachesize == self.DEBUGCACHESIZE:
                newbuffer = "%s\n" % datetime.fromtimestamp(int(time.time())).strftime('%d %b %Y %H:%M:%S')
                for entry in cache[::-1]:
                    newbuffer = "%s\n%s" % (newbuffer,entry)
                GLib.idle_add(self.debug_textbuffer.set_text,newbuffer)
            self.DEBUGCACHESIZE = cachesize
        return

    def show_debug_window(self):
        self.debug(1,"def show_debug_window()")
        try:
            if self.DEBUGWINDOW_OPEN == False:
                self.debug_window = Gtk.Window(title="DEBUG")
                self.debug_window.set_position(Gtk.WindowPosition.CENTER)
                self.debug_window.set_title("DEBUG")
                try:
                    self.debug_window.set_icon(self.app_icon)
                except Exception as e:
                    pass
                self.debug_window.set_default_size(700, 700)
                self.debug_window.connect("destroy",self.cb_destroy_debugwindow)
                self.debug_window.connect("key_release_event", lambda w, e: GLib.idle_add(self.debug_window.destroy) if e.keyval == 65307 else None)
                self.debug_grid = Gtk.Grid()
                self.debug_window.add(self.debug_grid)
                self.debug_create_textview()
                GLib.idle_add(self.debug_window.show_all)
                self.DEBUGWINDOW_OPEN = True
            else:
                self.destroy_debugwindow()
        except Exception as e:
            self.debug(1,"def show_debug_window: failed, exception = '%s'"%(e))

    def debug_create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.debug_grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.debug_textview = Gtk.TextView()
        self.debug_textview.set_editable(False)
        self.debug_textbuffer = self.debug_textview.get_buffer()
        self.debug_textbuffer.set_text("DEBUG")
        scrolledwindow.add(self.debug_textview)


def app():
    Systray()
    Gtk.main()

if __name__ == "__main__":
    app()
