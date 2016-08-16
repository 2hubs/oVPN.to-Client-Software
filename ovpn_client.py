# -*- coding: utf-8 -*-



import sys
import debug
DEVMODE = debug.devmode()
if DEVMODE == True:
	DEBUG = True
else:
	DEBUG = False
DEV_DIR=debug.devdir()

try:
	import patches
	patches.select_gtkdll(DEBUG)
except:
	sys.exit()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GObject, Gio
from datetime import datetime as datetime
import os, base64, gettext, locale, types, platform, hashlib, random, time, zipfile, subprocess, threading, socket, requests, json, struct, string
from ConfigParser import SafeConfigParser
# .py files imports

import winregs
import icons_b64
import schedule_task
import release_version
import openvpn
import signtool
import hashings



def CDEBUG(level,text,istrue,bindir):
	debug.debug(level,text,istrue,bindir)

try:
	
	CLIENTVERSION = "%s" % (release_version.version_data()["VERSION"])
	CLIENT_STRING = "%s %s" % (release_version.version_data()["NAME"],CLIENTVERSION)
	VCP_DOMAIN = release_version.org_data()["VCP_DOMAIN"]
	API_DOMAIN = release_version.org_data()["API_DOMAIN"]
	API_URL = "https://%s:%s/%s" % (API_DOMAIN,release_version.org_data()["API_PORT"],release_version.org_data()["API_POST"])
	print CLIENTVERSION
	print CLIENT_STRING
	print API_URL
	
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
	except: 
		BUILT_STRING = "(UNDEFINED)"
	print BUILT_STRING

	if DEVMODE == True:
		print "DEVMODE sleep 15"
		time.sleep(15)
except:
	print "import release_version failed"
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
		self.self_vars()
		self.tray = Gtk.StatusIcon()
		self.tray.is_embedded()
		traysize = self.tray.get_size()
		self.debug(1,"TrayIcon Output Size: %s pixel" % (traysize))
		self.tray.connect('size-changed', self.statusicon_size_changed)
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
						self.check_remote_update()
				else:
					self.msgwarn(_("Could not connect to %s") % (API_DOMAIN),_("Update failed!"))
			thread = threading.Thread(target=self.systray_timer)
			thread.daemon = True
			thread.start()
			self.win_firewall_analyze()
		else:
			sys.exit()

	def self_vars(self):
		self.DEBUG = DEBUG
		self.DEVMODE = DEVMODE
		self.OS = sys.platform
		self.ARCH = openvpn.values(self.DEBUG)["ARCH"]
		self.APIURL = API_URL
		self.MOUSELEVEL = False
		self.INIT_FIRST_UPDATE = True
		self.SAVE_APIKEY_INFILE = False
		self.MAINWINDOW_OPEN = False
		self.MAINWINDOW_HIDE = False
		self.MAINWINDOW_ALLOWCELLHIDE = [ 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26 ]
		self.MAINWINDOW_SHOWCELLS = self.MAINWINDOW_ALLOWCELLHIDE
		self.MAINWINDOW_CELLINDEX = { 2:"Server", 3:"IPv4", 4:"IPv6", 5:"Port", 6:"Proto", 7:"MTU", 8:"Cipher",
									9:"Live", 10:"Link", 11:"VLAN IPv4", 12:"VLAN IPv6", 13:"CPU", 14:"RAM", 15:"HDD", 
									16:"Traffic", 17:"Load", 18:"oVPN %", 19:"oSSH %", 20:"SOCK %", 21:"HTTP %", 
									22:"TINC %", 23:"PING4", 24:"PING6", 25:"SVR", 26:"Right Flag" }
		self.HIDECELLSWINDOW_OPEN = False
		self.SETTINGSWINDOW_OPEN = False
		self.APP_LANGUAGE = "en"
		self.LANG_FONT_CHANGE = False
		self.APP_FONT_SIZE = "9"
		self.APP_FONT_SIZE_AVAIABLE = [ "6", "7", "8", "9", "10", "11", "12", "13" ]
		self.APP_THEME = "Adwaita"
		self.INSTALLED_THEMES = [ "ms-windows", "Adwaita", "Adwaita-dark", "Greybird", "Flat-Remix-OS" ]
		self.ICONS_THEME = "standard"
		self.ICONS_THEME_frombefore = self.ICONS_THEME
		self.INSTALLED_ICONS = [ "standard", "classic", "classic2", "shield_bluesync", "experimental", "private" ]
		self.INSTALLED_LANGUAGES = [ "en", "de", "es" ]
		self.ACCWINDOW_OPEN = False
		self.DEBUG_LOGFILE = False
		self.timer_load_remote_data_running = False
		self.timer_ovpn_ping_running = False
		self.timer_check_certdl_running = False
		self.statusbartext_from_before = False
		self.statusbar_text = False
		self.systraytext_from_before = False
		self.systrayicon_from_before = False
		self.stop_systray_timer = False
		self.stop_systray_timer2 = False
		self.systray_timer_running = False
		self.systray_timer2_running = False
		self.inThread_jump_server_running = False
		self.USERID = False
		self.STATE_OVPN = False
		self.STATE_CERTDL = False
		self.LAST_CFG_UPDATE = 0
		self.LAST_CHECK_MYIP = 0
		self.NEXT_PING_EXEC = 0
		self.LAST_CHECK_INET_FALSE = 0
		self.LAST_MSGWARN_WINDOW = 0
		self.GATEWAY_LOCAL = False
		self.GATEWAY_DNS1 = False
		self.GATEWAY_DNS2 = False
		self.WIN_TAP_DEVICE = False
		self.WIN_TAP_DEVS = list()
		self.TAP_BLOCKOUTBOUND = False
		self.win_firewall_tap_blockoutbound_running = False
		self.WIN_EXT_DEVICE = False
		self.WIN_EXT_DHCP_DNS = False
		self.NO_WIN_FIREWALL = False
		self.NO_DNS_CHANGE = False
		self.MYDNS = {}
		self.NETSH_CMDLIST = list()
		self.ROUTE_CMDLIST = list()
		self.API_DIR = False
		self.OPENVPN_EXE = False
		self.OPENVPN_SILENT_SETUP = False
		
		self.OVPN_SERVER = list()
		self.OVPN_FAV_SERVER = False
		self.OVPN_AUTO_CONNECT_ON_START = False
		self.OVPN_CALL_SRV = False
		self.OVPN_CONNECTEDto = False
		self.OVPN_CONNECTEDtime = False
		self.OVPN_CONNECTEDseconds = 0
		self.OVPN_CONNECTEDtoIP = False
		self.GATEWAY_OVPN_IP4A = "172.16.32.1"
		self.GATEWAY_OVPN_IP4B = "172.16.48.1"
		self.GATEWAY_OVPN_IP4 = self.GATEWAY_OVPN_IP4A
		self.OVPN_THREADID = False
		self.OVPN_CONFIGVERSION = "23x"
		self.OPENVPN_DIR = False
		
		self.OVPN_PING = list()
		self.OVPN_isTESTING = False
		self.OVPN_PING_LAST = -1
		self.OVPN_PING_STAT = 0
		self.OVPN_PING_DEAD_COUNT = 0
		self.OVPN_PING_EVERY = "15,30"
		self.INTERFACES = False
		
		self.d0wns_DNS = {'ns1.sg.dns.d0wn.biz': {'countrycode': 'sg', 'dnscryptcertname': '2.dnscrypt-cert.sg.d0wn.biz', 'country': 'Singapore', 'dnscryptpubkey': 'pubkey.sg.dnscrypt.d0wn.biz', 'ip6': '2400:6180:0:d0::38:d001', 'ip4': '128.199.248.105', 'dnscryptports': '54 443 1053 5353 27015', 'dnscryptfingerprint': 'D82B:2B76:1DA0:8470:B55B:820C:FAAB:9F32:D632:E9E0:5616:2CE7:7D21:E970:98FF:4A34'}, 'ns1.nl.dns.d0wn.biz': {'countrycode': 'nl', 'dnscryptcertname': '2.dnscrypt-cert.nl.d0wn.biz', 'country': 'Netherlands', 'dnscryptpubkey': 'pubkey.nl.dnscrypt.d0wn.biz', 'ip6': '2a03:b0c0:0:1010::62:f001', 'ip4': '95.85.9.86', 'dnscryptports': '54 80 1053 5353 27015', 'dnscryptfingerprint': '7BE6:68FE:A505:FFA7:4C27:C2CA:F881:59DA:038C:5741:13AA:2556:A4D2:2D0B:B6F0:009E'}, 'ns1.de.dns.d0wn.biz': {'countrycode': 'de', 'dnscryptcertname': '2.dnscrypt-cert.de.d0wn.biz', 'country': 'Germany', 'dnscryptpubkey': 'pubkey.de.dnscrypt.d0wn.biz', 'ip6': '2001:1608:10:195:3:dead:beef:cafe', 'ip4': '82.211.31.248', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': 'D4A8:6FB5:AA0C:2B6B:8C13:8C29:7F69:F9C8:29C8:E157:F279:6FC7:7366:290F:2A80:0AD2'}, 'ns1.lv.dns.d0wn.biz': {'countrycode': 'lv', 'dnscryptcertname': '2.dnscrypt-cert.lv.d0wn.biz', 'country': 'Latvia', 'dnscryptpubkey': 'pubkey.lv.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '89.111.13.60', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': '1B70:FB6F:2E47:1753:91EF:1084:ECD2:983A:9018:F3E3:DDF1:E563:E528:156A:664A:1AE8'}, 'ns1.lu.dns.d0wn.biz': {'countrycode': 'lu', 'dnscryptcertname': '2.dnscrypt-cert.lu.d0wn.biz', 'country': 'Luxembourg', 'dnscryptpubkey': 'pubkey.lu.dnscrypt.d0wn.biz', 'ip6': '2605:6400:30:fbb5:0:1ce:1ce:babe', 'ip4': '104.244.72.13', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '737B:B68B:7D3C:896F:260D:91C3:60A6:AD64:8CD3:1B22:4D5F:7089:490C:539F:2EC6:C309'}, 'ns1.dk.dns.d0wn.biz': {'countrycode': 'dk', 'dnscryptcertname': '2.dnscrypt-cert.dk.d0wn.biz', 'country': 'Denmark', 'dnscryptpubkey': 'pubkey.dk.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '77.66.108.93', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '0838:C9CF:2292:2D4C:4DB7:4A5E:ED10:DD36:66DD:9551:7238:6387:B7A0:2FA0:885A:5F77'}, 'ns1.ua.dns.d0wn.biz': {'countrycode': 'ua', 'dnscryptcertname': '2.dnscrypt-cert.ua.d0wn.biz', 'country': 'Ukraine', 'dnscryptpubkey': 'pubkey.ua.dnscrypt.d0wn.biz', 'ip6': '2a02:27a8:0:2::556', 'ip4': '217.12.210.54', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '3B1E:D468:FFD3:F261:20DE:E7F1:6A74:E1D5:D59E:B40D:F3EA:99BC:0B05:70CC:292D:99BA'}, 'ns1.cz.dns.d0wn.biz': {'countrycode': 'cz', 'dnscryptcertname': '2.dnscrypt-cert.cz.d0wn.biz', 'country': 'Czech Republic', 'dnscryptpubkey': 'pubkey.cz.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '81.2.237.32', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': '4BAE:D9CE:1A99:42B2:44D1:4454:0C8C:EC0E:D5D8:90CE:0D9B:D3E3:93CF:7ACC:CCE0:3794'}, 'ns1.au.dns.d0wn.biz': {'countrycode': 'au', 'dnscryptcertname': '2.dnscrypt-cert.au.d0wn.biz', 'country': 'Australia', 'dnscryptpubkey': 'pubkey.au.dnscrypt.d0wn.biz', 'ip6': '2402:9e80:1::1:e554', 'ip4': '27.100.36.191', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': 'A7D9:0F8E:9A98:1381:176A:3D25:36DE:E865:8538:9CD8:78BC:C3B5:A146:23F1:C2EF:58D8'}, 'ns2.sg.dns.d0wn.biz': {'countrycode': 'sg', 'dnscryptcertname': '2.dnscrypt-cert.sg2.d0wn.biz', 'country': 'Singapore', 'dnscryptpubkey': 'pubkey.sg2.dnscrypt.d0wn.biz', 'ip6': '2403:5680::1:200f', 'ip4': '210.16.120.139', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '0F00:63C4:6EAF:29C3:29CD:E125:2033:6F0A:0C72:7CDD:F1F4:3D47:F95D:02BC:07F7:9FFC'}, 'ns1.bg.dns.d0wn.biz': {'countrycode': 'bg', 'dnscryptcertname': '2.dnscrypt-cert.bg.d0wn.biz', 'country': 'Bulgaria', 'dnscryptpubkey': 'pubkey.bg.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '217.12.203.133', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '423C:D823:B3EA:2015:F027:ECF1:5704:3EB7:764A:D02D:9447:56E6:51FD:D06F:E571:2FCC'}, 'ns1.us.dns.d0wn.biz': {'countrycode': 'us', 'dnscryptcertname': '2.dnscrypt-cert.us.d0wn.biz', 'country': 'United States of America', 'dnscryptpubkey': 'pubkey.us.dnscrypt.d0wn.biz', 'ip6': '2605:6400:10:59:0:b19:b00b:babe', 'ip4': '199.195.249.174', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '6741:6E7F:4744:194E:D725:91A2:1A62:A715:78F9:62CD:5263:84FC:DAA8:6C7E:4D9F:438B'}, 'ns1.ru.dns.d0wn.biz': {'countrycode': 'ru', 'dnscryptcertname': '2.dnscrypt-cert.ru.d0wn.biz', 'country': 'Russia', 'dnscryptpubkey': 'pubkey.ru.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '91.214.71.181', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '0ECA:BC40:E0A1:335F:0221:4240:AB86:2919:D16A:2393:CCEB:4B40:9EB9:4F24:3077:ED99'}, 'ns1.tz.dns.d0wn.biz': {'countrycode': 'tz', 'dnscryptcertname': '2.dnscrypt-cert.tz.d0wn.biz', 'country': 'Tanzania', 'dnscryptpubkey': 'pubkey.tz.dnscrypt.d0wn.biz', 'ip6': '2c0f:fda8:5::2ed1:d2ec', 'ip4': '41.79.69.13', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': 'B79F:A025:1AF6:2125:DF3E:3B03:856D:4CB7:704E:45EB:B850:3A7B:C6AA:5510:D87D:087D'}, 'ns1.random.dns.d0wn.biz': {'countrycode': 'random', 'dnscryptcertname': '2.dnscrypt-cert.random.d0wn.biz', 'country': 'Moldova', 'dnscryptpubkey': 'pubkey.random.dnscrypt.d0wn.biz', 'ip6': '2a00:1dc0:cafe::c6af:c19d', 'ip4': '178.17.170.133', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': 'A420:867F:ED5C:024C:C86A:EECE:AA05:194B:017F:D2FF:9E72:385A:874F:8CE5:6832:ED2E'}, 'ns2.lv.dns.d0wn.biz': {'countrycode': 'lv', 'dnscryptcertname': '2.dnscrypt-cert.lv2.d0wn.biz', 'country': 'Latvia', 'dnscryptpubkey': 'pubkey.lv.dnscrypt.d0wn.biz', 'ip6': '2a02:7aa0:1201::f60e:2719', 'ip4': '185.86.151.28', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': 'B111:F80C:E3E0:1C36:CC73:0995:009E:6351:EF08:0503:309D:9417:7AA3:8C67:916D:0CDF'}, 'ns1.se.dns.d0wn.biz': {'countrycode': 'se', 'dnscryptcertname': '2.dnscrypt-cert.se.d0wn.biz', 'country': 'Sweden', 'dnscryptpubkey': 'pubkey.se.dnscrypt.d0wn.biz', 'ip6': '2a02:7aa0:1619::4f50:a69', 'ip4': '95.215.44.124', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '9D4F:762B:DD24:F77A:64B4:7E0F:F5C6:93FD:A02A:39E9:8FEC:0CEE:F252:3A5F:A403:C032'}, 'ns2.nl.dns.d0wn.biz': {'countrycode': 'nl', 'dnscryptcertname': '2.dnscrypt-cert.nl2.d0wn.biz', 'country': 'Netherlands', 'dnscryptpubkey': 'pubkey.nl2.dnscrypt.d0wn.biz', 'ip6': '2a02:2ca0:64:22::2', 'ip4': '185.83.217.248', 'dnscryptports': '54 1053 5353 27015', 'dnscryptfingerprint': 'DFAA:B7D8:29E6:1F34:4FED:2610:4221:70C9:ADC7:7E9F:A65F:4A46:0BAE:A735:3186:3B99'}, 'ns1.cy.dns.d0wn.biz': {'countrycode': 'cy', 'dnscryptcertname': '2.dnscrypt-cert.cy.d0wn.biz', 'country': 'Cyprus', 'dnscryptpubkey': 'pubkey.cy.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '213.169.148.11', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '2144:4FE7:59C3:13B9:FABB:FC2A:F975:9F9C:CD9A:2ED7:0978:3A25:7347:4B83:8F86:EA2B'}, 'ns2.random.dns.d0wn.biz': {'countrycode': 'random', 'dnscryptcertname': '2.dnscrypt-cert.random2.d0wn.biz', 'country': 'Netherlands', 'dnscryptpubkey': 'pubkey.random2.dnscrypt.d0wn.biz', 'ip6': '2a00:1ca8:a7::1e9', 'ip4': '185.14.29.140', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': '9112:338E:7D0B:5E78:B792:9BB6:1B75:4888:AC94:65B5:B86B:B5DE:CCF3:E5B9:15A5:DC54'}, 'ns2.fr.dns.d0wn.biz': {'countrycode': 'fr', 'dnscryptcertname': '2.dnscrypt-cert.fr2.d0wn.biz', 'country': 'France', 'dnscryptpubkey': 'pubkey.fr2.dnscrypt.d0wn.biz', 'ip6': '2001:41D0:A:0028::1', 'ip4': '37.187.0.40', 'dnscryptports': '54 443 1053 5353 27015', 'dnscryptfingerprint': '25A7:DB7B:7835:55D5:7DA4:7C0C:57F8:9C5F:0220:3D09:67E3:585A:723E:E0D1:CB38:F767'}, 'ns1.uk.dns.d0wn.biz': {'countrycode': 'uk', 'dnscryptcertname': '2.dnscrypt-cert.uk.d0wn.biz', 'country': 'United Kingdom', 'dnscryptpubkey': 'pubkey.uk.dnscrypt.d0wn.biz', 'ip6': '2a04:92c7:7:7::14ae:460a', 'ip4': '185.121.25.85', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': 'FADB:BE63:7FCD:FE22:0DBE:D433:438C:5A1D:C267:1E96:4B67:1918:B15F:9121:77D7:5B2E'}, 'ns1.gr.dns.d0wn.biz': {'countrycode': 'gr', 'dnscryptcertname': '2.dnscrypt-cert.gr.d0wn.biz', 'country': 'Greece', 'dnscryptpubkey': 'pubkey.gr.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '85.25.105.193', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': 'D056:D3A4:9568:5AFE:4B0D:C688:7A75:41B2:7217:F0C9:75A5:A6C0:142D:363B:F992:9867'}, 'ns1.is.dns.d0wn.biz': {'countrycode': 'is', 'dnscryptcertname': '2.dnscrypt-cert.is.d0wn.biz', 'country': 'Iceland', 'dnscryptpubkey': 'pubkey.is.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '37.235.49.61', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': '2B28:974E:073A:6B38:722A:5BE1:F7A0:250C:508F:A809:238F:8F3D:76D8:6098:20D7:B2D9'}, 'ns1.hk.dns.d0wn.biz': {'countrycode': 'hk', 'dnscryptcertname': '2.dnscrypt-cert.hk.d0wn.biz', 'country': 'Hong Kong', 'dnscryptpubkey': 'pubkey.hk.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '45.124.66.200', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '84ED:0DFF:7967:5DBD:2D93:65A2:A6AB:7F90:146F:A50B:048C:8C75:651B:AA55:7129:6740'}, 'ns1.it.dns.d0wn.biz': {'countrycode': 'it', 'dnscryptcertname': '2.dnscrypt-cert.it.d0wn.biz', 'country': 'Italy', 'dnscryptpubkey': 'pubkey.it.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '31.14.133.188', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': 'B8F4:76E3:1EA4:ADDB:3426:D870:2819:6989:91EE:0C5A:B789:C74E:D6D9:BFB6:6C29:1D5C'}, 'ns3.nl.dns.d0wn.biz': {'countrycode': 'nl', 'dnscryptcertname': '2.dnscrypt-cert.nl3.d0wn.biz', 'country': 'Netherlands', 'dnscryptpubkey': 'pubkey.nl3.dnscrypt.d0wn.biz', 'ip6': '2a06:7240:5:601:dead:beef:e3e7:7a9d', 'ip4': '185.133.72.116', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '01FC:1AA9:F71F:F09E:55CE:0D04:9ACA:2B11:9536:319E:04A9:C3AE:77CB:127D:4C53:0651'}, 'ns1.md.dns.d0wn.biz': {'countrycode': 'md', 'dnscryptcertname': '2.dnscrypt-cert.md.d0wn.biz', 'country': 'Moldova', 'dnscryptpubkey': 'pubkey.md.dnscrypt.d0wn.biz', 'ip6': '2a00:1dc0:cafe::ad86:fa7e', 'ip4': '178.17.170.67', 'dnscryptports': '54 1053 5353 27015', 'dnscryptfingerprint': '3DB2:C4CB:39E2:6B82:FDDF:6D91:1A65:D164:F4F0:D237:8CDD:0C37:469F:24BA:B9A0:F9FF'}, 'ns2.us.dns.d0wn.biz': {'countrycode': 'us', 'dnscryptcertname': '2.dnscrypt-cert.us2.d0wn.biz', 'country': 'United States of America', 'dnscryptpubkey': 'pubkey.us.dnscrypt.d0wn.biz', 'ip6': '2605:6400:20:7d7:1:5ee:bad:c0de', 'ip4': '209.141.53.57', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': 'A22D:99C4:E2E9:CB94:67F0:E36A:619F:418B:466C:5786:C0B8:ACAA:B716:71F7:1F81:F5F8'}, 'ns1.ro.dns.d0wn.biz': {'countrycode': 'ro', 'dnscryptcertname': '2.dnscrypt-cert.ro.d0wn.biz', 'country': 'Romania', 'dnscryptpubkey': 'pubkey.ro.dnscrypt.d0wn.biz', 'ip6': '2a04:9dc0:c1:7::cb9:f785', 'ip4': '77.81.104.121', 'dnscryptports': '54 80 443 5353 1053 27015', 'dnscryptfingerprint': 'DA9E:6882:B0F8:335E:B5F4:A059:1B7D:EE6F:BD55:4451:93B4:13BF:AFFC:7D26:4527:CE1A'}, 'ns2.de.dns.d0wn.biz': {'countrycode': 'de', 'dnscryptcertname': '2.dnscrypt-cert.de2.d0wn.biz', 'country': 'Germany', 'dnscryptpubkey': 'pubkey.de2.dnscrypt.d0wn.biz', 'ip6': '', 'ip4': '185.137.15.105', 'dnscryptports': '54 80 443 1053 5353 27015', 'dnscryptfingerprint': '8C62:691A:A7EA:69D3:8A25:86AA:2715:87F0:9B11:9159:0663:55FC:1CD0:61C5:C863:1940'}}
		# update content of 'self.d0wns_DNS' in DEVMODE only: if 'self.d0wns_DNS = {}' with self.load_d0wns_dns() called from mainwindow rightclick and copy from debug.log
		#self.d0wns_DNS = {}
		
		import flags_b64
		self.FLAGS_B64 = flags_b64.flagsb64()
		print "len(self.FLAGS_B64) = '%s'" % (len(self.FLAGS_B64))
		#self.COUNTRYNAMES under: def make_systray_server_menu, here is translation not active
		self.FLAG_CACHE_PIXBUF = {}
		self.ICON_CACHE_PIXBUF = {}
		#self.IDLE_TIME = 0
		self.systray_menu = False
		self.WINDOW_QUIT_OPEN = False
		self.WINDOW_ABOUT_OPEN = False
		
		self.OVPN_SERVER_INFO = {}
		self.OVPN_SRV_DATA = {}
		self.LAST_OVPN_SRV_DATA_UPDATE = 0
		self.OVPN_ACC_DATA = {}
		self.OVPN_ACC_DATAfrombefore = False
		self.LAST_OVPN_ACC_DATA_UPDATE = 0
		#self.LAST_OVPN_SERVER_RELOAD = 0
		self.AUTOSTART = False
		self.AUTOSTART_DELAY_TIME = 30
		#self.AUTOSTART_DELAY = [ "10", "20", "30", "40", "50", "60" ]
		self.AUTOSTART_DELAY = [ 10, 20, 30, 40, 50, 60 ]
		self.UPDATEOVPNONSTART = False
		self.request_UPDATE = True
		self.APIKEY = False
		self.LOAD_DATA_EVERY = 900
		self.LOAD_ACCDATA = False
		self.request_LOAD_ACCDATA = True
		self.LOAD_SRVDATA = False
		self.request_LOAD_SRVDATA = False
		self.SRV_LIGHT_WIDTH = "512"
		self.SRV_LIGHT_HEIGHT = "720"
		self.SRV_WIDTH = "1280"
		self.SRV_HEIGHT = "720"
		self.SRV_LIGHT_WIDTH_DEFAULT = self.SRV_LIGHT_WIDTH
		self.SRV_LIGHT_HEIGHT_DEFAULT = self.SRV_LIGHT_HEIGHT
		self.SRV_WIDTH_DEFAULT = self.SRV_WIDTH
		self.SRV_HEIGHT_DEFAULT = self.SRV_HEIGHT
		self.WIN_RESET_EXT_DEVICE = False
		self.WIN_FIREWALL_STARTED = False
		self.WIN_FIREWALL_ADDED_RULE_TO_VCP = False
		self.WIN_BACKUP_FIREWALL = False
		self.WIN_RESET_FIREWALL = False
		self.WIN_DONT_ASK_FW_EXIT = False
		self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = True
		self.WIN_DISABLE_EXT_IF_ON_DISCO = False
		self.WIN_DNS_CHANGED = False
		self.CA_FIXED_HASH = "f37dff160dda454d432e5f0e0f30f8b20986b59daadabf2d261839de5dfd1e7d8a52ecae54bdd21c9fee9238628f9fff70c7e1a340481d14f3a1bdeea4a162e8"
		self.DISABLE_SRV_WINDOW = False
		self.DISABLE_ACC_WINDOW = False
		self.DISABLE_QUIT_ENTRY = True
		self.OVERWRITE_TRAYICON = False
		self.MOUSE_IN_TRAY = 0
		self.UPDATE_SWITCH = False
		self.isWRITING_OPTFILE = False
		self.WHITELIST_PUBLIC_PROFILE = {
			"Intern 01) oVPN Connection Check": {"ip":self.GATEWAY_OVPN_IP4A,"port":"80","proto":"tcp"},
			"Intern 02) https://vcp.ovpn.to": {"ip":self.GATEWAY_OVPN_IP4A,"port":"443","proto":"tcp"},
			"Intern 03) IRC": {"ip":self.GATEWAY_OVPN_IP4A,"port":"6697","proto":"tcp"},
			"Intern 04) DNS": {"ip":self.GATEWAY_OVPN_IP4A,"port":"53","proto":"tcp"},
			"Intern 05) DNS": {"ip":self.GATEWAY_OVPN_IP4A,"port":"53","proto":"udp"},
			"Intern 06) SSH": {"ip":self.GATEWAY_OVPN_IP4A,"port":"22","proto":"tcp"},
			"Intern 07) SOCKS": {"ip":self.GATEWAY_OVPN_IP4A,"port":"1080","proto":"tcp"},
			"Intern 08) HTTP": {"ip":self.GATEWAY_OVPN_IP4A,"port":"3128","proto":"tcp"},
			"Intern 09) SOCKS Random": {"ip":self.GATEWAY_OVPN_IP4A,"port":"1081","proto":"tcp"},
			"Intern 10) HTTP Random": {"ip":self.GATEWAY_OVPN_IP4A,"port":"3129","proto":"tcp"},
			"Intern 11) STUNNEL HTTP": {"ip":self.GATEWAY_OVPN_IP4A,"port":"8081","proto":"tcp"},
			"Intern 12) STUNNEL SOCKS": {"ip":self.GATEWAY_OVPN_IP4A,"port":"8080","proto":"tcp"},
			"Intern 13) TOR SOCKS": {"ip":self.GATEWAY_OVPN_IP4A,"port":"9100","proto":"tcp"},
			"Intern 14) JABBER client": {"ip":self.GATEWAY_OVPN_IP4A,"port":"5222","proto":"tcp"},
			"Intern 15) JABBER transfer": {"ip":self.GATEWAY_OVPN_IP4A,"port":"5000","proto":"tcp"},
			"Intern 16) AnoMail IMAPs": {"ip":self.GATEWAY_OVPN_IP4A,"port":"993","proto":"tcp"},
			"Intern 17) AnoMail POP3s": {"ip":self.GATEWAY_OVPN_IP4A,"port":"995","proto":"tcp"},
			"Intern 18) AnoMail SMTPs": {"ip":self.GATEWAY_OVPN_IP4A,"port":"587","proto":"tcp"},
			"Intern 19) ZNC": {"ip":self.GATEWAY_OVPN_IP4A,"port":"6444","proto":"tcp"},
			"Intern 20) dnscrypt": {"ip":self.GATEWAY_OVPN_IP4A,"port":"5353","proto":"tcp"},
			"Intern 21) dnscrypt": {"ip":self.GATEWAY_OVPN_IP4A,"port":"5353","proto":"udp"},
			"Intern 22) nntp-50001 Binary SSL user=ovpn,pass=free": {"ip":self.GATEWAY_OVPN_IP4A,"port":"50001","proto":"tcp"},
			"Intern 23) nntp-50002 Binary SSL user=ovpn,pass=free": {"ip":self.GATEWAY_OVPN_IP4A,"port":"50002","proto":"tcp"}
		}

	def preboot(self):
		self.debug(1,"def preboot()")
		self.self_vars()
		if self.OS == "win32":
				if self.win_pre1_check_app_dir():
					if self.win_pre2_check_profiles_win():
						if self.win_pre3_load_profile_dir_vars():
							if self.check_config_folders():
								if self.read_options_file():
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
			print "alternative folder found"
			self.BIN_DIR = os.getcwd()
			self.APP_DIR = "%s\\appdata\\ovpn" % (self.BIN_DIR)
		else:
			self.APP_DIR = "%s\\ovpn" % (os_appdata)
			self.BIN_DIR = "%s\\bin\\client\\dist" % (self.APP_DIR)
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
		self.PROFILES = list()
		for profile in self.profiles_unclean:
			if profile.isdigit():
				self.PROFILES.append(profile)
		self.PROFILES_COUNT = len(self.PROFILES)
		self.debug(1,"def list_profiles: profiles_count %s" % (self.PROFILES_COUNT))

	def win_pre2_check_profiles_win(self):
		self.debug(1,"def win_pre2_check_profiles_win()")
		self.list_profiles()
		if self.PROFILES_COUNT == 0:
			self.debug(1,"No profiles found")
			if self.USERID == False:
				self.debug(1,"spawn popup userid = %s" % (self.USERID))
				self.debug(1,"def win_pre2_check_profiles_win: L:308")
				self.form_ask_userid()
				self.debug(1,"def win_pre2_check_profiles_win: L:309")
				if not self.USERID == False and not self.APIKEY == False:
					self.debug(1,"def win_pre2_check_profiles_win: L:310")
					return True
		elif self.PROFILES_COUNT == 1 and self.PROFILES[0] > 1:
			self.USERID = self.PROFILES[0]
			return True
		elif self.PROFILES_COUNT > 1:
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
			except:
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
		
		self.DNS_DIR =  "%s\\dns" % (self.BIN_DIR)
		self.dns_d0wntxt =  "%s\\dns.txt" % (self.DNS_DIR)
		
		self.zip_cfg = "%s\\confs.zip" % (self.VPN_DIR)
		self.zip_crt = "%s\\certs.zip" % (self.VPN_DIR)
		self.api_upd = "%s\\lastupdate.txt" % (self.VPN_DIR)
		if os.path.isfile(self.api_upd):
			os.remove(self.api_upd)
		
		if self.load_icons() == False:
			return False
		
		self.CA_FILE = "%s\\cacert_ovpn.pem" % (self.BIN_DIR)
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
		self.debug(1,"def load_icons()")
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
					self.msgwarn(_("Private Icon(s) not found in:\n%s\n\nMissing Icons:\n%s") % (self.ico_dir_theme,missing_file),_("Error: Icon"))
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
				self.msgwarn(_("Private Icon Dir not found:\n%s") % (self.ico_dir_theme),_("Error: Icon Dir"))
				return False

		self.systrayicon_from_before = False
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
				except:
					self.errorquit(text=_("Could not remove lock file.\nFile itself locked because another oVPN Client instance running?"))
			if not os.path.isfile(self.lock_file):
				self.LOCK = open(self.lock_file,'wb')
				self.LOCK.write("%s" % (int(time.time())))
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
		except:
			self.errorquit(text=_("Creating config Folders failed"))

	def read_options_file(self):
		self.debug(1,"def read_options_file()")
		if os.path.isfile(self.OPT_FILE):
			try:
				parser = SafeConfigParser()
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
				except:
					pass
				
				try:
					self.DEBUG = parser.getboolean('oVPN','debugmode')
					self.debug(1,BUILT_STRING)
				except:
					pass
				
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
				except:
					self.debug(1,"def read_options_file: self.APP_LANGUAGE FAILED")
				
				try:
					LAST_CFG_UPDATE = parser.getint('oVPN','lastcfgupdate')
					if not LAST_CFG_UPDATE >= 0:
						self.LAST_CFG_UPDATE = 0
					else:
						self.LAST_CFG_UPDATE = LAST_CFG_UPDATE
					self.debug(1,"def read_options_file: self.LAST_CFG_UPDATE = '%s'" % (self.LAST_CFG_UPDATE))
				except:
					self.debug(1,"def read_options_file: self.LAST_CFG_UPDATE failed")
				
				try:
					OVPN_FAV_SERVER = parser.get('oVPN','favserver')
					if OVPN_FAV_SERVER == "False": 
						self.OVPN_FAV_SERVER = False
						self.OVPN_AUTO_CONNECT_ON_START = False
					else:
						self.OVPN_FAV_SERVER = OVPN_FAV_SERVER
						self.OVPN_AUTO_CONNECT_ON_START = True
					self.debug(1,"def read_options_file: self.OVPN_FAV_SERVER = '%s'" % (self.OVPN_FAV_SERVER))
				except:
					self.debug(1,"def read_options_file: self.OVPN_FAV_SERVER failed")
				
				try:
					WIN_EXT_DEVICE = parser.get('oVPN','winextdevice')
					if WIN_EXT_DEVICE == "False": 
						self.WIN_EXT_DEVICE = False
					else:
						self.WIN_EXT_DEVICE = WIN_EXT_DEVICE
					self.debug(1,"def read_options_file: self.WIN_TAP_DEVICE = '%s'" % (self.WIN_EXT_DEVICE))
				except:
					self.debug(1,"def read_options_file: self.WIN_TAP_DEVICE failed")
				
				try:
					WIN_TAP_DEVICE = parser.get('oVPN','wintapdevice')
					if WIN_TAP_DEVICE == "False": 
						self.WIN_TAP_DEVICE = False
					else:
						self.WIN_TAP_DEVICE = WIN_TAP_DEVICE
					self.debug(1,"def read_options_file: self.WIN_TAP_DEVICE = '%s'" % (self.WIN_TAP_DEVICE))
				except:
					self.debug(1,"def read_options_file: self.WIN_TAP_DEVICE failed")
				
				try:
					OPENVPN_EXE = parser.get('oVPN','openvpnexe')
					if OPENVPN_EXE == "False":
						self.OPENVPN_EXE = False
					else:
						self.OPENVPN_EXE = OPENVPN_EXE
					self.debug(1,"def read_options_file: self.OPENVPN_EXE = '%s'" % (self.OPENVPN_EXE))
				except:
					pass
				
				try:
					AUTOSTART_DELAY_TIME = parser.getint('oVPN','autostartdelay')
					if AUTOSTART_DELAY_TIME >= 10:
						self.AUTOSTART_DELAY_TIME = AUTOSTART_DELAY_TIME
					else:
						self.AUTOSTART_DELAY_TIME = 10
					self.debug(1,"def read_options_file: self.AUTOSTART_DELAY_TIME = '%s'" % (self.AUTOSTART_DELAY_TIME))
				except:
					self.debug(1,"def read_options_file: self.AUTOSTART_DELAY_TIME failed")
				
				try:
					self.AUTOSTART = parser.getboolean('oVPN','autostart')
					if self.AUTOSTART == True:
						try:
							schedule_task.set_task(self.DEBUG,self.AUTOSTART_DELAY_TIME)
						except:
							pass
					self.debug(1,"def read_options_file: self.AUTOSTART = '%s'" % (self.AUTOSTART))
				except:
					self.debug(1,"def read_options_file: self.AUTOSTART failed")
				
				try:
					self.UPDATEOVPNONSTART = parser.getboolean('oVPN','updateovpnonstart')
					self.debug(1,"def read_options_file: self.UPDATEOVPNONSTART = '%s'" % (self.UPDATEOVPNONSTART))
				except:
					self.debug(1,"def read_options_file: self.UPDATEOVPNONSTART failed")
				
				try:
					ocfgv = parser.get('oVPN','configversion')
					if ocfgv == "23x" or ocfgv == "23x46" or ocfgv == "23x64":
						self.OVPN_CONFIGVERSION = ocfgv
					else:
						self.OVPN_CONFIGVERSION = "23x"
					
					if self.OVPN_CONFIGVERSION == "23x":
						self.GATEWAY_OVPN_IP4 = self.GATEWAY_OVPN_IP4A
						self.VPN_CFG = self.VPN_CFGip4
					elif self.OVPN_CONFIGVERSION == "23x46":
						self.GATEWAY_OVPN_IP4 = self.GATEWAY_OVPN_IP4B
						self.VPN_CFG = self.VPN_CFGip46
					elif self.OVPN_CONFIGVERSION == "23x64":
						self.GATEWAY_OVPN_IP4 = self.GATEWAY_OVPN_IP4B
						self.VPN_CFG = self.VPN_CFGip64
					
					self.debug(1,"def read_options_file: self.OVPN_CONFIGVERSION = '%s'" % (self.OVPN_CONFIGVERSION))
				except:
					self.debug(1,"def read_options_file: self.OVPN_CONFIGVERSION failed")
				
				try:
					self.WIN_RESET_FIREWALL = parser.getboolean('oVPN','winresetfirewall')
					self.debug(1,"def read_options_file: self.WIN_RESET_FIREWALL = '%s'" % (self.WIN_RESET_FIREWALL))
				except:
					pass
				
				try:
					self.WIN_BACKUP_FIREWALL = parser.getboolean('oVPN','winbackupfirewall')
					self.debug(1,"def read_options_file: self.WIN_BACKUP_FIREWALL = '%s'" % (self.WIN_RESET_FIREWALL))
				except:
					pass
				
				try:
					self.NO_WIN_FIREWALL = parser.getboolean('oVPN','nowinfirewall')
					self.debug(1,"def read_options_file: self.NO_WIN_FIREWALL = '%s'" % (self.NO_WIN_FIREWALL))
				except:
					pass
				
				try:
					self.WIN_DONT_ASK_FW_EXIT = parser.getboolean('oVPN','winnoaskfwonexit')
					self.debug(1,"def read_options_file: self.WIN_DONT_ASK_FW_EXIT = '%s'" % (self.WIN_DONT_ASK_FW_EXIT))
				except:
					pass
				
				try:
					self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = parser.getboolean('oVPN','winfwblockonexit')
					self.debug(1,"def read_options_file: self.WIN_ALWAYS_BLOCK_FW_ON_EXIT = '%s'" % (self.WIN_ALWAYS_BLOCK_FW_ON_EXIT))
				except:
					pass

				try:
					self.WIN_DISABLE_EXT_IF_ON_DISCO = parser.getboolean('oVPN','windisableextifondisco')
					self.debug(1,"def read_options_file: self.WIN_DISABLE_EXT_IF_ON_DISCO = '%s'" % (self.WIN_DISABLE_EXT_IF_ON_DISCO))
				except:
					pass
				
				
				try:
					self.TAP_BLOCKOUTBOUND = parser.getboolean('oVPN','wintapblockoutbound')
					self.debug(1,"def read_options_file: self.TAP_BLOCKOUTBOUND = '%s'" % (self.TAP_BLOCKOUTBOUND))
				except:
					pass
				
				try:
					self.NO_DNS_CHANGE = parser.getboolean('oVPN','nodnschange')
					self.debug(1,"def read_options_file: self.NO_DNS_CHANGE = '%s'" % (self.NO_DNS_CHANGE))
				except:
					pass

				try:
					LOAD_DATA_EVERY = parser.getint('oVPN','loaddataevery')
					if LOAD_DATA_EVERY >= 66:
						self.LOAD_DATA_EVERY = LOAD_DATA_EVERY
					else:
						self.LOAD_DATA_EVERY = 900
						
					self.debug(1,"def read_options_file: self.LOAD_DATA_EVERY = '%s'" % (self.LOAD_DATA_EVERY))
				except:
					pass
					
				try:
					MAINWINDOW_SHOWCELLS = json.loads(parser.get('oVPN','mainwindowshowcells'))
					if len(MAINWINDOW_SHOWCELLS) > 0:
						self.MAINWINDOW_SHOWCELLS = MAINWINDOW_SHOWCELLS
						self.debug(1,"def read_options_file: self.MAINWINDOW_SHOWCELLS = '%s'" % (self.MAINWINDOW_SHOWCELLS))
				except:
					pass
					
				try:
					self.LOAD_ACCDATA = parser.getboolean('oVPN','loadaccinfo')
					self.debug(1,"def read_options_file: self.LOAD_ACCDATA = '%s'" % (self.LOAD_ACCDATA))
				except:
					pass
				
				try:
					self.LOAD_SRVDATA = parser.getboolean('oVPN','serverviewextend')
					self.debug(1,"def read_options_file: self.LOAD_SRVDATA = '%s'" % (self.LOAD_SRVDATA))
				except:
					pass
				
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
				except:
					pass
				
				try:
					self.APP_THEME = parser.get('oVPN','theme')
					self.debug(1,"def read_options_file: self.APP_THEME = '%s'" % (self.APP_THEME))
				except:
					pass
				
				try:
					self.ICONS_THEME = parser.get('oVPN','icons')
					self.load_icons()
					self.debug(1,"def read_options_file: self.ICONS_THEME = '%s'" % (self.ICONS_THEME))
				except:
					pass
				
				try:
					self.APP_FONT_SIZE = parser.get('oVPN','font')
					self.debug(1,"def read_options_file: self.APP_FONT_SIZE = '%s'" % (self.APP_FONT_SIZE))
				except:
					pass
				
				try:
					self.DISABLE_QUIT_ENTRY = parser.getboolean('oVPN','disablequitentry')
					self.debug(1,"def read_options_file: self.DISABLE_QUIT_ENTRY '%s'" % (self.DISABLE_QUIT_ENTRY))
				except:
					pass
				
				try:
					MYDNS = json.loads(parser.get('oVPN','mydns'))
					if len(MYDNS) > 0:
						self.MYDNS = MYDNS
					self.debug(1,"def read_options_file: len(self.MYDNS) == '%s', self.MYDNS == '%s'"%(len(self.MYDNS),self.MYDNS))
				except:
					self.debug(1,"def read_options_file: self.MYDNS = json.loads failed")
					self.MYDNS = {}
				
				return True
			
			except:
				self.msgwarn(_("Read config file failed!"),_("Error: def read_options_file"))
				try:
					os.remove(self.OPT_FILE)
				except:
					pass
		
		else:
			# We have no config file here at first start, set right values
			self.VPN_CFG = self.VPN_CFGip4
			self.init_localization(None)
			try:
				cfg = open(self.OPT_FILE,'wb')
				parser = SafeConfigParser()
				parser.add_section('oVPN')
				parser.set('oVPN','apikey','%s'%(self.APIKEY))
				parser.set('oVPN','debugmode','%s'%(self.DEBUG))
				parser.set('oVPN','applanguage','%s'%(self.APP_LANGUAGE))
				parser.set('oVPN','lastcfgupdate','%s'%(self.LAST_CFG_UPDATE))
				parser.set('oVPN','favserver','%s'%(self.OVPN_FAV_SERVER))
				parser.set('oVPN','winextdevice','%s'%(self.WIN_EXT_DEVICE))
				parser.set('oVPN','wintapdevice','%s'%(self.WIN_TAP_DEVICE))
				parser.set('oVPN','openvpnexe','%s'%(self.OPENVPN_EXE))
				parser.set('oVPN','autostartdelay','%s'%(self.AUTOSTART_DELAY_TIME))
				parser.set('oVPN','autostart','%s'%(self.AUTOSTART))
				parser.set('oVPN','updateovpnonstart','%s'%(self.UPDATEOVPNONSTART))
				parser.set('oVPN','configversion','%s'%(self.OVPN_CONFIGVERSION))
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
				parser.set('oVPN','mainwindowshowcells','%s'%(json.dumps(self.MAINWINDOW_SHOWCELLS, ensure_ascii=True)))
				parser.set('oVPN','disablequitentry','%s'%(self.DISABLE_QUIT_ENTRY))
				parser.set('oVPN','mydns','False')
				parser.write(cfg)
				cfg.close()
				return True
			except:
				self.debug(1,"def read_options_file: create failed")

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
			cfg = open(self.OPT_FILE,'wb')
			parser = SafeConfigParser()
			parser.add_section('oVPN')
			parser.set('oVPN','apikey','%s'%(APIKEY))
			parser.set('oVPN','debugmode','%s'%(self.DEBUG))
			parser.set('oVPN','applanguage','%s'%(self.APP_LANGUAGE))
			parser.set('oVPN','lastcfgupdate','%s'%(self.LAST_CFG_UPDATE))
			parser.set('oVPN','favserver','%s'%(self.OVPN_FAV_SERVER))
			parser.set('oVPN','winextdevice','%s'%(self.WIN_EXT_DEVICE))
			parser.set('oVPN','wintapdevice','%s'%(self.WIN_TAP_DEVICE))
			parser.set('oVPN','openvpnexe','%s'%(self.OPENVPN_EXE))
			parser.set('oVPN','autostartdelay','%s'%(self.AUTOSTART_DELAY_TIME))
			parser.set('oVPN','autostart','%s'%(self.AUTOSTART))
			parser.set('oVPN','updateovpnonstart','%s'%(self.UPDATEOVPNONSTART))
			parser.set('oVPN','configversion','%s'%(self.OVPN_CONFIGVERSION))
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
			parser.set('oVPN','mainwindowshowcells','%s'%(json.dumps(self.MAINWINDOW_SHOWCELLS, ensure_ascii=True)))
			parser.set('oVPN','disablequitentry','%s'%(self.DISABLE_QUIT_ENTRY))
			parser.set('oVPN','mydns','%s'%(json.dumps(self.MYDNS, ensure_ascii=True)))
			parser.write(cfg)
			cfg.close()
			self.isWRITING_OPTFILE = False
			return True
		except:
			self.debug(1,"def write_options_file: failed")
		self.isWRITING_OPTFILE = False

	def read_interfaces(self):
		self.debug(1,"def read_interfaces()")
		if self.OS == "win32":
			if self.WIN_RESET_EXT_DEVICE == False:
				if self.win_read_interfaces():
					if self.win_firewall_export_on_start():
						if self.win_read_dns_to_backup():
							if self.read_gateway_from_interface():
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
				self.win_netsh_restore_dns_from_backup()
				self.WIN_RESET_EXT_DEVICE = False
				if self.win_read_interfaces():
					if self.win_firewall_export_on_start():
						if self.win_read_dns_to_backup():
							if self.read_gateway_from_interface():
								return True

	def win_read_interfaces(self):
		self.debug(1,"def win_read_interfaces()")
		self.INTERFACES = winregs.get_networkadapterlist(self.DEBUG)
		if len(self.INTERFACES) < 2:
			self.errorquit(text=_("Could not read your Network Interfaces! Please install OpenVPN or check if your TAP-Adapter is really enabled and driver installed."))
		newdata = winregs.get_tapadapters(self.OPENVPN_EXE,self.INTERFACES)
		self.INTERFACES = newdata["INTERFACES"]
		self.WIN_TAP_DEVS = newdata["TAP_DEVS"]
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
		if self.WIN_TAP_DEVICE == False:
			self.errorquit(text=_("No OpenVPN TAP-Adapter found!\nPlease install openVPN!\nURL1: %s\nURL2: %s") % (openvpn.values(DEBUG)["OPENVPN_DL_URL"],openvpn.values(DEBUG)["OPENVPN_DL_URL_ALT"]))
		else:
			badchars = ["%","&","$"]
			for char in badchars:
				if char in self.WIN_TAP_DEVICE:
					self.errorquit(text=_("Invalid characters in '%s'") % char)
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

	def win_select_tapadapter(self):
		dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK)
		dialogWindow.set_position(Gtk.WindowPosition.CENTER)
		dialogWindow.set_transient_for(self.window)
		dialogWindow.set_border_width(8)
		try:
			dialogWindow.set_icon(self.app_icon)
		except:
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

	def win_select_networkadapter(self):
		dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK)
		dialogWindow.set_position(Gtk.WindowPosition.CENTER)
		dialogWindow.set_transient_for(self.window)
		dialogWindow.set_border_width(8)
		try:
			dialogWindow.set_icon(self.app_icon)
		except:
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

	def select_userid(self):
		self.debug(1,"def select_userid()")
		dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK)
		dialogWindow.set_position(Gtk.WindowPosition.CENTER)
		dialogWindow.set_transient_for(self.window)
		dialogWindow.set_border_width(8)
		try:
			dialogWindow.set_icon(self.app_icon)
		except:
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

	def on_right_click_mainwindow(self, treeview, event):
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

	def make_context_menu_servertab(self,servername):
		self.debug(1,"def make_context_menu_servertab: %s" % (servername))
		context_menu_servertab = Gtk.Menu()
		self.context_menu_servertab = context_menu_servertab
		
		if self.OVPN_CONNECTEDto == servername:
			disconnect = Gtk.MenuItem(_("Disconnect %s")%(self.OVPN_CONNECTEDto))
			context_menu_servertab.append(disconnect)
			disconnect.connect('button-release-event', self.cb_kill_openvpn)
		else:
			connect = Gtk.MenuItem(_("Connect to %s")%(servername))
			context_menu_servertab.append(connect)
			connect.connect('button-release-event',self.cb_jump_openvpn,servername)
		
		sep = Gtk.SeparatorMenuItem()
		context_menu_servertab.append(sep)
		
		if self.OVPN_FAV_SERVER == servername:
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
			except:
				self.debug(1,"def make_context_menu_servertab: extserverview failed")

			try:
				if self.LOAD_SRVDATA == True:
					hidecells = Gtk.MenuItem(_("Hide unwanted cells"))
					hidecells.connect('button-release-event', self.cb_hide_cells)
					context_menu_servertab.append(hidecells)
			except:
				self.debug(1,"def make_context_menu_servertab: hidecells failed")

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
			except:
				self.debug(1,"def make_context_menu_servertab: extserverviewsize failed")
				
			try:
				loaddataevery = Gtk.MenuItem(_("Update every: %s seconds") %(self.LOAD_DATA_EVERY))
				loaddataevery.connect('button-release-event', self.cb_set_loaddataevery)
				context_menu_servertab.append(loaddataevery)
			except:
				self.debug(1,"def make_context_menu_servertab: loaddataevery failed")

		context_menu_servertab.show_all()
		context_menu_servertab.popup(None, None, None, 3, int(time.time()), 0)
		self.debug(1,"def make_context_menu_servertab: return")
		return

	def make_context_menu_servertab_d0wns_dnsmenu(self,servername):
		try:
			self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: servername = '%s'" % (servername))
			
			if self.DEVMODE == True and len(self.d0wns_DNS) == 0:
				self.load_d0wns_dns()
			
			dnsmenu = Gtk.Menu()
			dnsm = Gtk.MenuItem(_("Change DNS"))
			dnsm.set_submenu(dnsmenu)
			self.dnsmenu = dnsmenu
			
			try:
				self.debug(1,"mydns debug 1.1")
				pridns = self.MYDNS[servername]["primary"]["ip4"]
				self.debug(1,"mydns debug 1.2")
				priname = self.MYDNS[servername]["primary"]["dnsname"]
				self.debug(1,"mydns debug 1.3")
				string = _("Primary DNS: %s (%s)") % (priname,pridns)
				self.debug(1,"mydns debug 1.4")
				pridnsm = Gtk.MenuItem(string)
				self.debug(1,"mydns debug 1.5")
				cbdata = {servername:{"primary":{"ip4":pridns,"dnsname":priname}}}
				self.debug(1,"mydns debug 1.6")
				pridnsm.connect('button-release-event',self.cb_del_dns,cbdata)
				self.debug(1,"mydns debug 1.7")
				self.context_menu_servertab.append(pridnsm)
				self.debug(1,"mydns debug 1.8")
			except:
				self.debug(1,"mydns debug 1.9")
				pridns = False
			
			try:
				self.debug(1,"mydns debug 2.1")
				secdns = self.MYDNS[servername]["secondary"]["ip4"]
				self.debug(1,"mydns debug 2.2")
				secname = self.MYDNS[servername]["secondary"]["dnsname"]
				self.debug(1,"mydns debug 2.3")
				string = _("Secondary DNS: %s (%s)") % (secname,secdns)
				self.debug(1,"mydns debug 2.4")
				secdnsm = Gtk.MenuItem(string)
				self.debug(1,"mydns debug 2.5")
				cbdata = {servername:{"secondary":{"ip4":secdns,"dnsname":secname}}}
				self.debug(1,"mydns debug 2.6")
				secdnsm.connect('button-release-event',self.cb_del_dns,cbdata)
				self.debug(1,"mydns debug 2.7")
				self.context_menu_servertab.append(secdnsm)
				self.debug(1,"mydns debug 2.8")
			except:
				self.debug(1,"mydns debug 2.9")
				secdns = False
			
			for name,value in sorted(self.d0wns_DNS.iteritems()):
				try:
					dnsip4 = value['ip4']
					countrycode = self.d0wns_DNS[name]['countrycode']
					dnssubmenu = Gtk.Menu()
					self.dnssubmenu = dnssubmenu
					dnssubmtext = "%s (%s)" % (name,dnsip4)
					dnssubm = Gtk.ImageMenuItem(dnssubmtext)
					dnssubm.set_submenu(dnssubmenu)
					img = Gtk.Image()
					imgfile = self.decode_flag(countrycode)
					img.set_from_pixbuf(imgfile)
					dnssubm.set_always_show_image(True)
					dnssubm.set_image(img)
					dnsmenu.append(dnssubm)
					
					cbdata = {servername:{"primary":{"ip4":dnsip4,"dnsname":name}}}
					if pridns == dnsip4:
						string = _("Primary DNS '%s' @ %s") % (pridns,servername)
						setpridns = Gtk.MenuItem(string)
						setpridns.connect('button-release-event',self.cb_del_dns,cbdata)
					else:
						setpridns = Gtk.MenuItem(_("Set Primary DNS"))
						setpridns.connect('button-release-event',self.cb_set_dns,cbdata)
					dnssubmenu.append(setpridns)
					
					cbdata = {servername:{"secondary":{"ip4":dnsip4,"dnsname":name}}}
					if secdns == dnsip4:
						string = _("Secondary DNS '%s' @ %s") % (secdns,servername)
						setsecdns = Gtk.MenuItem(string)
						setsecdns.connect('button-release-event',self.cb_del_dns,cbdata)
					else:
						setsecdns = Gtk.MenuItem(_("Set Secondary DNS"))
						setsecdns.connect('button-release-event',self.cb_set_dns,cbdata)
					dnssubmenu.append(setsecdns)
				except:
					self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: dnsmenu.append(dnssubm) '%s' failed "%(countrycode))
				
			dnsm.show_all()
			self.context_menu_servertab.append(dnsm)
		except:
			self.debug(1,"def make_context_menu_servertab_d0wns_dnsmenu: failed!")

	def systray_timer2(self):
		self.debug(10,"def systray_timer2()")
		self.systray_timer2_running = True
		if self.stop_systray_timer2 == True:
			self.systray_timer2_running = False
			return False
		
		if not self.systray_menu == False:
			self.check_hide_popup()
		
		try:
			if self.LAST_MSGWARN_WINDOW > 0 and (int(time.time())-self.LAST_MSGWARN_WINDOW) > 9:
				GLib.idle_add(self.msgwarn_window.destroy)
				self.LAST_MSGWARN_WINDOW = 0
		except:
			pass
		
		if self.UPDATE_SWITCH == True and self.SETTINGSWINDOW_OPEN == True:
			self.debug(1,"def systray_timer2: UPDATE_SWITCH")
			
			# Language changed
			if self.LANG_FONT_CHANGE == True:
				try:
					self.settingsnotebook.remove(self.nbpage0)
					self.settingsnotebook.remove(self.nbpage1)
					self.settingsnotebook.remove(self.nbpage2)
				except:
					pass
				try:
					self.settingsnotebook.remove(self.nbpage3)
				except:
					pass
				try:
					self.show_hide_security_window()
					self.show_hide_options_window()
					self.show_hide_updates_window()
					self.settingswindow.show_all()
					self.settingsnotebook.set_current_page(1)
				except:
					pass
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
				except:
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
					self.show_hide_backup_window()
					self.settingswindow.show_all()
				except:
					pass
			
			# def settings_firewall_switch_nofw()
			if self.NO_WIN_FIREWALL == True:
				self.switch_fw.set_active(False)
				try:
					self.settingsnotebook.remove(self.nbpage3)
				except:
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
			if self.AUTOSTART == True:
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
			if self.OVPN_CONFIGVERSION == "23x":
				self.button_title.set_label(_("Current: IPv4 Entry Server with Exit to IPv4 (standard)"))
				self.button_ipmode.set_label(_("Use IPv4 Entry Server with Exits to IPv4 + IPv6"))
			elif self.OVPN_CONFIGVERSION == "23x46":
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
				if self.STATE_CERTDL == "lastupdate":
					systraytext = _("Checking for Updates!")
					systrayicon = self.systray_icon_syncupdate1
				elif self.STATE_CERTDL == "getconfigs":
					systraytext = _("Downloading Configurations...")
					systrayicon = self.systray_icon_syncupdate2
				elif self.STATE_CERTDL == "requestcerts":
					systraytext = _("Requesting Certificates...")
					systrayicon = self.systray_icon_syncupdate1
				elif self.STATE_CERTDL == "wait":
						systraytext = _("Please wait... Certificates requested from backend! (%s)") % (int(round(self.API_COUNTDOWN,0)))
						if not self.OVERWRITE_TRAYICON == False:
							systrayicon = self.OVERWRITE_TRAYICON
						elif self.STATUS_ICON_BLINK%2==0:
							systrayicon = self.systray_icon_syncupdate1
						else:
							systrayicon = self.systray_icon_syncupdate2
				elif self.STATE_CERTDL == "getcerts":
					systraytext = _("Downloading Certificates...")
					systrayicon = self.systray_icon_syncupdate1
				elif self.STATE_CERTDL == "extract":
					systraytext = _("Extracting Configs and Certs...")
					systrayicon = self.systray_icon_syncupdate2
				statusbar_text = systraytext
				
		elif self.state_openvpn() == False and self.OVERWRITE_TRAYICON == False:
			systraytext = _("Disconnected! Have a nice and anonymous day!")
			statusbar_text = systraytext
			systrayicon = self.systray_icon_disconnected
			try:
				if len(self.OVPN_SERVER) == 0 and self.INIT_FIRST_UPDATE == True:
					self.INIT_FIRST_UPDATE = False
					self.load_ovpn_server()
					if not self.APIKEY == False and len(self.OVPN_SERVER) == 0:
						self.debug(1,"zero server found, initiate first update")
						self.check_remote_update()
				elif len(self.OVPN_SERVER) > 0 and self.INIT_FIRST_UPDATE == True:
					self.INIT_FIRST_UPDATE = False
				elif self.OVPN_AUTO_CONNECT_ON_START == True and not self.OVPN_FAV_SERVER == False:
					self.OVPN_AUTO_CONNECT_ON_START = False
					self.debug(1,"def systray_timer: self.OVPN_AUTO_CONNECT_ON_START: self.OVPN_FAV_SERVER = '%s'" % (self.OVPN_FAV_SERVER))
					self.cb_jump_openvpn(0,0,self.OVPN_FAV_SERVER)
				
			except:
				self.debug(1,"def timer_statusbar: OVPN_AUTO_CONNECT_ON_START failed")
		elif self.inThread_jump_server_running == True and self.OVERWRITE_TRAYICON == True:
			systraytext = _("Connecting to %s") % (self.OVPN_CALL_SRV)
			systrayicon = self.systray_icon_connect
			statusbar_text = systraytext
			self.debug(1,"def systray_timer: cstate = '%s'" % (systraytext))
		elif self.state_openvpn() == True:
			connectedseconds = int(time.time()) - self.OVPN_CONNECTEDtime
			self.OVPN_CONNECTEDseconds = connectedseconds
			if self.OVPN_PING_STAT == -2:
				self.OVPN_isTESTING = True
				systraytext = _("Testing connection to %s") % (self.OVPN_CONNECTEDto)
				systrayicon = self.systray_icon_testing
				statusbar_text = systraytext
				self.debug(1,"def systray_timer: cstate = '%s'" % (systraytext))
			elif self.OVPN_PING_LAST == -2 and self.OVPN_PING_DEAD_COUNT > 3:
				systraytext = _("Connection to %s unstable or failed!") % (self.OVPN_CONNECTEDto)
				systrayicon = self.systray_icon_testing
				statusbar_text = systraytext
				self.debug(1,"def systray_timer: cstate = '%s'" % (systraytext))
			elif self.OVPN_PING_STAT > 0:
				try:
					if self.OVPN_isTESTING == True:
						self.OVPN_PING = list()
						self.OVPN_PING_STAT = self.OVPN_PING_LAST
						self.OVPN_isTESTING = False
					m, s = divmod(connectedseconds, 60)
					h, m = divmod(m, 60)
					d, h = divmod(h, 24)
					if self.OVPN_CONNECTEDseconds >= 0:
						connectedtime_text = "%d:%02d:%02d:%02d" % (d,h,m,s)
					statusbar_text = _("Connected to %s [%s]:%s (%s) [ %s ] (%s / %s ms)") % (self.OVPN_CONNECTEDto,self.OVPN_CONNECTEDtoIP,self.OVPN_CONNECTEDtoPort,self.OVPN_CONNECTEDtoProtocol.upper(),connectedtime_text,self.OVPN_PING_LAST,self.OVPN_PING_STAT)
					# systraytext Windows only shows the first 64 characters
					systraytext = "%s [%s]:%s (%s) [%s] %sms" % (self.OVPN_CONNECTEDto,self.OVPN_CONNECTEDtoIP,self.OVPN_CONNECTEDtoPort,self.OVPN_CONNECTEDtoProtocol.upper(),connectedtime_text,self.OVPN_PING_LAST)
					#statusbar_text = systraytext
					systrayicon = self.systray_icon_connected
				except:
					self.debug(1,"def systray_timer: systraytext failed")
		
		try:
			try:
				# traytext
				if not self.systraytext_from_before == systraytext and not systraytext == False:
					self.systraytext_from_before = systraytext
					self.tray.set_tooltip_markup(systraytext)
			except:
				self.debug(1,"def systray_timer2: set traytext failed")
				
			try:
				# trayicon
				if not self.systrayicon_from_before == systrayicon:
					self.systrayicon_from_before = systrayicon
					if self.APP_THEME == "private":
						self.tray.set_from_file(systrayicon)
					else:
						self.tray.set_from_pixbuf(systrayicon)
			except:
				self.debug(1,"def systray_timer2: set trayicon failed")
			
			try:
				# statusbar
				if self.MAINWINDOW_OPEN == True and self.MAINWINDOW_HIDE == False:
					if not self.statusbartext_from_before == statusbar_text:
						self.set_statusbar_text(statusbar_text)
						self.statusbartext_from_before = statusbar_text
			except:
				self.debug(1,"def systray_timer2: set statusbar failed")
		except:
			self.debug(1,"def systray_timer2: set 'traytext, trayicon, statusbar' failed")
		
		try:
			if self.timer_load_remote_data_running == False:
				thread = threading.Thread(target=self.load_remote_data)
				thread.daemon = True
				thread.start()
		except:
			self.debug(1,"def systray_timer2: thread target=self.load_remote_data failed")
		
		self.systray_timer2_running = False
		
		self.debug(19,"def systray_timer2() return")
		return

	def systray_timer(self):
		#self.debug(19,"def systray_timer()")
		if self.stop_systray_timer == True:
			return False
		if self.systray_timer2_running == False:
			self.debug(19,"def systray_timer: GLib.idle_add(self.systray_timer2)")
			GLib.idle_add(self.systray_timer2)
		time.sleep(0.5)
		thread = threading.Thread(target=self.systray_timer)
		thread.daemon = True
		thread.start()
		return

	def on_right_click(self, widget, event, event_time):
		self.debug(1,"def on_right_click()")
		#self.IDLE_TIME = 0
		if not self.systray_menu == False:
			self.destroy_systray_menu()
		else:
			self.make_systray_menu(event)

	def on_left_click(self, widget):
		self.debug(1,"def on_left_click()")
		#self.IDLE_TIME = 0
		if not self.systray_menu == False:
			self.destroy_systray_menu()
		else:
			if self.MAINWINDOW_OPEN == False:
				try:
					self.load_ovpn_server()
					if len(self.OVPN_SERVER) > 0:
						event = Gtk.get_current_event_time()
						self.show_mainwindow(widget, event)
				except:
					self.debug(1,"def show_mainwindow() on_left_click failed")
			else:
				if self.mainwindow.get_property("visible") == False:
					self.debug(1,"def on_left_click: unhide Mainwindow")
					self.MAINWINDOW_HIDE = False
					self.mainwindow.show()
				else:
					self.debug(1,"def on_left_click: hide Mainwindow")
					self.mainwindow.hide()
					self.MAINWINDOW_HIDE = True
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
			except:
				self.debug(1,"def make_systray_menu: self.load_ovpn_server() failed")
			
			try:
				self.make_systray_server_menu()
			except:
				self.debug(1,"def make_systray_menu: self.make_systray_server_menu() failed")
			
			try:
				self.make_systray_openvpn_menu()
			except:
				self.debug(1,"def make_systray_menu: self.make_systray_openvpn_menu() failed")
			
			try:
				self.make_systray_bottom_menu()
			except:
				self.debug(1,"def make_systray_menu: self.make_systray_bottom_menu() failed")
			
			self.systray_menu.connect('enter-notify-event', self.systray_notify_event_enter,"systray_menu")
			self.systray_menu.show_all()
			self.systray_menu.popup(None, None, None, event, 0, 0)
		except:
			self.destroy_systray_menu()
			self.debug(1,"def make_systray_menu: failed")

	def make_systray_server_menu(self):
		self.debug(1,"def make_systray_server_menu()")
		self.COUNTRYNAMES = {'AF':_("Afghanistan"),'AL':_("Albania"),'DZ':_("Algeria"),'AS':_("American Samoa"),'AD':_("Andorra"),'AO':_("Angola"),'AI':_("Anguilla"),'AQ':_("Antarctica"),'AG':_("Antigua and Barbuda"),'AR':_("Argentina"),'AM':_("Armenia"),'AW':_("Aruba"),'AU':_("Australia"),'AT':_("Austria"),'AZ':_("Azerbaijan"),'BS':_("Bahamas"),'BH':_("Bahrain"),'BD':_("Bangladesh"),'BB':_("Barbados"),'BY':_("Belarus"),'BE':_("Belgium"),'BZ':_("Belize"),'BJ':_("Benin"),'BM':_("Bermuda"),'BT':_("Bhutan"),'BO':_("Plurinational State of Bolivia"),'BA':_("Bosnia and Herzegovina"),'BW':_("Botswana"),'BV':_("Bouvet Island"),'BR':_("Brazil"),'IO':_("British Indian Ocean Territory"),'BN':_("Brunei Darussalam"),'BG':_("Bulgaria"),'BF':_("Burkina Faso"),'BI':_("Burundi"),'KH':_("Cambodia"),'CM':_("Cameroon"),'CA':_("Canada"),'CV':_("Cape Verde"),'KY':_("Cayman Islands"),'CF':_("Central African Republic"),'TD':_("Chad"),'CL':_("Chile"),'CN':_("China"),'CX':_("Christmas Island"),'CC':_("Cocos (Keeling) Islands"),'CO':_("Colombia"),'KM':_("Comoros"),'CG':_("Congo"),'CD':_("the Democratic Republic of the Congo"),'CK':_("Cook Islands"),'CR':_("Costa Rica"),'HR':_("Croatia"),'CU':_("Cuba"),'CY':_("Cyprus"),'CZ':_("Czech Republic"),'DK':_("Denmark"),'DJ':_("Djibouti"),'DM':_("Dominica"),'DO':_("Dominican Republic"),'EC':_("Ecuador"),'EG':_("Egypt"),'SV':_("El Salvador"),'GQ':_("Equatorial Guinea"),'ER':_("Eritrea"),'EE':_("Estonia"),'ET':_("Ethiopia"),'FK':_("Falkland Islands (Malvinas)"),'FO':_("Faroe Islands"),'FJ':_("Fiji"),'FI':_("Finland"),'FR':_("France"),'GF':_("French Guiana"),'PF':_("French Polynesia"),'TF':_("French Southern Territories"),'GA':_("Gabon"),'GM':_("Gambia"),'GE':_("Georgia"),'DE':_("Germany"),'GH':_("Ghana"),'GI':_("Gibraltar"),'GR':_("Greece"),'GL':_("Greenland"),'GD':_("Grenada"),'GP':_("Guadeloupe"),'GU':_("Guam"),'GT':_("Guatemala"),'GG':_("Guernsey"),'GN':_("Guinea"),'GW':_("Guinea-Bissau"),'GY':_("Guyana"),'HT':_("Haiti"),'HM':_("Heard Island and McDonald Islands"),'VA':_("Holy See (Vatican City State)"),'HN':_("Honduras"),'HK':_("Hong Kong"),'HU':_("Hungary"),'IS':_("Iceland"),'IN':_("India"),'ID':_("Indonesia"),'IR':_("Islamic Republic of Iran"),'IQ':_("Iraq"),'IE':_("Ireland"),'IM':_("Isle of Man"),'IL':_("Israel"),'IT':_("Italy"),'JM':_("Jamaica"),'JP':_("Japan"),'JE':_("Jersey"),'JO':_("Jordan"),'KZ':_("Kazakhstan"),'KE':_("Kenya"),'KI':_("Kiribati"),'KW':_("Kuwait"),'KG':_("Kyrgyzstan"),'LV':_("Latvia"),'LB':_("Lebanon"),'LS':_("Lesotho"),'LR':_("Liberia"),'LY':_("Libyan Arab Jamahiriya"),'LI':_("Liechtenstein"),'LT':_("Lithuania"),'LU':_("Luxembourg"),'MO':_("Macao"),'MK':_("Macedonia"),'MG':_("Madagascar"),'MW':_("Malawi"),'MY':_("Malaysia"),'MV':_("Maldives"),'ML':_("Mali"),'MT':_("Malta"),'MH':_("Marshall Islands"),'MQ':_("Martinique"),'MR':_("Mauritania"),'MU':_("Mauritius"),'YT':_("Mayotte"),'MX':_("Mexico"),'FM':_("Federated States of Micronesia"),'MD':_("Republic of Moldova"),'MC':_("Monaco"),'MN':_("Mongolia"),'ME':_("Montenegro"),'MS':_("Montserrat"),'MA':_("Morocco"),'MZ':_("Mozambique"),'MM':_("Myanmar"),'NA':_("Namibia"),'NR':_("Nauru"),'NP':_("Nepal"),'NL':_("Netherlands"),'AN':_("Netherlands Antilles"),'NC':_("New Caledonia"),'NZ':_("New Zealand"),'NI':_("Nicaragua"),'NE':_("Niger"),'NG':_("Nigeria"),'NU':_("Niue"),'NF':_("Norfolk Island"),'MP':_("Northern Mariana Islands"),'NO':_("Norway"),'OM':_("Oman"),'PK':_("Pakistan"),'PW':_("Palau"),'PS':_("Occupied Palestinian Territory"),'PA':_("Panama"),'PG':_("Papua New Guinea"),'PY':_("Paraguay"),'PE':_("Peru"),'PH':_("Philippines"),'PN':_("Pitcairn"),'PL':_("Poland"),'PT':_("Portugal"),'PR':_("Puerto Rico"),'QA':_("Qatar"),'RE':_("Reunion"),'RO':_("Romania"),'RU':_("Russian Federation"),'RW':_("Rwanda"),'BL':_("Saint Barthelemy"),'SH':_("Saint Helena"),'KN':_("Saint Kitts and Nevis"),'LC':_("Saint Lucia"),'MF':_("Saint Martin (French part)"),'PM':_("Saint Pierre and Miquelon"),'VC':_("Saint Vincent and the Grenadines"),'WS':_("Samoa"),'SM':_("San Marino"),'ST':_("Sao Tome and Principe"),'SA':_("Saudi Arabia"),'SN':_("Senegal"),'RS':_("Serbia"),'SC':_("Seychelles"),'SL':_("Sierra Leone"),'SG':_("Singapore"),'SK':_("Slovakia"),'SI':_("Slovenia"),'SB':_("Solomon Islands"),'SO':_("Somalia"),'ZA':_("South Africa"),'GS':_("South Georgia and the South Sandwich Islands"),'ES':_("Spain"),'LK':_("Sri Lanka"),'SD':_("Sudan"),'SR':_("Suriname"),'SJ':_("Svalbard and Jan Mayen"),'SZ':_("Swaziland"),'SE':_("Sweden"),'CH':_("Switzerland"),'SY':_("Syrian Arab Republic"),'TW':_("Taiwan"),'TJ':_("Tajikistan"),'TZ':_("United Republic of Tanzania"),'TH':_("Thailand"),'TL':_("Timor-Leste"),'TG':_("Togo"),'TK':_("Tokelau"),'TO':_("Tonga"),'TT':_("Trinidad and Tobago"),'TN':_("Tunisia"),'TR':_("Turkey"),'TM':_("Turkmenistan"),'TC':_("Turks and Caicos Islands"),'TV':_("Tuvalu"),'UG':_("Uganda"),'UA':_("Ukraine"),'AE':_("United Arab Emirates"),'GB':_("United Kingdom"),'UK':_("United Kingdom"),'US':_("United States"),'UM':_("United States Minor Outlying Islands"),'UY':_("Uruguay"),'UZ':_("Uzbekistan"),'VU':_("Vanuatu"),'VE':_("Bolivarian Republic of Venezuela"),'VN':_("Viet Nam"),'VG':_("British Virgin Islands"),'VI':_("U.S. Virgin Islands"),'WF':_("Wallis and Futuna"),'EH':_("Western Sahara"),'YE':_("Yemen"),'ZM':_("Zambia"),'ZW':_("Zimbabwe")}
		if len(self.OVPN_SERVER) > 0:
			try:
				countrycodefrombefore = 0
				for servername in self.OVPN_SERVER:
					servershort = servername[:3]
					
					textstring = "%s [%s]:%s (%s)" % (servershort,self.OVPN_SERVER_INFO[servershort][0],self.OVPN_SERVER_INFO[servershort][1],self.OVPN_SERVER_INFO[servershort][2])
					countrycode = servershort[:2].lower()
					#print "string = %s, countrycode = %s" % (textstring,countrycode)
					
					if not countrycodefrombefore == countrycode:
						# create countrygroup menu
						countrycodefrombefore = countrycode
						cgmenu = Gtk.Menu()
						cgmenu.connect('enter-notify-event', self.systray_notify_event_enter,"sub_cgmenu")
						cgmenu.connect('leave-notify-event', self.systray_notify_event_leave,"sub_cgmenu")
						self.cgmenu = cgmenu
						try:
							countryname = self.COUNTRYNAMES[countrycode.upper()]
						except:
							countryname = countrycode.upper()
						
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
							except:
								self.debug(1,"def make_systray_server_menu: countrycode = '%s' failed" % (countrycode))
								self.destroy_systray_menu()
						except:
							self.destroy_systray_menu()
							self.debug(1,"def make_systray_server_menu: flagimg group1 failed")
					
					if self.OVPN_CONNECTEDto == servername:
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

			except:
				self.destroy_systray_menu()
				self.debug(1,"def make_systray_server_menu: failed")

	def make_systray_openvpn_menu(self):
		self.debug(1,"def make_systray_openvpn_menu()")
		if self.state_openvpn() == True:
			try:
				sep = Gtk.SeparatorMenuItem()
				servershort = self.OVPN_CONNECTEDto[:3]
				textstring = '%s @ [%s]:%s (%s)' % (servershort,self.OVPN_CONNECTEDtoIP,self.OVPN_CONNECTEDtoPort,self.OVPN_CONNECTEDtoProtocol.upper())
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
			except:
				self.debug(1,"def make_systray_openvpn_menu: failed")

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
		except:
			self.debug(1,"def make_systray_bottom_menu: accwindowentry failed")
		
		try:
			if self.SETTINGSWINDOW_OPEN == True:
				settwindowentry = Gtk.MenuItem(_("Close Settings"))
			else:
				settwindowentry = Gtk.MenuItem(_("Settings"))
			self.systray_menu.append(settwindowentry)
			settwindowentry.connect('button-release-event', self.show_settingswindow)
			settwindowentry.connect('leave-notify-event', self.systray_notify_event_leave,"settwindowentry")
		except:
			self.debug(1,"def make_systray_bottom_menu: settwindowentry failed")
		
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
			except:
				self.debug(1,"def make_systray_bottom_menu: about failed")
			
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

	def check_remote_update(self):
		self.debug(1,"def check_remote_update()")
		if self.timer_check_certdl_running == False:
			self.debug(1,"def check_remote_update: check_inet_connection() == True")
			try:
				thread_certdl = threading.Thread(name='certdl',target=self.inThread_timer_check_certdl)
				thread_certdl.daemon = True
				thread_certdl.start()
				threadid_certdl = threading.currentThread()
				self.debug(1,"def check_remote_update threadid_certdl = %s" %(threadid_certdl))
				return True
			except:
				self.debug(1,"starting thread_certdl failed")
		return False

	def inThread_timer_check_certdl(self):
		self.debug(1,"def inThread_timer_check_certdl()")
		try:
			self.timer_check_certdl_running = True
			try:
				self.load_ovpn_server()
				if len(self.OVPN_SERVER) == 0:
					self.reset_last_update()
			except:
				self.debug(1,"def inThread_timer_check_certdl: self.load_ovpn_server() failed")
			self.debug(1,"def inThread_timer_check_certdl()")
			self.STATE_CERTDL = "lastupdate"
			if self.API_REQUEST(API_ACTION = "lastupdate"):
				self.debug(1,"def inThread_timer_check_certdl: API_ACTION lastupdate")
				if self.check_last_server_update(self.curldata):
					self.STATE_CERTDL = "getconfigs"
					if self.API_REQUEST(API_ACTION = "getconfigs"):
						self.STATE_CERTDL = "requestcerts"
						if self.API_REQUEST(API_ACTION = "requestcerts"):
							self.STATUS_ICON_BLINK = 0
							self.STATE_CERTDL = "wait"
							self.API_COUNTDOWN = 180
							LAST_requestcerts = 0
							while not self.body == "ready":
								if self.API_COUNTDOWN <= 0:
									self.timer_check_certdl_running = False
									self.msgwarn(_("Update took too long...aborted!\nPlease retry in few minutes..."),_("Error: Update Timeout"))
									return False
								sleep = 0.5
								time.sleep(sleep)
								if LAST_requestcerts > 16:
									self.OVERWRITE_TRAYICON = self.systray_icon_syncupdate3
									self.API_REQUEST(API_ACTION = "requestcerts")
									self.OVERWRITE_TRAYICON = False
									LAST_requestcerts = 0
								else:
									LAST_requestcerts += sleep
								self.STATUS_ICON_BLINK += 1
								self.API_COUNTDOWN -= sleep
							# final step to download certs
							self.STATE_CERTDL = "getcerts"
							if self.API_REQUEST(API_ACTION = "getcerts"):
								self.STATE_CERTDL = "extract"
								if self.extract_ovpn():
									self.timer_check_certdl_running = False
									self.msgwarn(_("Certificates and Configs updated!"),_("oVPN Update OK!"))
									self.OVPN_SERVER = list()
									if self.load_ovpn_server() == True:
										self.rebuild_mainwindow()
									return True
								else:
									self.msgwarn(_("Extraction failed!"),_("Error: def inThread_timer_check_certdl"))
							else:
								self.msgwarn(_("Failed to download certificates"),_("Error: def inThread_timer_check_certdl"))
							# finish downloading certs
						else:
							self.msgwarn(_("Failed to request certificates!"),_("Error: def inThread_timer_check_certdl"))
					else:
						self.msgwarn(_("Failed to download configurations!"),_("Error: def inThread_timer_check_certdl"))
				else:
					self.timer_check_certdl_running = False
					self.msgwarn(_("No update needed!"),_("oVPN Update OK!"))
					return True
			#else:
			#	self.msgwarn(_("oVPN Update failed"),_("Error: def inThread_timer_check_certdl"))
		except:
			self.msgwarn(_("Failed to check for updates!"),_("Error: def inThread_timer_check_certdl"))
		self.timer_check_certdl_running = False
		return False

	def update_mwls(self):
		self.debug(1,"def update_mwls()")
		liststore = self.serverliststore
		debugupdate_mwls = False
		t1 = time.time()
		for row in liststore:
			server = row[2]
			if server in self.OVPN_SERVER:
				if debugupdate_mwls: self.debug(1,"def update_mwls: server '%s'" % (server))
				servershort = server[:3].upper()
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
							serverip4  = str(self.OVPN_SERVER_INFO[servershort][0])
							serverport = str(self.OVPN_SERVER_INFO[servershort][1])
							serverproto = str(self.OVPN_SERVER_INFO[servershort][2])
							servercipher = str(self.OVPN_SERVER_INFO[servershort][3])
							try:
								servermtu = str(self.OVPN_SERVER_INFO[servershort][4])
							except:
								servermtu = str(1500)
							if cellnumber == 0:
								if self.LOAD_SRVDATA == True and len(self.OVPN_SRV_DATA) >= 1:
									try:
										serverstatus = self.OVPN_SRV_DATA[servershort]["status"]
										if server == self.OVPN_CONNECTEDto:
											statusimg = self.decode_icon("shield_go")
										elif server == self.OVPN_FAV_SERVER:
											statusimg = self.decode_icon("star")
										elif serverstatus == "0":
											statusimg = self.decode_icon("bullet_red")
										elif serverstatus == "1":
											statusimg = self.decode_icon("bullet_green")
										elif serverstatus == "2":
											statusimg = self.decode_icon("bullet_white")
									except:
										self.debug(1,"def update_mwls: self.OVPN_SRV_DATA[%s]['status'] not found" % (servershort))
										break
								else:
									if server == self.OVPN_CONNECTEDto:
										statusimg = self.decode_icon("shield_go")
									elif server == self.OVPN_FAV_SERVER:
										statusimg = self.decode_icon("star")
									else:
										statusimg = self.decode_icon("bullet_white")
								try:
									liststore.set_value(iter,cellnumber,statusimg)
									row_changed += 1
								except:
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
							elif self.LOAD_SRVDATA == True and len(self.OVPN_SRV_DATA) >= 1:
								try:
									vlanip4 = str(self.OVPN_SRV_DATA[servershort]["vlanip4"])
									vlanip6 = str(self.OVPN_SRV_DATA[servershort]["vlanip6"])
									live = str("%s Mbps" % self.OVPN_SRV_DATA[servershort]["traffic"]["live"])
									uplink = str(self.OVPN_SRV_DATA[servershort]["traffic"]["uplink"])
									cpuinfo = str(self.OVPN_SRV_DATA[servershort]["info"]["cpu"])
									raminfo = str(self.OVPN_SRV_DATA[servershort]["info"]["ram"])
									hddinfo = str(self.OVPN_SRV_DATA[servershort]["info"]["hdd"])
									traffic = str(self.OVPN_SRV_DATA[servershort]["traffic"]["eth0"])
									cpuload = str(self.OVPN_SRV_DATA[servershort]["cpu"]["cpu-load"])
									cpuovpn = str(self.OVPN_SRV_DATA[servershort]["cpu"]["cpu-ovpn"])
									cpusshd = str(self.OVPN_SRV_DATA[servershort]["cpu"]["cpu-sshd"])
									cpusock = str(self.OVPN_SRV_DATA[servershort]["cpu"]["cpu-sock"])
									cpuhttp = str(self.OVPN_SRV_DATA[servershort]["cpu"]["cpu-http"])
									cputinc = str(self.OVPN_SRV_DATA[servershort]["cpu"]["cpu-tinc"])
									ping4 = str(self.OVPN_SRV_DATA[servershort]["pings"]["ipv4"])
									ping6 = str(self.OVPN_SRV_DATA[servershort]["pings"]["ipv6"])
									serverip6 = str(self.OVPN_SRV_DATA[servershort]["extip6"])
									
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
								except:
									pass
									# we may fail silently for private servers
									#self.debug(11,"def update_mwls: extended values '%s' failed" % (server))
						except:
							self.debug(1,"def update_mwls: #0 failed ")
						cellnumber += 1
						# end while cellnumber
					if row_changed >= 1:
						path = liststore.get_path(iter)
						liststore.row_changed(path,iter)
						self.debug(10,"def update_mwls: row_changed server '%s'" % (server))
		self.debug(1,"def update_mwls: return %s ms" % (int((time.time()-t1)*1000)))
		return

	def call_redraw_mainwindow(self):
		self.debug(1,"def call_redraw_mainwindow()")
		if self.MAINWINDOW_OPEN == True and self.MAINWINDOW_HIDE == False:
			self.statusbartext_from_before = False
			try:
				GLib.idle_add(self.update_mwls)
			except:
				self.debug(1,"def call_redraw_mainwindow: try #1 failed")

	def rebuild_mainwindow(self):
		GLib.idle_add(self.rebuild_mainwindow_glib)

	def rebuild_mainwindow_glib(self):
		if self.MAINWINDOW_OPEN == True and self.MAINWINDOW_HIDE == False:
			try:
				self.mainwindow.remove(self.mainwindow_vbox)
				self.debug(1,"def rebuild_mainwindow_glib: removed vbox from mainwindow")
			except:
				self.debug(1,"def rebuild_mainwindow_glib: no vbox in mainwindow")
				
			try:
				self.mainwindow_ovpn_server()
				self.fill_mainwindow_with_server()
				self.update_mwls()
				self.mainwindow.show_all()
				self.debug(1,"def rebuild_mainwindow_glib: filled window with data")
			except:
				self.debug(1,"def rebuild_mainwindow_glib: fill window failed")

	def show_mainwindow(self,widget,event):
		self.debug(1,"def show_mainwindow()")
		self.destroy_systray_menu()
		self.reset_load_remote_timer()
		self.statusbartext_from_before = False
		if self.MAINWINDOW_OPEN == False:
			self.load_ovpn_server()
			try:
				self.mainwindow = Gtk.Window(Gtk.WindowType.TOPLEVEL)
				self.mainwindow.set_position(Gtk.WindowPosition.CENTER)
				self.mainwindow.connect("destroy",self.cb_destroy_mainwindow)
				self.mainwindow.connect("key-release-event",self.cb_reset_load_remote_timer)
				self.mainwindow.set_title(_("oVPN Server - %s") % (CLIENT_STRING))
				self.mainwindow.set_icon(self.app_icon)
				self.rebuild_mainwindow()
				self.MAINWINDOW_OPEN = True
				return True
			except:
				self.MAINWINDOW_OPEN = False
				self.debug(1,"def show_mainwindow: mainwindow failed")
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
		except:
			return 0
			self.debug(1,"def cell_sort: failed")

	def cell_sort_traffic(self, treemodel, iter1, iter2, user_data):
		try:
			self.debug(16,"def cell_sort_traffic()")
			sort_column, _ = treemodel.get_sort_column_id()
			data1 = treemodel.get_value(iter1, sort_column)
			data2 = treemodel.get_value(iter2, sort_column)
			if data1 == "-1":
				data1 = "0 GB"
			if data2 == "-1":
				data2 = "0 GB"
			
			iter1 = data1.split(" ")
			number1 = float(iter1[0])
			byte1 = iter1[1]
			if byte1 == "TiB":
				number1 = number1 * 1024
			
			iter2 = data2.split(" ")
			number2 = float(iter2[0])
			byte2 = iter2[1]
			if byte2 == "TiB":
				number2 = number2 * 1024
			
			if float(number1) < float(number2):
				return -1
			elif float(number1) == float(number2):
				return 0
			else:
				return 1
		except:
			self.debug(1,"def cell_sort_traffic: failed")
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
		except:
			return 0
			self.debug(1,"def cell_sort_mbps: failed")

	def mainwindow_ovpn_server(self):
		self.debug(1,"def mainwindow_ovpn_server: go")
		self.mainwindow_vbox = Gtk.VBox(False,1)
		self.mainwindow.add(self.mainwindow_vbox)
		
		if self.OVPN_CONFIGVERSION == "23x":
			mode = "IPv4"
		elif self.OVPN_CONFIGVERSION == "23x46":
			mode = "IPv4 + IPv6"
		elif self.OVPN_CONFIGVERSION == "23x64":
			mode = "IPv6 + IPv4"
		self.debug(1,"def mainwindow_ovpn_server: go0")
		label = Gtk.Label(_("oVPN Server [ %s ]") % (mode))
		
		self.debug(1,"def mainwindow_ovpn_server: go1")
		try:
			self.serverliststore = Gtk.ListStore(GdkPixbuf.Pixbuf,GdkPixbuf.Pixbuf,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,GdkPixbuf.Pixbuf,str)
			self.debug(1,"def mainwindow_ovpn_server: go2")
		except:
			self.debug(1,"def mainwindow_ovpn_server: server-window failed")
		
		self.debug(1,"def mainwindow_ovpn_server: go3")
		self.treeview = Gtk.TreeView(self.serverliststore)
		self.treeview.connect("button-release-event",self.on_right_click_mainwindow)
		self.scrolledwindow = Gtk.ScrolledWindow()
		self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		self.scrolledwindow.set_size_request(64,48)
		self.debug(1,"def mainwindow_ovpn_server: go4")
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
		except:
			self.debug(1,"cell = Gtk.CellRendererPixbuf failed")
		
		## cell 0 == statusicon
		## cell 1 == flagicon
		cellnumber = 2
		for cellid,cellname in self.MAINWINDOW_CELLINDEX.items():
			if not cellnumber == 26:
				self.debug(0,"def cellname = '%s'" % (cellname))
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
					if cellnumber in self.MAINWINDOW_ALLOWCELLHIDE:
						if not cellnumber in self.MAINWINDOW_SHOWCELLS:
							column.set_visible(False)
						else:
							column.set_visible(True)
				self.treeview.append_column(column)
				cellnumber = cellnumber + 1
		
		# RightFlagIcon
		cell = Gtk.CellRendererPixbuf()
		cellnumber = 26
		column = Gtk.TreeViewColumn(' ',cell, pixbuf=cellnumber)
		column.set_fixed_width(30)
		if self.LOAD_SRVDATA == False:
			column.set_visible(False)
		else:
			if cellnumber in self.MAINWINDOW_ALLOWCELLHIDE:
					if not cellnumber in self.MAINWINDOW_SHOWCELLS:
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
		return

	def fill_mainwindow_with_server(self):
		for server in self.OVPN_SERVER:
			try:
				countrycode = server[:2].lower()
				servershort = server[:3].upper()
				statusimg = self.decode_icon("bullet_white")
				countryimg = self.decode_flag(countrycode)
				serverip4  = self.OVPN_SERVER_INFO[servershort][0]
				serverport = self.OVPN_SERVER_INFO[servershort][1]
				serverproto = self.OVPN_SERVER_INFO[servershort][2]
				servercipher = self.OVPN_SERVER_INFO[servershort][3]
				try:
					servermtu = self.OVPN_SERVER_INFO[servershort][4]
				except:
					servermtu = 1500
				self.serverliststore.append([statusimg,countryimg,str(server),str(serverip4),str("-1"),str(serverport),str(serverproto),str(servermtu),str(servercipher),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str("-1"),str(servershort),countryimg,str("")])
			except:
				self.debug(1,"def fill_mainwindow_with_server: server '%s' failed" % (server))

	def destroy_mainwindow(self):
		self.debug(1,"def destroy_mainwindow()")
		GLib.idle_add(self.mainwindow.destroy)
		#self.mainwindow.destroy()
		self.MAINWINDOW_OPEN = False
		self.MAINWINDOW_HIDE = False
		self.statusbar_text = False
		self.debug(1,"def destroy_mainwindow")

	def call_redraw_accwindow(self):
		self.debug(1,"def call_redraw_accwindow()")
		if self.ACCWINDOW_OPEN == True:
			try:
				self.accwindow.remove(self.accwindow_accinfo_vbox)
				self.accwindow_accinfo()
				self.debug(1,"def call_redraw_accwindow: True")
			except:
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
				self.accwindow.set_title(_("oVPN Account - %s") % (CLIENT_STRING))
				try:
					self.accwindow.set_icon(self.app_icon)
				except:
					pass
				self.accwindow.set_default_size(370,480)
				self.accwindow_accinfo()
				self.ACCWINDOW_OPEN = True
				self.reset_load_remote_timer()
				return True
			except:
				self.ACCWINDOW_OPEN = False
				self.debug(1,"def show_accwindow: accwindow failed")
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
				for key, value in sorted(self.OVPN_ACC_DATA.iteritems()):
					#print key
					value1 = False
					if key == "001":
						head = "User-ID"
					elif key == "002":
						head = "Service"
						if int(value) == ((2**31)-1):
							value1 = "Lifetime"
						else:
							value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S UTC+1')
					elif key == "003":
						head = "Balance EUR"
						value1 = round(int(value),0) / 100
					elif key == "004":
						head = "Saved Days"
					elif key == "005":
						head = "Last Login"
						value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S UTC+1')
					elif key == "006":
						head = "Login Count"
					elif key == "007":
						head = "Login Fail Count"
					elif key == "008":
						head = "Last Failed Login"
						value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S UTC+1')
					elif key == "009":
						head = "eMail verified"
					elif key == "010":
						head = "Last eMail sent"
					elif key == "020":
						head = "Last Update Request"
						value1 = datetime.fromtimestamp(int(value)).strftime('%d %b %Y %H:%M:%S UTC+1')
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
						for coin,addr in sorted(value.iteritems()):
							try:
								text = "%s: '%s'" % (coin.upper(),addr)
								#print text
								entry = Gtk.Entry()
								entry.set_max_length(128)
								entry.set_editable(0)
								entry.set_text(text)
								self.accwindow_accinfo_vbox.pack_start(entry,True,True,0)
							except:
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
					except:
						self.debug(1,"def accwindow_accinfo: accdata vbox.pack_start entry failed!")
			except:
				self.debug(1,"def accwindow_accinfo: self.OVPN_ACC_DATA failed")
		self.accwindow.show_all()
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
				self.settingswindow.set_title(_("oVPN Settings - %s") % (CLIENT_STRING))
				try:
					self.settingswindow.set_icon(self.app_icon)
				except:
					pass
				self.settingsnotebook = Gtk.Notebook()
				self.settingswindow.add(self.settingsnotebook)
				
				self.show_hide_security_window()
				self.show_hide_options_window()
				self.show_hide_updates_window()
				
				self.UPDATE_SWITCH = True
				self.settingswindow.show_all()
				self.SETTINGSWINDOW_OPEN = True
				return True
			except:
				self.SETTINGSWINDOW_OPEN = False
				self.debug(1,"def show_settingswindow: settingswindow failed")
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
		except:
			self.debug(1,"def show_settingswindow: nbpage0 failed")

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
			self.settings_options_switch_accinfo(self.nbpage1)
			self.settings_options_switch_srvinfo(self.nbpage1)
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
		except:
			self.debug(1,"def show_settingswindow: nbpage1 failed")

	def show_hide_updates_window(self):
		try:
			self.nbpage2 = Gtk.VBox(False,spacing=2)
			self.nbpage2.set_border_width(8)

			self.settings_updates_button_normalconf(self.nbpage2)
			self.settings_updates_button_forceconf(self.nbpage2)
			self.settings_options_button_ipv6(self.nbpage2)
			self.settings_options_button_networkadapter(self.nbpage2)
			self.settings_updates_button_apireset(self.nbpage2)

			self.settingsnotebook.append_page(self.nbpage2, Gtk.Label(_(" Updates ")))
		except:
			self.debug(1,"def show_settingswindow: nbpage2 failed")

	def show_hide_backup_window(self):
		try:
			self.load_firewall_backups()
			if len(self.FIREWALL_BACKUPS) > 0 and self.NO_WIN_FIREWALL == False and self.state_openvpn() == False:
				self.nbpage3 = Gtk.VBox(False,spacing=2)
				self.nbpage3.set_border_width(8)
				self.nbpage3.pack_start(Gtk.Label(label=_("Restore Firewall Backups\n")),False,False,0)
				self.settings_firewall_switch_backuprestore(self.nbpage3)
				self.settingsnotebook.append_page(self.nbpage3, Gtk.Label(_(" Backups ")))
		except:
			self.debug(1,"def show_hide_backup_window: nbpage3 failed")

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
		except:
			self.debug(1,"def settings_firewall_switch_nofw: failed")

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
		except:
			self.debug(1,"def settings_firewall_switch_tapblockoutbound: failed")

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
		except:
			self.debug(1,"def settings_firewall_switch_fwblockonexit: failed")

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
		except:
			self.debug(1,"def settings_firewall_switch_fwblockonexit: failed")

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
		except:
			self.debug(1,"def settings_firewall_switch_fwresetonconnect: failed")

	def cb_settings_firewall_switch_fwresetonconnect(self,switch,gparam):
		if self.NO_WIN_FIREWALL == True or self.state_openvpn() == True:
			self.UPDATE_SWITCH = True
			return
		self.debug(1,"def cb_settings_firewall_switch_fwresetonconnect()")
		if switch.get_active():
			self.WIN_RESET_FIREWALL = True
			if not self.win_firewall_export_on_start():
				self.msgwarn(_("Could not export Windows Firewall Backup!"),_("Error: Windows Firewall Backup failed"))
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
		except:
			self.debug(1,"def settings_firewall_switch_fwbackupmode: failed")

	def cb_settings_firewall_switch_fwbackupmode(self,switch,gparam):
		if self.NO_WIN_FIREWALL == True or self.state_openvpn() == True:
			self.UPDATE_SWITCH = True
			return
		self.debug(1,"def cb_settings_firewall_switch_fwbackupmode()")
		if switch.get_active():
			self.WIN_BACKUP_FIREWALL = True
			if not self.win_firewall_export_on_start():
				self.msgwarn(_("Could not export Windows Firewall Backup!"),_("Error: Windows Firewall Backup failed"))
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
		except:
			self.debug(1,"def settings_network_switch_nodns: failed")

	def cb_switch_nodns(self,switch,gparam):
		if self.state_openvpn() == True:
			self.UPDATE_SWITCH = True
			return
		self.debug(1,"def cb_switch_nodns()")
		if switch.get_active():
			self.NO_DNS_CHANGE = False
		else:
			self.win_netsh_restore_dns_from_backup()
			self.NO_DNS_CHANGE = True
		self.write_options_file()
		self.UPDATE_SWITCH = True

	def settings_network_switch_disableextifondisco(self,page):
		try:
			switch = Gtk.Switch()
			self.switch_disableextifondisco = switch
			checkbox_title = Gtk.Label(label=_("Disable '%s' on Disconnect (default: OFF)")%(self.WIN_EXT_DEVICE))
			if self.WIN_DISABLE_EXT_IF_ON_DISCO == True:
				switch.set_active(True)
			else:
				switch.set_active(False)
			switch.connect("notify::state", self.cb_settings_network_switch_disableextifondisco)
			page.pack_start(checkbox_title,False,False,0)
			page.pack_start(switch,False,False,0)
			page.pack_start(Gtk.Label(label=""),False,False,0)
		except:
			self.debug(1,"def settings_network_switch_disableextifondisco: failed")

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
			button.connect('clicked', self.cb_settings_firewall_switch_backuprestore, file)
			page.pack_start(button,False,False,0)
			page.pack_start(Gtk.Label(label=""),False,False,0)

	def cb_settings_firewall_switch_backuprestore(self, file):
		GLib.idle_add(self.cb_restore_firewallbackup, file)

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
		except:
			self.debug(1,"def settings_options_switch_updateovpnonstart: failed")

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
			if self.AUTOSTART == True:
				switch.set_active(True)
			else:
				switch.set_active(False)
			switch.connect("notify::state", self.cb_switch_autostart)
			page.pack_start(checkbox_title,False,False,0)
			page.pack_start(switch,False,False,0)
			page.pack_start(Gtk.Label(label=""),False,False,0)
		except:
			self.debug(1,"def settings_options_switch_autostart: failed")

	def cb_switch_autostart(self,switch,gparam):
		self.debug(1,"def cb_switch_autostart()")
		if switch.get_active():
			self.AUTOSTART = True
			schedule_task.set_task(self.DEBUG,self.AUTOSTART_DELAY_TIME)
		else:
			self.AUTOSTART = False
			schedule_task.delete_task(self.DEBUG)
		self.write_options_file()
		self.UPDATE_SWITCH = True

	def settings_options_combobox_time(self,page):
		try:
			self.debug(1,"def settings_options_combobox_time()")
			combobox_title = Gtk.Label(label=_("Delay in seconds"))
			combobox = Gtk.ComboBoxText.new()
			self.combobox_time = combobox
			for time in self.AUTOSTART_DELAY:
				combobox.append_text("%s"%(time))
			if self.AUTOSTART_DELAY_TIME == 10:
				active_item = 0
			if self.AUTOSTART_DELAY_TIME == 20:
				active_item = 1
			if self.AUTOSTART_DELAY_TIME == 30:
				active_item = 2
			if self.AUTOSTART_DELAY_TIME == 40:
				active_item = 3
			if self.AUTOSTART_DELAY_TIME == 50:
				active_item = 4
			if self.AUTOSTART_DELAY_TIME == 60:
				active_item = 5
			combobox.set_active(active_item)
			combobox.connect('changed',self.cb_time_switcher_changed)
			page.pack_start(combobox_title,False,False,0)
			page.pack_start(combobox,False,False,0)
			page.pack_start(Gtk.Label(label=""),False,False,0)
		except:
			self.debug(1,"def settings_options_combobox_time: failed")

	def cb_time_switcher_changed(self, combobox):
		self.debug(1,"def cb_time_switcher_changed()")
		model = combobox.get_model()
		index = combobox.get_active()
		if index > -1:
			self.AUTOSTART_DELAY_TIME = combobox.get_active_text()
			self.write_options_file()
			self.UPDATE_SWITCH = True
			self.debug(1,"def cb_time_switcher_changed: selected Time = '%s'" % (self.AUTOSTART_DELAY_TIME))
		return

	def settings_options_switch_accinfo(self,page):
		try:
			switch = Gtk.Switch()
			self.switch_accinfo = switch
			checkbox_title = Gtk.Label(label=_("Load Account Info (default: OFF)"))
			if self.LOAD_ACCDATA == True and not self.APIKEY == False:
				switch.set_active(True)
			else:
				switch.set_active(False)
			switch.connect("notify::state", self.cb_switch_accinfo)
			page.pack_start(checkbox_title,False,False,0)
			page.pack_start(switch,False,False,0)
			page.pack_start(Gtk.Label(label=""),False,False,0)
		except:
			self.debug(1,"def settings_options_switch_accinfo: failed")

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
			checkbox_title = Gtk.Label(label=_("Load Server Info (default: OFF)"))
			if self.LOAD_SRVDATA == True and not self.APIKEY == False:
				switch.set_active(True)
			else:
				switch.set_active(False)
			switch.connect("notify::state", self.cb_switch_srvinfo)
			page.pack_start(checkbox_title,False,False,0)
			page.pack_start(switch,False,False,0)
			page.pack_start(Gtk.Label(label=""),False,False,0)
		except:
			self.debug(1,"def settings_options_switch_srvinfo: failed")

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
			self.OVPN_SRV_DATA = {}
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
		except:
			self.debug(1,"def settings_options_switch_debugmode: failed")

	def cb_switch_debugmode(self,switch,gparam):
		self.debug(1,"def cb_switch_debugmode()")
		if switch.get_active():
			self.DEBUG = True
			self.msgwarn(_("Logfile:\n'%s'") % (self.DEBUG_LOGFILE),_("Debug Mode Enabled"))
		else:
			self.DEBUG = False
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
		if self.OVPN_CONFIGVERSION == "23x":
			button_title = Gtk.Label(label=_("Current: IPv4 Entry Server with Exit to IPv4 (standard)"))
			button = Gtk.Button(label=_("Use IPv4 Entry Server with Exits to IPv4 + IPv6"))
			button.connect('clicked', self.cb_settings_options_button_ipv6)
		elif self.OVPN_CONFIGVERSION  == "23x46":
			button_title = Gtk.Label(label=_("Current: IPv4 Entry Server with Exits to IPv4 + IPv6"))
			button = Gtk.Button(label=_("Use IPv4 Entry Server with Exit to IPv4 (standard)"))
			button.connect('clicked', self.cb_settings_options_button_ipv6)
		self.button_ipmode = button
		self.button_title = button_title
		page.pack_start(button_title,False,False,0)
		page.pack_start(button,False,False,0)
		page.pack_start(Gtk.Label(label=""),False,False,0)

	def cb_settings_options_button_ipv6(self,event):
		if not self.OVPN_CONFIGVERSION == "23x":
			GLib.idle_add(self.cb_change_ipmode1)
		if not self.OVPN_CONFIGVERSION  == "23x46":
			GLib.idle_add(self.cb_change_ipmode2)
		"""
		 *** fixme need isValueIPv6 first! ***
		if not self.OVPN_CONFIGVERSION == "23x64":
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
		except:
			self.debug(1,"def settings_options_combobox_theme: failed")

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
		except:
			self.debug(1,"def settings_options_combobox_icons: failed")

	def cb_icons_switcher_changed(self, combobox):
		self.debug(1,"def cb_icons_switcher_changed()")
		model = combobox.get_model()
		index = combobox.get_active()
		if index > -1:
			self.ICONS_THEME_frombefore = self.ICONS_THEME
			self.ICONS_THEME = combobox.get_active_text()
			if self.load_icons():
				self.write_options_file()
				self.debug(1,"def cb_icons_switcher_changed: selected Icons = '%s'" % (self.ICONS_THEME))
				self.ICON_CACHE_PIXBUF = {}
			else:
				self.debug(1,"def cb_icons_switcher_changed: failed icon theme = '%s', revert to '%s'" % (self.ICONS_THEME,self.ICONS_THEME_frombefore))
				self.ICONS_THEME = self.ICONS_THEME_frombefore
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
		except:
			self.debug(1,"def settings_options_combobox_theme: failed")

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
		except:
			self.debug(1,"def settings_options_combobox_language: failed")

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
		except:
			self.debug(1,"def settings_options_switch_disablequit: failed")

	def cb_settings_options_switch_disablequit(self,switch,gparam ):
		self.debug(1,"def cb_settings_options_switch_disablequit()")
		if switch.get_active():
			self.DISABLE_QUIT_ENTRY = True
		else:
			self.DISABLE_QUIT_ENTRY = False
		self.write_options_file()

	def settings_updates_button_normalconf(self,page):
		button = Gtk.Button(label=_("Normal Config Update"))
		button.connect('clicked', self.cb_settings_updates_button_normalconf)
		page.pack_start(button,False,False,0)
		page.pack_start(Gtk.Label(label=""),False,False,0)

	def cb_settings_updates_button_normalconf(self,event):
		self.cb_check_normal_update()

	def settings_updates_button_forceconf(self,page):
		button = Gtk.Button(label=_("Forced Config Update"))
		button.connect('clicked', self.cb_settings_updates_button_forceconf)
		page.pack_start(button,False,False,0)
		page.pack_start(Gtk.Label(label=""),False,False,0)

	def cb_settings_updates_button_forceconf(self,event):
		GLib.idle_add(self.cb_force_update)

	def settings_updates_button_apireset(self,page):
		button = Gtk.Button(label=_("Reset API-Login"))
		button.connect('clicked', self.cb_settings_updates_button_apireset)
		page.pack_start(button,False,False,0)
		page.pack_start(Gtk.Label(label=""),False,False,0)

	def cb_settings_updates_button_apireset(self,event):
		GLib.idle_add(self.dialog_apikey)

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
		self.MAINWINDOW_OPEN = False
		self.MAINWINDOW_HIDE = False

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
			print "def cb_del_dns: cbdata = '%s'" % (data)
			for name,value in data.iteritems():
				try:
					if value["primary"]["ip4"] == self.MYDNS[name]["primary"]["ip4"]:
						try:
							if self.isValueIPv4(self.MYDNS[name]["secondary"]["ip4"]):
								self.MYDNS[name]["primary"] = self.MYDNS[name]["secondary"]
								self.MYDNS[name]["secondary"] = {}
						except:
							self.MYDNS[name]["primary"] = {}
				except:
					pass
				
				try:
					if value["secondary"]["ip4"] == self.MYDNS[name]["secondary"]["ip4"]:
						self.MYDNS[name]["secondary"] = {}
				except:
					pass
			self.write_options_file()
			if self.OVPN_CONNECTEDto == name:
				self.debug(1,"def cb_set_dns: self.OVPN_CONNECTEDto = %s , name = %s" % (self.OVPN_CONNECTEDto,name))
				self.win_netsh_set_dns_ovpn()
			return True

	def cb_set_dns(self,widget,event,data):
		if event.button == 1:
			self.debug(1,"def cb_set_dns()")
			self.destroy_context_menu_servertab()
			for name,value in data.iteritems():
				self.debug(1,"def cb_set_dns: name '%s' value: '%s'" % (name,value))
				try:
					newpridns = value["primary"]["ip4"]
					if self.isValueIPv4(newpridns):
						print " set primary dns"
						try:
							print 'try: if newpridns == self.MYDNS[name]["secondary"]["ip4"]'
							if newpridns == self.MYDNS[name]["secondary"]["ip4"]:
								self.MYDNS[name]["secondary"] = {}
								self.debug('self.MYDNS[name]["secondary"] = {}')
						except:
							print "except1a"
				except:
					print "except1b"
				
				try:
					newsecdns = value["secondary"]["ip4"]
					if self.isValueIPv4(newsecdns):
						print " set secondary dns"
						try:
							print 'try: if newsecdns == self.MYDNS[name]["primary"]["ip4"]'
							if newsecdns == self.MYDNS[name]["primary"]["ip4"]:
								return False
						except:
							print "except2a"
				except:
					print "except2b"
				
				try:
					self.MYDNS[name].update(value)
				except:
					self.MYDNS[name] = value
				self.write_options_file()
				if self.OVPN_CONNECTEDto == name:
					self.debug(1,"def cb_set_dns: self.OVPN_CONNECTEDto = %s , name = %s" % (self.OVPN_CONNECTEDto,name))
					self.win_netsh_set_dns_ovpn()
					return True

	def destroy_context_menu_servertab(self):
		self.debug(1,"def destroy_context_menu_servertab()")
		try:
			self.dnssubmenu.hide()
			self.debug(1,"def destroy_context_menu_servertab: 0x0001")
		except:
			pass
		try:
			self.dnsmenu.hide()
			self.debug(1,"def destroy_context_menu_servertab: 0x0002")
		except:
			pass
		try:
			self.context_menu_servertab.hide()
			self.debug(1,"def destroy_context_menu_servertab: 0x0003")
		except:
			pass

	def destroy_systray_menu(self):
		self.debug(2,"def destroy_systray_menu()")
		try:
			GLib.idle_add(self.systray_menu.destroy)
			self.systray_menu = False
			self.MOUSE_IN_TRAY = 0
			self.debug(2,"def destroy_systray_menu: true")
		except:
			self.debug(7,"def destroy_systray_menu: failed")
			self.systray_menu = False

	def set_statusbar_text(self,text):
		self.debug(9,"def set_statusbar_text()")
		try:
			if not self.statusbar_text == False:
				GLib.idle_add(self.statusbar_text.set_label,text)
		except:
			self.debug(1,"def set_statusbar_text: text = '%s' failed" % (text))

	def cb_set_ovpn_favorite_server(self,widget,event,server):
		if event.button == 1:
			self.destroy_context_menu_servertab()
			self.debug(1,"def cb_set_ovpn_favorite_server()")
			try:
				self.OVPN_FAV_SERVER = server
				self.write_options_file()
				self.call_redraw_mainwindow()
				return True
			except:
				self.debug(1,"def cb_set_ovpn_favorite_server: failed")

	def cb_del_ovpn_favorite_server(self,widget,event,server):
		if event.button == 1:
			self.destroy_context_menu_servertab()
			self.debug(1,"def cb_del_ovpn_favorite_server()")
			try:
				self.OVPN_FAV_SERVER = False
				self.write_options_file()
				self.call_redraw_mainwindow()
				return True
			except:
				self.debug(1,"def cb_del_ovpn_favorite_server: failed")

	def cb_reset_load_remote_timer(self,widget,event):
		if event.keyval == Gdk.KEY_F5:
			self.call_redraw_mainwindow()
			self.debug(1,"def cb_reset_load_remote_timer == F5")
			self.reset_load_remote_timer()

	def reset_load_remote_timer(self):
		
		if self.LOAD_SRVDATA == True and self.MAINWINDOW_OPEN == True:
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
			self.destroy_context_menu_servertab()
			self.destroy_systray_menu()
			self.debug(1,"def cb_kill_openvpn()")
			self.OVPN_AUTO_CONNECT_ON_START = False
			self.debug(1,"def cb_kill_openvpn")
			killthread = threading.Thread(target=self.inThread_kill_openvpn)
			killthread.daemon = True
			killthread.start()

	def inThread_kill_openvpn(self):
		self.debug(1,"def inThread_kill_openvpn()")
		self.kill_openvpn()

	def cb_jump_openvpn(self,widget,event,server):
		if (widget == 0 and event == 0) or event.button == 1:
			self.OVPN_CALL_SRV = server
			self.debug(1,"def cb_jump_openvpn(%s)"%(server))
			self.destroy_systray_menu()
			self.destroy_context_menu_servertab()
			self.debug(1,"def cb_jump_openvpn: %s" % (server))
			jumpthread = threading.Thread(target=lambda server=server: self.inThread_jump_server(server))
			jumpthread.daemon = True
			jumpthread.start()

	def inThread_jump_server(self,server):
		self.debug(1,"def inThread_jump_server()")
		if self.inThread_jump_server_running == True:
			self.debug(1,"def inThread_jump_server: running ! return")
			return
		else:
			self.inThread_jump_server_running = True
			self.OVERWRITE_TRAYICON = True
			self.UPDATE_SWITCH = True
			self.debug(1,"def inThread_jump_server: server %s" % (server))
			if self.state_openvpn() == True:
				self.kill_openvpn()
			while not self.OVPN_THREADID == False:
				self.debug(1,"def cb_jump_openvpn: sleep while self.OVPN_THREADID not == False")
				time.sleep(1)
			self.call_openvpn(server)
			self.debug(1,"def inThread_jump_server: exit")

	def kill_openvpn(self):
		self.debug(1,"def kill_openvpn()")
		if self.state_openvpn() == False:
			return False
		if self.timer_check_certdl_running == True:
			self.msgwarn(_("Update is running."),_("Please wait!"))
			return False
		self.debug(1,"def kill_openvpn")
		try:
			self.del_ovpn_routes()
		except:
			pass
		try:
			if os.path.isfile(self.WIN_TASKKILL_EXE):
				ovpn_exe = self.OPENVPN_EXE.split("\\")[-1]
				string = '"%s" /F /IM %s' % (self.WIN_TASKKILL_EXE,ovpn_exe)
				exitcode = subprocess.check_call("%s" % (string),shell=True)
				self.debug(1,"def kill_openvpn: exitcode = %s" % (exitcode))
		except:
			self.debug(1,"def kill_openvpn: failed!")
			self.reset_ovpn_values_disconnected()

	def call_openvpn(self,server):
		self.debug(1,"def call_openvpn()")
		try:
			thread_openvpn = threading.Thread(target=lambda server=server: self.openvpn(server))
			thread_openvpn.start()
			self.debug(1,"def call_openvpn: thread_openvpn.start()")
		except:
			self.debug(1,"def call_openvpn: thread self.openvpn(server) failed")
			return False
		return True

	def state_openvpn(self):
		if self.STATE_OVPN == False and self.inThread_jump_server_running == False:
			return False
		if self.STATE_OVPN == True or self.inThread_jump_server_running == True:
			return True

	def openvpn(self,server):
		self.debug(1,"def openvpn()")
		while self.timer_check_certdl_running == True:
			self.debug(1,"def openvpn: sleep while timer_check_certdl_running")
			time.sleep(1)
		self.debug(1,"def openvpn: server = '%s'" % (server))
		if self.state_openvpn() == False:
			self.ovpn_server_UPPER = server
			self.ovpn_server_LOWER = server.lower()
			self.ovpn_server_config_file = "%s\\%s.ovpn" % (self.VPN_CFG,self.ovpn_server_UPPER)
			if os.path.isfile(self.ovpn_server_config_file):
				for line in open(self.ovpn_server_config_file):
					if "remote " in line:
						print(line)
						try:
							ip = line.split()[1]
							port = int(line.split()[2])
							# *** fixme *** need ipv6 check here
							if self.isValueIPv4(ip) and port > 0 and port < 65535:
								self.OVPN_CONNECTEDtoIP = ip
								self.OVPN_CONNECTEDtoPort = port
							#break
						except:
							self.debug(1,"Could not read Servers Remote-IP:Port from config: %s" % (self.ovpn_server_config_file))
							return False
					if "proto " in line:
						try:
							proto = line.split()[1]
							if proto.lower()  == "tcp" or proto.lower() == "udp":
								self.OVPN_CONNECTEDtoProtocol = proto
						except:
							self.debug(1,"Could not read Servers Protocol from config: %s" % (self.ovpn_server_config_file))
							return False
			else:
				self.debug(1,"Error: Server Config not found: '%s'" % (self.ovpn_server_config_file))
				return False
			self.ovpn_sessionlog = "%s\\ovpn.log" % (self.VPN_DIR)
			self.ovpn_server_dir = "%s\\%s" % (self.VPN_CFG,self.ovpn_server_LOWER)
			self.ovpn_cert_ca = "%s\\%s.crt" % (self.ovpn_server_dir,self.ovpn_server_LOWER)
			self.ovpn_tls_key = "%s\\%s.key" % (self.ovpn_server_dir,self.ovpn_server_LOWER)
			self.ovpn_cli_crt = "%s\\client%s.crt" % (self.ovpn_server_dir,self.USERID)
			self.ovpn_cli_key = "%s\\client%s.key" % (self.ovpn_server_dir,self.USERID)
			if not os.path.isdir(self.ovpn_server_dir) or \
				not os.path.isfile(self.ovpn_cert_ca) or \
				not os.path.isfile(self.ovpn_tls_key) or \
				not os.path.isfile(self.ovpn_cli_crt) or \
				not os.path.isfile(self.ovpn_cli_key):
					self.msgwarn(_("Files missing: '%s'") % (self.ovpn_server_dir),_("Error: Certs not found!"))
					self.reset_ovpn_values_disconnected()
					return False
			try:
				ovpn_string = '"%s" --config "%s" --ca "%s" --cert "%s" --key "%s" --tls-auth "%s" --dev-node "%s"' % (self.OPENVPN_EXE,self.ovpn_server_config_file,self.ovpn_cert_ca,self.ovpn_cli_crt,self.ovpn_cli_key,self.ovpn_tls_key,self.WIN_TAP_DEVICE)
				if self.DEBUG == True:
					self.ovpn_string = '%s --log "%s"' % (ovpn_string,self.ovpn_sessionlog)
				else:
					self.ovpn_string = ovpn_string
				thread_spawn_openvpn_process = threading.Thread(target=self.inThread_spawn_openvpn_process)
				thread_spawn_openvpn_process.start()
				self.OVPN_THREADID = threading.currentThread()
				self.debug(1,"Started: oVPN %s on Thread: %s" % (server,self.OVPN_THREADID))
			except:
				self.debug(1,"Error: Unable to start thread: oVPN %s " % (server))
				self.reset_ovpn_values_disconnected()
				return False
		else:
			self.debug(1,"def openvpn: self.OVPN_THREADID = %s" % (self.OVPN_THREADID))

	def inThread_spawn_openvpn_process(self):
		self.debug(1,"def inThread_spawn_openvpn_process")
		exitcode = False
		# *fixme* def win_select_networkadapter() fails if anybody changes interface name between start and connect
		#if not self.win_read_interfaces():
		#	self.reset_ovpn_values_disconnected()
		#	return False
		if not self.openvpn_check_files() == True:
			self.reset_ovpn_values_disconnected()
			return False
		if not self.win_firewall_start():
			self.msgwarn(_("Could not start Windows Firewall!"),_("Error: def inThread_spawn_openvpn_process"))
			self.reset_ovpn_values_disconnected()
			return False
		self.win_firewall_modify_rule(option="add")
		self.win_clear_ipv6()
		self.OVPN_CONNECTEDtime = int(time.time())
		self.OVPN_CONNECTEDto = self.OVPN_CALL_SRV
		self.OVPN_PING_STAT = -1
		self.OVPN_PING_LAST = -1
		self.NEXT_PING_EXEC = 0
		self.reset_load_remote_timer()
		self.OVERWRITE_TRAYICON = False
		self.STATE_OVPN = True
		if self.timer_ovpn_ping_running == False:
			self.debug(1,"def inThread_spawn_openvpn_process: self.inThread_timer_ovpn_ping")
			pingthread = threading.Thread(target=self.inThread_timer_ovpn_ping)
			pingthread.daemon = True
			pingthread.start()
		if self.TAP_BLOCKOUTBOUND == True:
			self.win_firewall_tap_blockoutbound()
		self.win_netsh_set_dns_ovpn()
		self.call_redraw_mainwindow()
		self.inThread_jump_server_running = False
		self.win_enable_ext_interface()
		try:
			exitcode = subprocess.check_call("%s" % (self.ovpn_string),shell=True,stdout=None,stderr=None)
		except:
			self.debug(1,"def inThread_spawn_openvpn_process: exited")
		self.win_disable_ext_interface()
		self.reset_ovpn_values_disconnected()
		self.call_redraw_mainwindow()
		return

	def reset_ovpn_values_disconnected(self):
		try:
			self.win_firewall_modify_rule(option="delete")
		except:
			self.debug(1,"def inThread_spawn_openvpn_process: self.win_firewall_modify_rule option=delete failed!")
		self.win_clear_ipv6()
		self.debug(1,"def reset_ovpn_values_after()")
		self.STATE_OVPN = False
		self.inThread_jump_server_running = False
		self.OVPN_CONNECTEDto = False
		self.OVPN_CONNECTEDtoIP = False
		self.OVPN_CONNECTEDtime = 0
		self.OVPN_CONNECTEDseconds = 0
		self.OVPN_THREADID = False
		self.OVPN_PING_STAT = 0
		self.OVPN_PING_LAST = 0
		self.OVPN_PING = list()
		self.UPDATE_SWITCH = True
		try:
			if os.path.isfile(self.ovpn_sessionlog):
				os.remove(self.ovpn_sessionlog)
		except:
			pass

	def inThread_timer_ovpn_ping(self):
		self.debug(10,"def inThread_timer_ovpn_ping()")
		if self.timer_ovpn_ping_running == False:
			self.OVPN_PING_STAT = -2
			self.timer_ovpn_ping_running = True
			self.debug(1,"def inThread_timer_ovpn_ping: start")
		
		if self.state_openvpn() == False:
			self.OVPN_PING_STAT = -1
			self.OVPN_PING = list()
			self.timer_ovpn_ping_running = False
			self.debug(1,"def inThread_timer_ovpn_ping: leaving")
			return
		
		elif self.STATE_OVPN == True:
			try:
				try:
					if self.NEXT_PING_EXEC < int(time.time()) and self.OVPN_CONNECTEDseconds > 5:
						PING = self.get_ovpn_ping()
						if PING > 0 and PING < 1:
							PING = round(PING,3)
						elif PING > 1:
							PING = int(round(PING,0))
						if PING > 0 and self.check_myip() == True:
							randint = random.randint(15,30)
							self.NEXT_PING_EXEC = int(time.time())+randint
							pingsum = 0
							if PING > 0:
								self.OVPN_PING.append(PING)
							if len(self.OVPN_PING) > 16:
								self.OVPN_PING.pop(0)
							if len(self.OVPN_PING) > 0:
								for pingi in self.OVPN_PING:
									pingsum += int(pingi)
								self.OVPN_PING_STAT = pingsum/len(self.OVPN_PING)
							self.OVPN_PING_LAST = PING
							self.OVPN_PING_DEAD_COUNT = 0
							self.debug(7,"def inThread_timer_ovpn_ping: %s ms, next in %s s"%(PING,randint))
						else:
							self.set_ovpn_ping_dead()
				except:
					self.set_ovpn_ping_dead()
			except:
				self.set_ovpn_ping_dead()
				self.debug(1,"def inThread_timer_ovpn_ping: failed")
			time.sleep(0.5)
			try:
				pingthread = threading.Thread(target=self.inThread_timer_ovpn_ping)
				pingthread.daemon = True
				pingthread.start()
				return True
			except:
				self.debug(1,"rejoin def inThread_timer_ovpn_ping() failed")

	def set_ovpn_ping_dead(self):
		self.OVPN_PING_LAST = -2
		self.NEXT_PING_EXEC = int(time.time())+5
		self.OVPN_PING_DEAD_COUNT += 1

	def get_ovpn_ping(self):
		self.debug(7,"def get_ovpn_ping()")
		try:
			ai_list = socket.getaddrinfo(self.GATEWAY_OVPN_IP4A,"443",socket.AF_UNSPEC,socket.SOCK_STREAM)
			for (family, socktype, proto, canon, sockaddr) in ai_list:
				try:
					t1 = time.time()
					s = socket.socket(family, socktype)
					s.connect(sockaddr)
					t2 = time.time()
					s.close()
					PING = (t2-t1)*1000
					if PING > 3000:
						PING = -2
					self.debug(7,"def get_ovpn_ping: %s ms" % (PING))
					return PING
				except:
					self.OVPN_PING_LAST = -2
					return -2
		except:
			self.debug(1,"def get_ovpn_ping: failed")

	def read_gateway_from_interface(self):
		try:
			DEVICE_GUID = winregs.get_networkadapter_guid(self.DEBUG,self.WIN_EXT_DEVICE)
			DEVICE_DATA = winregs.get_interface_infos_from_guid(self.DEBUG,DEVICE_GUID)
			GATEWAY_LOCAL = DEVICE_DATA["DefaultGateway"][0]
			if self.isValueIPv4(GATEWAY_LOCAL):
				self.GATEWAY_LOCAL = GATEWAY_LOCAL
				self.debug(1,"def read_gateway_from_interface: self.GATEWAY_LOCAL = '%s'" % (self.GATEWAY_LOCAL))
				return True
		except:
			self.debug(1,"def read_gateway_from_interface: failed")

	def read_gateway_from_routes(self):
		self.debug(1,"def read_gateway_from_routes()")
		try:
			output = self.win_return_route_cmd('print')
			for line in output:
				split = line.split()
				try:
					if self.OVPN_CONNECTEDtoIP in line:
						self.debug(1,"def read_ovpn_routes: self.OVPN_CONNECTEDtoIP in line '%s'" % (line))
						GATEWAY_LOCAL = line.split()[2]
						if self.isValueIPv4(GATEWAY_LOCAL) and GATEWAY_LOCAL == self.GATEWAY_LOCAL:
							self.debug(1,"def read_gateway_from_routes: self.GATEWAY_LOCAL = '%s'" % (self.GATEWAY_LOCAL))
							return True
						else:
							self.msgwarn(_("Read Gateway from Routes failed:\nGATEWAY_LOCAL: '%s' != self.GATEWAY_LOCAL: '%s'") % (GATEWAY_LOCAL,self.GATEWAY_LOCAL),_("Error"))
				except:
					pass
		except:
			self.debug(1,"def read_gateway_from_routes: failed")

	def del_ovpn_routes(self):
		self.debug(1,"def del_ovpn_routes()")
		try:
			if self.read_gateway_from_routes():
				if not self.GATEWAY_LOCAL == False:
					self.ROUTE_CMDLIST.append("DELETE %s MASK 255.255.255.255 %s" % (self.OVPN_CONNECTEDtoIP,self.GATEWAY_LOCAL))
					self.ROUTE_CMDLIST.append("DELETE 0.0.0.0 MASK 128.0.0.0 %s" % (self.GATEWAY_OVPN_IP4))
					self.ROUTE_CMDLIST.append("DELETE 128.0.0.0 MASK 128.0.0.0 %s" % (self.GATEWAY_OVPN_IP4))
					return self.win_join_route_cmd()
		except:
			self.debug(1,"def del_ovpn_routes: failed")

	def win_clear_ipv6(self):
		self.debug(1,"def win_clear_ipv6()")
		self.win_clear_ipv6_dns()
		self.win_clear_ipv6_addr()
		self.win_clear_ipv6_routes()

	def win_clear_ipv6_dns(self):
		self.debug(1,"def win_clear_ipv6_dns()")
		try:
			netshcmd = 'interface ipv6 show dnsservers "%s"' % (self.WIN_TAP_DEVICE)
			netsh_output = self.win_return_netsh_cmd(netshcmd)
			for line in netsh_output:
				#print line
				if " fd48:8bea:68a5:" in line:
					#print line
					ipv6addr = line.split("    ")[2]
					#print ipv6addr
					if ipv6addr.startswith("fd48:8bea:68a5:"):
						string = 'netsh.exe interface ipv6 delete dnsservers "%s" "%s"' % (self.WIN_TAP_DEVICE,ipv6addr)
						try:
							cmd = subprocess.check_output("%s" % (string),shell=True)
							self.debug(1,"def win_clear_ipv6_dns: removed %s '%s'" % (ipv6addr,string))
						except subprocess.CalledProcessError as e:
							self.debug(1,"def win_clear_ipv6_dns: %s %s failed '%s': %s" % (ipv6addr,self.WIN_TAP_DEVICE,string,e.output))
						except:
							self.debug(1,"def win_clear_ipv6_dns: %s %s failed '%s'" % (ipv6addr,self.WIN_TAP_DEVICE,string))
		except:
			self.debug(1,"def win_clear_ipv6_dns: failed")

	def win_clear_ipv6_addr(self):
		self.debug(1,"def win_clear_ipv6_addr()")
		try:
			try:
				netshcmd = 'interface ipv6 show addresses "%s"' % (self.WIN_TAP_DEVICE)
				netsh_output = self.win_return_netsh_cmd(netshcmd)
				try:
					for line in netsh_output:
						if " fd48:8bea:68a5:" in line or " fe80:" in line:
							self.debug(1,"def win_clear_ipv6_addr: found: line = '%s'" % (line))
							if not "%" in line:
								ipv6addr = line.split()[1]
								netshcmd = 'interface ipv6 delete address address="%s" interface="%s" store=active' % (ipv6addr,self.WIN_TAP_DEVICE)
								self.NETSH_CMDLIST.append(netshcmd)
					if len(self.NETSH_CMDLIST) > 0:
						self.win_join_netsh_cmd()
				except:
					self.debug(1,"def win_clear_ipv6_addr: failed #2")
			except:
				self.debug(1,"def win_clear_ipv6_addr: failed #1")
		except:
			self.debug(1,"def win_clear_ipv6_addr: failed")

	def win_clear_ipv6_routes(self):
		self.debug(1,"def win_clear_ipv6_routes()")
		try:
			netshcmd = 'interface ipv6 show route'
			netsh_output = self.win_return_netsh_cmd(netshcmd)
			for line in netsh_output:
				if " fd48:8bea:68a5:" in line or " fe80:" in line:
					self.debug(1,"def win_clear_ipv6_routes: found: line = '%s'" % (line))
					ipv6 = line.split()[3]
					output = self.win_return_route_cmd("DELETE %s" % (ipv6))
					self.debug(1,"def win_clear_ipv6_routes: %s %s" % (ipv6,output))
		except:
			self.debug(1,"def win_clear_ipv6_routes: failed")

	def win_netsh_set_dns_ovpn(self):
		self.debug(1,"def win_netsh_set_dns_ovpn()")
		if self.NO_DNS_CHANGE == True:
			self.debug(1,"def win_netsh_set_dns_ovpn: self.NO_DNS_CHANGE")
			return True
		if self.check_dns_is_whitelisted() == True:
			return True
		
		servername = self.OVPN_CONNECTEDto
		self.debug(1,"def win_netsh_set_dns_ovpn: servername = '%s'" % (servername))
		try:
			pridns = self.MYDNS[servername]["primary"]["ip4"]
			self.NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_EXT_DEVICE,pridns))
			self.NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_TAP_DEVICE,pridns))
			try:
				secdns = self.MYDNS[servername]["secondary"]["ip4"]
				self.NETSH_CMDLIST.append('interface ip add dnsservers "%s" %s index=2 no' % (self.WIN_EXT_DEVICE,secdns))
				self.NETSH_CMDLIST.append('interface ip add dnsservers "%s" %s index=2 no' % (self.WIN_TAP_DEVICE,secdns))
			except:
				self.debug(1,"def win_netsh_set_dns_ovpn: secdns not found")
		except:
			self.debug(1,"def win_netsh_set_dns_ovpn: pridns not found")
			if len(self.NETSH_CMDLIST) == 0:
				if self.GATEWAY_DNS1 == "127.0.0.1":
					setdns = "127.0.0.1"
				else:
					setdns = self.GATEWAY_OVPN_IP4A
				self.NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_EXT_DEVICE,setdns))
				self.NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no' % (self.WIN_TAP_DEVICE,setdns))
		if self.win_join_netsh_cmd() == True:
			self.WIN_DNS_CHANGED = True
			return True
		else:
			self.debug(1,"def win_netsh_set_dns_ovpn: failed!")

	def win_netsh_restore_dns_from_backup(self):
		self.debug(1,"def win_netsh_restore_dns_from_backup()")
		try:
			if self.NO_DNS_CHANGE == True:
				return True
			if self.WIN_DNS_CHANGED == False:
				return True
			if self.check_dns_is_whitelisted() == True:
				return True
			try:
				if self.WIN_EXT_DHCP_DNS == True:
					self.NETSH_CMDLIST.append('interface ip set dnsservers "%s" dhcp' % (self.WIN_EXT_DEVICE))
					if self.win_join_netsh_cmd():
						self.debug(1,"DNS restored to DHCP.")
						return True
					else:
						return False
			except:
				self.debug(1,"def win_netsh_restore_dns_from_backup: restore DHCP on IF: '%s' failed " % (self.WIN_EXT_DEVICE))
			
			try:
				if not self.GATEWAY_DNS1 == self.GATEWAY_OVPN_IP4A:
					self.NETSH_CMDLIST.append('interface ip set dnsservers "%s" static %s primary no'%(self.WIN_EXT_DEVICE,self.GATEWAY_DNS1))
					if self.win_join_netsh_cmd():
						self.debug(1,"Primary DNS restored to: %s"%(self.GATEWAY_DNS1))
						if self.GATEWAY_DNS2 == False:
							return True
						else:
							self.NETSH_CMDLIST.append('interface ip add dnsservers "%s" %s index=2 no'%(self.WIN_EXT_DEVICE,self.GATEWAY_DNS2))
							if self.win_join_netsh_cmd():
								self.debug(1,"Secondary DNS restored to %s" % (self.GATEWAY_DNS2))
								return True
							else:
								self.msgwarn(_("Error: Restore Secondary DNS to %s failed.") % (self.GATEWAY_DNS2),_("Error: DNS restore 2nd"))
								return False
					else:
						self.msgwarn(_("Error: Restore Primary DNS to %s failed.") % (self.GATEWAY_DNS1),_("Error: DNS restore 1st"))
						return False
				else:
					self.NETSH_CMDLIST.append('interface ip set dnsservers "%s" dhcp' % (self.WIN_EXT_DEVICE))
					if self.win_join_netsh_cmd():
						self.debug(1,"DNS restored to DHCP")
						return True
					else:
						return False
			except:
				self.debug(1,"def win_netsh_restore_dns_from_backup: Restore DNS failed")
		except:
			self.debug(1,"def win_netsh_restore_dns_from_backup: failed")

	def win_read_dns_from_interface(self,adaptername):
		DNS1 = False
		DNS2 = False
		try:
			DEVICE_GUID = winregs.get_networkadapter_guid(self.DEBUG,adaptername)
			DEVICE_DATA = winregs.get_interface_infos_from_guid(self.DEBUG,DEVICE_GUID)
			try:
				DNS1 = DEVICE_DATA['NameServer'].split(",")[0]
				if self.isValueIPv4(DNS1):
					self.debug(1,"def win_read_dns_from_interface(%s): 1st DNS '%s' backuped" % (adaptername,DNS1))
					try:
						DNS2 = DEVICE_DATA['NameServer'].split(",")[1]
						if self.isValueIPv4(DNS2):
							self.debug(1,"def win_read_dns_from_interface(%s): 2nd DNS '%s' backuped" % (adaptername,DNS2))
					except:
						pass
			except:
				pass
		except:
			pass
		return { "DNS1":DNS1,"DNS2":DNS2 }

	def win_read_dns_to_backup(self):
		self.debug(1,"def win_read_dns_to_backup()")
		try:
			if not self.WIN_EXT_DEVICE == False:
				data = False
				data = self.win_read_dns_from_interface(self.WIN_EXT_DEVICE)
				if not data == False and len(data) == 2:
					self.GATEWAY_DNS1 = data["DNS1"]
					self.GATEWAY_DNS2 = data["DNS2"]
					if not self.GATEWAY_DNS1 == False:
						self.WIN_EXT_DHCP_DNS = False
					else:
						self.WIN_EXT_DHCP_DNS = True
					return True
		except:
			return False

	def win_compare_dns(self):
		self.debug(1,"def win_compare_dns()")

	def load_ca_cert(self):
		self.debug(1,"def load_ca_cert()")
		if os.path.isfile(self.CA_FILE):
			self.CA_FILE_HASH = hashings.hash_sha512_file(self.DEBUG,self.CA_FILE)
			if self.CA_FILE_HASH == self.CA_FIXED_HASH:
				try:
					os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), self.CA_FILE)
					return True
				except:
					self.msgwarn(_("Error:\nSSL Root Certificate for %s not loaded %s") % (release_version.org_data()["VCP_DOMAIN"],self.CA_FILE),_("Error: SSL CA Cert #1"))
					return False
			else:
				self.msgwarn(_("Error:\nInvalid SSL Root Certificate for %s in:\n'%s'\nhash is:\n'%s'\nbut should be '%s'") % (release_version.org_data()["VCP_DOMAIN"],self.CA_FILE,self.CA_FILE_HASH,self.CA_FIXED_HASH),_("Error: SSL CA Cert #2"))
				return False
		else:
			self.msgwarn(_("Error:\nSSL Root Certificate for %s not found in:\n'%s'!") % (release_version.org_data()["VCP_DOMAIN"],self.CA_FILE),_("Error: SSL CA Cert #3"))
			return False

	def win_firewall_start(self):
		self.debug(1,"def win_firewall_start()")
		if self.NO_WIN_FIREWALL == True:
			return True
		if self.NO_DNS_CHANGE == False:
			self.win_ipconfig_flushdns()
		if self.WIN_RESET_FIREWALL == True:
			self.NETSH_CMDLIST.append("advfirewall reset")
		#self.NETSH_CMDLIST.append("advfirewall set privateprofile logging filename \"%s\"" % (self.pfw_private_log))
		#self.NETSH_CMDLIST.append("advfirewall set publicprofile logging filename \"%s\"" % (self.pfw_public_log))
		#self.NETSH_CMDLIST.append("advfirewall set domainprofile logging filename \"%s\"" % (self.pfw_domain_log))
		self.NETSH_CMDLIST.append("advfirewall set allprofiles state on")
		self.NETSH_CMDLIST.append("advfirewall set privateprofile firewallpolicy blockinbound,blockoutbound")
		self.NETSH_CMDLIST.append("advfirewall set domainprofile firewallpolicy blockinbound,blockoutbound")
		if self.TAP_BLOCKOUTBOUND == True:
			opt = "blockoutbound"
		else:
			opt = "allowoutbound"
		self.NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,%s" % (opt))
		if self.win_join_netsh_cmd():
			self.WIN_FIREWALL_STARTED = True
			return True

	def win_firewall_tap_blockoutbound(self):
		self.win_firewall_tap_blockoutbound_running = True
		self.debug(1,"def win_firewall_tap_blockoutbound()")
		try:
			if self.NO_WIN_FIREWALL == True:
				self.win_firewall_tap_blockoutbound_running = False
				return
			if self.TAP_BLOCKOUTBOUND == True:
				self.win_firewall_whitelist_ovpn_on_tap(option="delete")
				self.win_firewall_whitelist_ovpn_on_tap(option="add")
				self.NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,blockoutbound")
			else:
				self.win_firewall_whitelist_ovpn_on_tap(option="delete")
				self.NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,allowoutbound")
			self.win_join_netsh_cmd()
			self.debug(1,"Block outbound on TAP!\n\nAllow Whitelist to Internal oVPN Services\n\n'%s'\n\nSee all Rules:\n Windows Firewall with Advanced Security\n --> Outgoing Rules" % (self.WHITELIST_PUBLIC_PROFILE))
		except:
			self.debug(1,"def win_firewall_tap_blockoutbound: failed!")
		self.win_firewall_tap_blockoutbound_running = False

	def win_firewall_allowout(self):
		self.debug(1,"def win_firewall_allowout()")
		if self.NO_WIN_FIREWALL == True:
			return True	
		self.NETSH_CMDLIST.append("advfirewall set allprofiles state on")
		self.NETSH_CMDLIST.append("advfirewall set privateprofile firewallpolicy blockinbound,allowoutbound")
		self.NETSH_CMDLIST.append("advfirewall set domainprofile firewallpolicy blockinbound,allowoutbound")
		self.NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,allowoutbound")
		if self.win_join_netsh_cmd():
			self.WIN_FIREWALL_STARTED = True
			return True

	def win_firewall_block_on_exit(self):
		self.debug(1,"def win_firewall_block_on_exit()")
		if self.NO_WIN_FIREWALL == True:
			return True
		self.NETSH_CMDLIST.append("advfirewall set allprofiles state on")
		self.NETSH_CMDLIST.append("advfirewall set privateprofile firewallpolicy blockinbound,blockoutbound")
		self.NETSH_CMDLIST.append("advfirewall set domainprofile firewallpolicy blockinbound,blockoutbound")
		self.NETSH_CMDLIST.append("advfirewall set publicprofile firewallpolicy blockinbound,blockoutbound")
		return self.win_join_netsh_cmd()

	def win_firewall_whitelist_ovpn_on_tap(self,option):
		self.debug(1,"def win_firewall_whitelist_ovpn_on_tap()")
		if self.NO_WIN_FIREWALL == True:
			self.debug(1,"def win_firewall_whitelist_ovpn_on_tap: self.NO_WIN_FIREWALL == True")
			return True
		if option == "add":
			actionstring = "action=allow"
		elif option == "delete":
			actionstring = ""
		for entry,value in self.WHITELIST_PUBLIC_PROFILE.iteritems():
			ip = value["ip"]
			port = value["port"]
			protocol = value["proto"]
			
			rule_name = "(oVPN) Allow OUT on TAP: %s %s:%s %s" % (entry,ip,port,protocol)
			rule_string = "advfirewall firewall %s rule name=\"%s\" remoteip=\"%s\" remoteport=\"%s\" protocol=\"%s\" profile=public dir=out %s" % (option,rule_name,ip,port,protocol,actionstring)
			self.NETSH_CMDLIST.append(rule_string)
			self.debug(1,"Whitelist: %s %s %s %s" % (entry,ip,port,protocol))
		self.win_join_netsh_cmd()
		return True

	def win_firewall_add_rule_to_vcp(self,option):
		if self.NO_WIN_FIREWALL == True:
			return True
		self.debug(1,"def win_firewall_add_rule_to_vcp(%s)"%(option))
		if option == "add":
			actionstring = "action=allow"
		elif option == "delete":
			actionstring = ""
		url = "https://%s" % (release_version.org_data()["VCP_DOMAIN"])
		ips = ["178.17.170.116",self.GATEWAY_OVPN_IP4A]
		port = 443
		protocol = "tcp"
		for ip in ips:
			rule_name = "(oVPN) Allow OUT on EXT: %s %s:%s %s" % (url,ip,port,protocol)
			rule_string = "advfirewall firewall %s rule name=\"%s\" remoteip=\"%s\" remoteport=\"%s\" protocol=\"%s\" profile=private dir=out %s" % (option,rule_name,ip,port,protocol,actionstring)
			self.NETSH_CMDLIST.append(rule_string)
		if self.win_join_netsh_cmd():
			self.WIN_FIREWALL_ADDED_RULE_TO_VCP = True
			return True

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
		self.NETSH_CMDLIST.append('advfirewall export "%s"' % (self.pfw_bak))
		return self.win_join_netsh_cmd()

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
			self.NETSH_CMDLIST.append("advfirewall reset")
			if os.path.isfile(self.pfw_bak):
				self.NETSH_CMDLIST.append('advfirewall import "%s"' % (self.pfw_bak))
			return self.win_join_netsh_cmd()

	def win_enable_tap_interface(self):
		self.debug(1,"def win_enable_tap_interface()")
		self.NETSH_CMDLIST.append('interface set interface "%s" ENABLED'%(self.WIN_TAP_DEVICE))
		return self.win_join_netsh_cmd()

	def win_disable_ext_interface(self):
		self.debug(1,"def win_disable_ext_interface()")
		if self.WIN_DISABLE_EXT_IF_ON_DISCO == True:
			self.NETSH_CMDLIST.append('interface set interface "%s" DISABLED'%(self.WIN_EXT_DEVICE))
			return self.win_join_netsh_cmd()

	def win_enable_ext_interface(self):
		self.debug(1,"def win_enable_ext_interface()")
		self.NETSH_CMDLIST.append('interface set interface "%s" ENABLED'%(self.WIN_EXT_DEVICE))
		self.win_join_netsh_cmd()

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
			rule_name = "Allow OUT oVPN-IP %s to Port %s Protocol %s" % (self.OVPN_CONNECTEDtoIP,self.OVPN_CONNECTEDtoPort,self.OVPN_CONNECTEDtoProtocol)
			if option == "add":
				rule_string = "advfirewall firewall %s rule name=\"%s\" remoteip=\"%s\" remoteport=\"%s\" protocol=\"%s\" profile=private dir=out action=allow" % (option,rule_name,self.OVPN_CONNECTEDtoIP,self.OVPN_CONNECTEDtoPort,self.OVPN_CONNECTEDtoProtocol)
			if option == "delete":
				rule_string = "advfirewall firewall %s rule name=\"%s\"" % (option,rule_name)
			#self.debug(1,"def pfw: %s"%(rule_string))
			self.NETSH_CMDLIST.append(rule_string)
			return self.win_join_netsh_cmd()
		except:
			self.debug(1,"def win_firewall_modify_rule: option = '%s' failed" %(option))

	def win_return_netsh_cmd(self,cmd):
		self.debug(1,"def win_return_netsh_cmd()")
		if os.path.isfile(self.WIN_NETSH_EXE):
			netshcmd = '%s %s' % (self.WIN_NETSH_EXE,cmd)
			try: 
				read = subprocess.check_output('%s' % (netshcmd),shell=True)
				output = read.strip().decode('cp1258','ignore').strip(' ').split('\r\n')
				self.debug(5,"def win_return_netsh_cmd: output = '%s'" % (output))
				return output
			except:
				self.debug(1,"def win_return_netsh_cmd: '%s' failed" % (netshcmd))
		else:
			self.errorquit(text=_("Error: netsh.exe not found!"))

	def win_join_netsh_cmd(self):
		self.debug(1,"def win_join_netsh_cmd()")
		if os.path.isfile(self.WIN_NETSH_EXE):
			i=0
			for cmd in self.NETSH_CMDLIST:
				netshcmd = '"%s" %s' % (self.WIN_NETSH_EXE,cmd)
				try: 
					exitcode = subprocess.call('%s' % (netshcmd),shell=True)
					if exitcode == 0:
						self.debug(1,"netshOK: '%s': exitcode = %s" % (netshcmd,exitcode))
						i+=1
					else:
						self.debug(1,"netshERROR: '%s': exitcode = %s" % (netshcmd,exitcode))
				except:
					self.debug(1,"def win_join_netsh_cmd: '%s' failed" % (netshcmd))
			if len(self.NETSH_CMDLIST) == i:
				self.NETSH_CMDLIST = list()
				return True
			else:
				self.NETSH_CMDLIST = list()
				return False
		else:
			self.errorquit(text=_("Error: netsh.exe not found!"))

	def win_return_route_cmd(self,cmd):
		self.debug(1,"def win_return_route_cmd()")
		if os.path.isfile(self.WIN_ROUTE_EXE):
			routecmd = '"%s" %s' % (self.WIN_ROUTE_EXE,cmd)
			try: 
				read = subprocess.check_output('%s' % (routecmd),shell=True)
				output = read.strip().decode('cp1258','ignore').strip(' ').split('\r\n')
				self.debug(5,"def win_return_route_cmd: output = '%s'" % (output))
				return output
			except:
				self.debug(1,"def win_return_route_cmd: '%s' failed" % (routecmd))
				return False
		else:
			self.errorquit(text=_("Error: route.exe not found!"))

	def win_join_route_cmd(self):
		self.debug(1,"def win_join_route_cmd()")
		if os.path.isfile(self.WIN_ROUTE_EXE):
			i=0
			for cmd in self.ROUTE_CMDLIST:
				routecmd = '"%s" %s' % (self.WIN_ROUTE_EXE,cmd)
				try: 
					exitcode = subprocess.call('%s' % (routecmd),shell=True)
					if exitcode == 0:
						self.debug(1,"routeOK: '%s': exitcode = %s" % (routecmd,exitcode))
						i+=1
					else:
						self.debug(1,"routeERROR: '%s': exitcode = %s" % (routecmd,exitcode))
				except:
					self.debug(1,"def win_join_route_cmd: '%s' failed" % (routecmd))
			if len(self.ROUTE_CMDLIST) == i:
				self.ROUTE_CMDLIST = list()
				return True
			else:
				self.ROUTE_CMDLIST = list()
				return False
		else:
			self.errorquit(text=_("Error: route.exe not found!"))

	def win_ipconfig_flushdns(self):
		self.debug(1,"def win_ipconfig_flushdns()")
		if os.path.isfile(self.WIN_IPCONFIG_EXE):
			try: 
				cmdstring = '"%s" /flushdns' % (self.WIN_IPCONFIG_EXE)
				exitcode = subprocess.call("%s" % (cmdstring),shell=True)
				if exitcode == 0:
					self.debug(1,"%s: exitcode = %s" % (cmdstring,exitcode))
					return True
				else:
					self.debug(1,"%s: exitcode = %s" % (cmdstring,exitcode))
			except:
				self.debug(1,"def win_join_ipconfig_cmd: '%s' failed" % (cmdstring))
		else:
			self.errorquit(text=_("ipconfig.exe not found!"))

	def win_ipconfig_displaydns(self):
		self.debug(1,"def win_ipconfig_displaydns()")
		if os.path.isfile(self.WIN_IPCONFIG_EXE):
			try: 
				cmdstring = '"%s" /displaydns' % (self.WIN_IPCONFIG_EXE)
				out = subprocess.check_output("%s" % (cmdstring),shell=True)
				return out
			except:
				self.debug(1,"def win_ipconfig_displaydns: failed" % (cmdstring))
		else:
			self.errorquit(text=_("ipconfig.exe not found!"))

	def isValueIPv4(self,value):
		#self.debug(99,"def isValueIPv4()")
		try:
			if len(value.split('.')) == 4:
				for n in value.split('.'):
					if n.isdigit():
						self.debug(50,"def isValueIPv4: n = %s"%(n))
						if not n >= 0 and not n <= 255:
							return False
				return True
		except:
			return False

	# *** fixme ***
	def isValueIPv6(self,value):
		self.debug(1,"def isValueIPv6()")
		return True

	def form_ask_userid(self):
		self.debug(1,"def form_ask_userid()")
		try:
			self.dialog_form_ask_userid.destroy()
		except:
			pass
		try:
			dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK_CANCEL)
			dialogWindow.set_position(Gtk.WindowPosition.CENTER)
			self.dialog_form_ask_userid = dialogWindow
			try:
				dialogWindow.set_icon(self.app_icon)
			except:
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
		except:
			self.debug(1,"def form_ask_userid: Failed")

	def response_dialog_apilogin(self, dialog, response_id, useridEntry, apikeyEntry, checkbox):
		self.debug(1,"response_dialog_apilogin()")
		if response_id == Gtk.ResponseType.CANCEL:
			self.debug(1,"def response_dialog_apilogin: response_id == Gtk.ResponseType.CANCEL")
			dialog.destroy()
			return
		elif response_id == Gtk.ResponseType.OK:
			self.debug(1,"def response_dialog_apilogin: Gtk.ResponseType.OK self.USERID = '%s'"%(self.USERID))
			if self.USERID == False:
				userid = useridEntry.get_text().rstrip()
			else:
				userid = self.USERID
			apikey = apikeyEntry.get_text().rstrip()
			self.debug(1,"def response_dialog_apilogin: Gtk.ResponseType.OK userid = '%s'"%(userid))
			if userid.isdigit() and userid > 1 and (len(apikey) == 0 or (len(apikey) == 128 and apikey.isalnum())) and (self.USERID == False or self.USERID == userid):
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
								self.API_REQUEST("auth")
								self.APIKEY = apikey
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
				self.check_remote_update()
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
		self.debug(1,"def cb_check_normal_update()")
		if self.check_inet_connection() == False:
			self.msgwarn(_("Could not connect to %s") % (API_DOMAIN),_("Error: Update failed"))
			return False
		if self.check_remote_update():
			self.debug(1,"def cb_check_normal_update: self.check_remote_update() == True")
			return True

	def cb_force_update(self):
		self.debug(1,"def cb_force_update()")
		if self.check_inet_connection() == False:
			self.msgwarn(_("Could not connect to %s") % (API_DOMAIN),_("Error: Update failed"))
			return False
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

	def cb_extserverview(self,widget,event):
		if event.button == 1:
			self.debug(1,"def cb_extserverview()")
			if self.LOAD_SRVDATA == False and not self.APIKEY == False:
				self.LOAD_SRVDATA = True
				self.LAST_OVPN_SRV_DATA_UPDATE = 0
				self.OVPN_SRV_DATA = {}
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
			except:
				actualwidth = 0
				actualheigt = 0
			dialogWindow.set_position(Gtk.WindowPosition.CENTER)
			dialogWindow.set_transient_for(self.window)
			dialogWindow.set_border_width(8)
			try:
				dialogWindow.set_icon(self.app_icon)
			except:
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
				print "response: btn cancel %s" % (response)
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
				print "response: btn cancel %s" % (response)
				return False
			elif response == Gtk.ResponseType.OK:
				try:
					seconds = int(Entry.get_text().rstrip())
				except:
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
				for cellid in self.MAINWINDOW_ALLOWCELLHIDE:
					cellname = self.MAINWINDOW_CELLINDEX[cellid]
					print cellname
					button = Gtk.ToggleButton(label=cellname)
					if cellid in self.MAINWINDOW_SHOWCELLS:
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
		except:
			self.debug(1,"def cb_hide_cells: failed")
			self.HIDECELLSWINDOW_OPEN = False

	def cb_hide_cells2(self,button,cellid):
		self.debug(1,"def cb_hide_cells2() cellid = '%s'"%(cellid))
		if cellid in self.MAINWINDOW_ALLOWCELLHIDE:
			if cellid in self.MAINWINDOW_SHOWCELLS:
				self.MAINWINDOW_SHOWCELLS.remove(cellid)
				self.debug(1,"def cb_hide_cells2: remove cellid = '%s'"%(cellid))
			else:
				self.MAINWINDOW_SHOWCELLS.append(cellid)
				self.debug(1,"def cb_hide_cells2: append cellid = '%s'"%(cellid))
			self.write_options_file()
			self.rebuild_mainwindow()

	def cb_change_ipmode1(self):
		self.debug(1,"def cb_change_ipmode1()")
		self.OVPN_CONFIGVERSION = "23x"
		self.write_options_file()
		self.read_options_file()
		self.OVPN_SERVER = {}
		self.load_ovpn_server()
		if len(self.OVPN_SERVER) == 0:
			self.cb_check_normal_update()
		self.rebuild_mainwindow()
		self.UPDATE_SWITCH = True

	def cb_change_ipmode2(self):
		self.debug(1,"def cb_change_ipmode2()")
		self.OVPN_CONFIGVERSION = "23x46"
		self.write_options_file()
		self.read_options_file()
		self.OVPN_SERVER = {}
		self.load_ovpn_server()
		if len(self.OVPN_SERVER) == 0:
			self.msgwarn(_("Changed Option:\n\nUse 'Forced Config Update' to get new configs!\n\nYou have to join 'IPv6 Beta' on https://%s to use any IPv6 options!") % (release_version.org_data()["VCP_DOMAIN"]),_("Switched to IPv4+6"))
			self.cb_check_normal_update()
		self.rebuild_mainwindow()
		self.UPDATE_SWITCH = True

	# *** fixme: need isValueIPv6 first! ***
	def cb_change_ipmode3(self):
		self.debug(1,"def cb_change_ipmode3()")
		return True
		self.OVPN_CONFIGVERSION = "23x64"
		self.write_options_file()
		self.read_options_file()
		self.OVPN_SERVER = {}
		self.load_ovpn_server()
		if len(self.OVPN_SERVER) == 0:
			self.msgwarn(_("Changed Option:\n\nUse 'Forced Config Update' to get new configs!\n\nYou have to join 'IPv6 Beta' on https://%s to use any IPv6 options!") % (release_version.org_data()["VCP_DOMAIN"]),_("Switched to IPv6+4"))
			self.cb_check_normal_update()
		self.rebuild_mainwindow()
		self.UPDATE_SWITCH = True

	def cb_restore_firewallbackup(self,file):
		self.debug(1,"def cb_restore_firewallbackup()")
		fwbak = "%s\\%s" % (self.pfw_dir,file)
		if os.path.isfile(fwbak):
			self.debug(1,"def cb_restore_firewallbackup: %s" % (fwbak))
			self.win_firewall_export_on_start()
			self.NETSH_CMDLIST.append('advfirewall import "%s"' % (fwbak))
			return self.win_join_netsh_cmd()

	def delete_dir(self,path):
		self.debug(1,"def delete_dir()")
		if self.OS == "win32":
			string = 'rmdir /S /Q "%s"' % (path)
			self.debug(1,"def delete_dir: %s" % (string))
			subprocess.check_output("%s" % (string),shell=True)

	""" *fixme* move to openvpn.py """
	def extract_ovpn(self):
		self.debug(1,"def extract_ovpn()")
		try:
			if os.path.isfile(self.zip_cfg) and os.path.isfile(self.zip_crt):
				z1file = zipfile.ZipFile(self.zip_cfg)
				z2file = zipfile.ZipFile(self.zip_crt)
				if os.path.isdir(self.VPN_CFG):
					self.debug(1,"def extract_ovpn: os.path.isdir(%s)"%(self.VPN_CFG))
					self.delete_dir(self.VPN_CFG)
				if not os.path.isdir(self.VPN_CFG):
					try:
						os.mkdir(self.VPN_CFG)
						self.debug(1,"def extract_ovpn: os.mkdir(%s)"%(self.VPN_CFG))
					except:
						self.debug(1,"def extract_ovpn: %s not found, create failed."%(self.VPN_CFG))
				try:
					z1file.extractall(self.VPN_CFG)
					z2file.extractall(self.VPN_CFG)
					if self.write_last_update():
						self.debug(1,"Certificates and Configs extracted.")
						return True
				except:
					self.debug(1,"Error on extracting Certificates and Configs!")
					return False
		except:
			self.debug(1,"def extract_ovpn: failed")

	def get_random_string(self):
		int = random.randint(16,32)
		rand = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(int))
		return rand

	def make_useragent(self):
		self.debug(99,"def make_useragent()")
		user_agent = 007
		rand = self.get_random_string()
		try:
			version = release_version.version_data()["VERSION"]
			versionint = 0
			
			try:
				split = version.split(".")
				versionint = "%s%s%s" % (split[0],split[1],split[2])
			except:
				self.debug(1,"def make_useragent: version.split failed")
			
			if versionint > 0:
				version = versionint
			user_agent = "client/%s" % (version)
		except:
			self.debug(1,"def make_useragent: construct user-agent failed")
		headers = { 'User-Agent':"%s/%s" % (user_agent,rand) }
		self.debug(99,"def make_useragent: return headers = '%s'" % (headers))
		return headers

	def API_REQUEST(self,API_ACTION):
		self.debug(1,"def API_REQUEST(%s)"%(API_ACTION))
		if self.APIKEY == False:
			self.msgwarn(_("No API-Key!"),_("No API-Key!"))
			return False
		
		if API_ACTION == "auth":
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION }
			
		if API_ACTION == "lastupdate":
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION }
		
		if API_ACTION == "getconfigs":
			if os.path.isfile(self.zip_cfg): os.remove(self.zip_cfg)
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION, 'version' : self.OVPN_CONFIGVERSION, 'type' : 'win' }	
		
		if API_ACTION == "requestcerts":
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION }
		
		if API_ACTION == "getcerts":
			if os.path.isfile(self.zip_crt): os.remove(self.zip_crt)
			values = {'uid' : self.USERID, 'apikey' : self.APIKEY, 'action' : API_ACTION }
		
		self.body = False
		
		self.debug(1,"def API_REQUEST: API_ACTION = %s" % (API_ACTION))
		
		try:
			HEADERS = self.make_useragent()
			r = requests.post(url=self.APIURL,data=values,headers=HEADERS)
			
			if API_ACTION == "getconfigs" or API_ACTION == "getcerts":
				self.body = r.content
			else:
				self.body = r.text
			
			if self.body == "AUTHERROR":
				self.msgwarn(_("Invalid User-ID or API-Key or Account expired!"),_("API Login Error"))
				return False
			elif API_ACTION == "auth" and self.body == "AUTHOK:True":
				self.msgwarn(_("API Login OK!"),_("API Login OK!"))
				return True
			
			if self.body.isalnum() and len(self.body) <= 128:
				self.debug(1,"def API_REQUEST: self.body = %s"%(self.body))
		
		except:
			self.msgwarn(_("API requests on: %s failed!") % (API_ACTION),_("Error: def API_REQUEST"))
			return False
		
		if not self.body == False:
			
			if not self.body == "AUTHERROR":
				self.curldata = self.body.split(":")
				if self.curldata[0] == "AUTHOK":
					self.curldata = self.curldata[1]
					self.debug(1,"def API_REQUEST: self.curldata = '%s'" % (self.curldata))
					return True
			else:
				self.msgwarn(_("Invalid User-ID or API-Key or Account expired!"),_("Error: def API_REQUEST"))
				self.body = False
				self.timer_check_certdl_running = False
				return False
			
			if API_ACTION == "getconfigs":
				try:
					fp = open(self.zip_cfg, "wb")
					fp.write(self.body)
					fp.close()
					return True
				except:
					return False
			
			elif API_ACTION == "getcerts":
				try:
					fp = open(self.zip_crt, "wb")
					fp.write(self.body)
					fp.close()
					return True
				except:
					return False
			
			if API_ACTION == "requestcerts":
				if self.body == "ready" or self.body == "wait" or self.body == "submitted":
					return True

	def check_inet_connection(self):
		self.debug(7,"def check_inet_connection()")
		if self.LAST_CHECK_INET_FALSE > int(time.time())-15:
			return False
		if not self.try_socket(API_DOMAIN,443) == True:
			self.debug(1,"def check_inet_connection: failed!")
			self.LAST_CHECK_INET_FALSE = int(time.time())
			return False
		return True

	def try_socket(self,host,port):
		self.debug(7,"def try_socket()")
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(3)
			result = s.connect_ex((host, port))
			s.close()
		except:
			return False
		if result == 0:
			self.debug(7,"def try_socket: %s:%s True" % (host,port))
			return True

	def check_myip(self):
		self.debug(7,"def check_myip()")
		# *** fixme *** missing ipv6 support
		if self.OVPN_CONFIGVERSION == "23x" or self.OVPN_CONFIGVERSION == "23x46":
			if self.LAST_CHECK_MYIP > int(time.time())-random.randint(120,300) and self.OVPN_PING_LAST > 0:
				return True
			try:
				url = "http://%s/myip4" % (self.GATEWAY_OVPN_IP4A)
				HEADERS = self.make_useragent()
				r = requests.get(url,timeout=3,headers=HEADERS)
				rip = r.content.strip().split()[0]
				if rip == self.OVPN_CONNECTEDtoIP:
					self.debug(1,"def check_myip: rip == self.OVPN_CONNECTEDtoIP")
					self.LAST_CHECK_MYIP = int(time.time())
					return True
			except:
				self.debug(1,"def check_myip: False")
				return False
		else:
			self.debug(1,"def check_myip: invalid self.OVPN_CONFIGVERSION")
			return False

	def load_firewall_backups(self):
		self.debug(1,"def load_firewall_backups()")
		try:
			if os.path.exists(self.pfw_dir):
				content = os.listdir(self.pfw_dir)
				self.FIREWALL_BACKUPS = list()
				for file in content:
					if file.endswith('.bak.wfw'):
						filepath = "%s\\%s" % (self.pfw_dir,file)
						self.FIREWALL_BACKUPS.append(file)
		except:
			self.debug(1,"def load_firewall_backups: failed")

	def load_ovpn_server(self):
		self.debug(1,"def load_ovpn_server()")
		# *fixme* useless?
		#if self.LAST_OVPN_SERVER_RELOAD > time.time()-86400:
		#	return
		if len(self.OVPN_SERVER) > 0:
			return
		try:
			if os.path.exists(self.VPN_CFG):
				self.debug(1,"def load_ovpn_server: self.VPN_CFG = '%s'" % (self.VPN_CFG))
				content = os.listdir(self.VPN_CFG)
				self.OVPN_SERVER = list()
				self.OVPN_SERVER_INFO = {}
				for file in content:
					if file.endswith('.ovpn.to.ovpn'):
						filepath = "%s\\%s" % (self.VPN_CFG,file)
						servername = file[:-5]
						countrycode = servername[:2].lower()
						servershort = servername[:3].upper()
						if os.path.isfile(filepath):
							#print filepath
							serverinfo = list()
							for line in open(filepath):
								if "remote " in line:
									#print line
									try:
										ip = line.split()[1]
										port = int(line.split()[2])
										# *** fixme need isValueIPv6 first! ***
										if self.isValueIPv4(ip) and port > 0 and port <= 65535:
											serverinfo.append(ip)
											serverinfo.append(port)
									except:
										self.errorquit(text=_("Could not read Servers Remote-IP:Port from config: %s") % (self.ovpn_server_config_file))
								elif "proto " in line:
									#print line
									try:
										proto = line.split()[1]
										if proto.lower()  == "tcp" or proto.lower() == "udp":
											proto = proto.upper()
											serverinfo.append(proto)
									except:
										self.errorquit(text=_("Could not read Servers Protocol from config: %s") % (self.ovpn_server_config_file))
								elif line.startswith("cipher "):
									#elif "cipher " in line:
									#print line
									try:
										cipher = line.split()[1]
										if cipher == "CAMELLIA-256-CBC":
											cipher = "CAM-256"
										elif cipher == "AES-256-CBC":
											cipher = "AES-256"
										serverinfo.append(cipher)
									except:
										self.errorquit(text=_("Could not read Servers Cipher from config: %s") % (self.ovpn_server_config_file))
								if "fragment " in line or "link-mtu " in line:
									#print line
									try:
										mtu = line.split()[1]
										serverinfo.append(mtu)
									except:
										mtu = 1500
										serverinfo.append(mtu)
										self.debug(1,"Could not read mtu from config: %s" % (self.ovpn_server_config_file))
							# end: for line in open(filepath)
							self.OVPN_SERVER_INFO[servershort] = serverinfo
						self.OVPN_SERVER.append(servername)
						self.debug(5,"def load_ovpn_server: file = '%s' END" % (file))
				# for end
				self.OVPN_SERVER.sort()
				#*fixme* useless?
				#self.LAST_OVPN_SERVER_RELOAD = time.time()
				return True
			else:
				self.reset_last_update()
		except:
			self.debug(1,"def load_ovpn_server: failed")

	def load_remote_data(self):
		if self.timer_load_remote_data_running == True:
			return False
		self.timer_load_remote_data_running = True
		if self.APIKEY == False:
			self.debug(6,"def load_remote_data: no api data")
			self.timer_load_remote_data_running = False
			return False
		elif self.state_openvpn() == True and self.OVPN_CONNECTEDseconds > 0 and self.OVPN_PING_LAST <= 0:
			self.debug(6,"def load_remote_data: waiting for ovpn connection")
			self.timer_load_remote_data_running = False
			return False
		elif self.state_openvpn() == True and self.OVPN_CONNECTEDseconds > 0 and self.OVPN_PING_LAST > 999:
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
			for key,value in sorted(newdata.iteritems()):
				texta = "%s %s %s" % (texta,key,value)
			for key,value in sorted(olddata.iteritems()):
				textb = "%s %s %s" % (textb,key,value)
			hasha = hashlib.sha256(texta).hexdigest()
			hashb = hashlib.sha256(textb).hexdigest()
			self.debug(9,"hasha newdata = '%s'" % (hasha))
			self.debug(9,"hashb olddata = '%s'" % (hashb))
			if hasha == hashb:
				return True
		except:
			self.debug(1,"def check_hash_dictdata: failed")

	def load_serverdata_from_remote(self):
		updatein = self.LAST_OVPN_SRV_DATA_UPDATE + self.LOAD_DATA_EVERY
		now = int(time.time())
		self.debug(46,"def load_serverdata_from_remote: ?")
		if self.LOAD_SRVDATA == False:
			self.debug(46,"def load_serverdata_from_remote: disabled")
			return False
		elif self.MAINWINDOW_OPEN == False:
			self.debug(46,"def load_serverdata_from_remote: mainwindow not open")
			return False
		elif self.MAINWINDOW_HIDE == True:
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
			HEADERS = self.make_useragent()
			r = requests.post(self.APIURL,data=values,headers=HEADERS,timeout=(3,3))
			self.debug(1,"def load_serverdata_from_remote: posted")
			try:
				if not r.content == "AUTHERROR":
					#self.debug(1,"r.content = '%s'" % (r.content))
					OVPN_SRV_DATA = json.loads(r.content)
					self.debug(9,"OVPN_SRV_DATA = '%s'" % (OVPN_SRV_DATA))
					if len(OVPN_SRV_DATA) > 1:
						if not self.check_hash_dictdata(OVPN_SRV_DATA,self.OVPN_SRV_DATA):
							self.OVPN_SRV_DATA = OVPN_SRV_DATA
							self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
							self.debug(1,"def load_serverdata_from_remote: loaded, len = %s" % (len(self.OVPN_SRV_DATA)))
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
					self.msgwarn(_("Invalid User-ID or API-Key or Account expired!"),"Error!")
					return False
			except:
				self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
				self.debug(1,"def load_serverdata_from_remote: json decode error")
				return False
		except:
			self.LAST_OVPN_SRV_DATA_UPDATE = int(time.time())
			self.debug(1,"def load_serverdata_from_remote: api request failed")
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
			HEADERS = self.make_useragent()
			r = requests.post(self.APIURL,data=values,headers=HEADERS,timeout=(3,3))
			self.debug(1,"def load_accinfo_from_remote: posted")
			try:
				if not r.content == "AUTHERROR":
					#self.debug(1,"r.content = '%s'" % (r.content))
					OVPN_ACC_DATA = json.loads(r.content)
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
					self.msgwarn(_("Invalid User-ID or API-Key or Account expired!"),"Error: def load_accinfo_from_remote")
					return False
			except:
				self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
				self.debug(1,"def load_accinfo_from_remote: json decode error")
				return False
		except:
			self.LAST_OVPN_ACC_DATA_UPDATE = int(time.time())
			self.debug(1,"def load_accinfo_from_remote: api request failed")
			return False

	""" *fixme* move to openvpn.py """
	def upgrade_openvpn(self):
		self.debug(1,"def upgrade_openvpn()")
		if self.load_openvpnbin_from_remote():
			if self.win_install_openvpn():
				self.debug(1,"def upgrade_openvpn: self.win_install_openvpn() = True")
				return True
		if self.verify_openvpnbin_dl():
			self.errorquit(text=_("openVPN Setup downloaded and hash verified OK!\n\nPlease start setup from file:\n'%s'\n\nVerify GPG with:\n'%s'") % (self.OPENVPN_SAVE_BIN_TO,self.OPENVPN_ASC_FILE))
		else:
			self.errorquit(text=_("openVPN Setup downloaded but hash verify failed!\nPlease install openVPN!\nURL1: %s\nURL2: %s") % (openvpn.values(DEBUG)["OPENVPN_DL_URL"],openvpn.values(DEBUG)["OPENVPN_DL_URL_ALT"]))

	""" *fixme* move to openvpn.py """
	def load_openvpnbin_from_remote(self):
		self.debug(1,"def load_openvpnbin_from_remote()")
		self.OPENVPN_SAVE_BIN_TO = "%s\\%s" % (self.VPN_DIR,openvpn.values(DEBUG)["SETUP_FILENAME"])
		self.OPENVPN_ASC_FILE = "%s.asc" % (self.OPENVPN_SAVE_BIN_TO)
		if os.path.isfile(self.OPENVPN_SAVE_BIN_TO):
			return self.verify_openvpnbin_dl()
		else:
			self.tray.set_tooltip_markup(_("%s - Downloading openVPN (1.8 MB)") % (CLIENT_STRING))
			try:
				HEADERS = self.make_useragent()
				r1 = requests.get(openvpn.values(DEBUG)["OPENVPN_DL_URL"],headers=HEADERS)
				if len(r1.content) == openvpn.values(self.DEBUG)["F_SIZES"][self.ARCH]:
					fp1 = open(self.OPENVPN_SAVE_BIN_TO, "wb")
					fp1.write(r1.content)
					fp1.close()
					ascfile = "%s.asc" % (openvpn.values(DEBUG)["OPENVPN_DL_URL"])
					if os.path.isfile(ascfile):
						os.remove(ascfile)
					HEADERS = self.make_useragent()
					r2 = requests.get(ascfile,headers=HEADERS)
					fp2 = open(self.OPENVPN_ASC_FILE, "wb")
					fp2.write(r2.content)
					fp2.close()
					self.tray.set_tooltip_markup(_("%s - Verify openVPN") % (CLIENT_STRING))
				else:
					self.debug(1,"Invalid filesize len(r1.content) = '%s' but !== self.OPENVPN_FILESIZE"%(len(r1.content)))
				return self.verify_openvpnbin_dl()
			except:
				self.debug(1,"def load_openvpnbin_from_remote: failed")
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
				self.msgwarn(_("Invalid File hash: %s !\nlocalhash = '%s'\nbut should be = '%s'") % (self.OPENVPN_SAVE_BIN_TO,localhash,self.OPENVPN_FILEHASH),_("Error!"))
				try:
					os.remove(self.OPENVPN_SAVE_BIN_TO)
				except:
					self.msgwarn(_("Failed remove file: %s") % (self.OPENVPN_SAVE_BIN_TO),_("Error!"))
				self.tray.set_tooltip_markup(_("%s - Verify openVPN failed") % (CLIENT_STRING))
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
		except:
			self.debug(1,"def win_install_openvpn: '%s' failed" % (netshcmd))
			return False

	""" *fixme* move to openvpn.py """
	def win_dialog_select_openvpn(self):
		self.debug(1,"def win_dialog_select_openvpn()")
		#self.msgwarn(_("OpenVPN not found!\n\nPlease select openvpn.exe on next window!\n\nIf you did not install openVPN yet: click cancel on next window!"),_("Setup: openVPN"))
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
		except:
			self.debug(1,"def win_dialog_select_openvpn: response failed")
			return False

	""" *fixme* moved to openvpn.py """
	def win_detect_openvpn(self):
		values = openvpn.win_detect_openvpn(self.DEBUG,self.OPENVPN_EXE)
		if not values == False:
			self.OPENVPN_DIR = values["OPENVPN_DIR"]
			self.OPENVPN_EXE = values["OPENVPN_EXE"]
			self.debug(1,"def win_detect_openvpn: DIR = '%s', EXE = '%s'"%(self.OPENVPN_DIR,self.OPENVPN_EXE))
			
			if openvpn.check_files(self.DEBUG,self.OPENVPN_DIR) == True:
				if openvpn.win_detect_openvpn_version(self.DEBUG,self.OPENVPN_EXE) == True:
					return True
			else:
				if self.upgrade_openvpn() == True:
					return self.win_detect_openvpn()
		else:
			if self.win_dialog_select_openvpn() == True:
				return self.win_detect_openvpn()
			else:
				if self.upgrade_openvpn() == True:
					return self.win_detect_openvpn()
		return False

	def check_dns_is_whitelisted(self):
		self.debug(1,"def check_dns_is_whitelisted()")
		#if self.GATEWAY_DNS1 == "127.0.0.1" or self.GATEWAY_DNS1 == self.GATEWAY_OVPN_IP4 or self.GATEWAY_DNS1 == "8.8.8.8" or self.GATEWAY_DNS1 == "8.8.4.4" or self.GATEWAY_DNS1 == "208.67.222.222" or self.GATEWAY_DNS1 == "208.67.220.220" or self.GATEWAY_DNS1 in self.d0wns_DNS:
		if self.GATEWAY_DNS1 == "127.0.0.1":
			self.debug(1,"def check_dns_is_whitelisted: True")
			return True
		else:
			self.debug(1,"def check_dns_is_whitelisted: False")
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
		except:
			self.debug(1,"def load_d0wns_dns: failed")

	def d0wn_dns_entrys(self):
		dnsdata = False
		if self.DEVMODE == True:
			if not os.path.isfile(self.dns_d0wntxt):
				if not self.load_d0wns_dns_from_remote():
					self.debug(1,"def d0wn_dns_entrys: self.load_d0wns_dns_from_remote() failed")
			if os.path.isfile(self.dns_d0wntxt):
				self.debug(1,"self.d0wn_dns_entrys() DEVMODE")
				fp = open(self.dns_d0wntxt,'rb')
				dnsdata = fp.read().split('\r\n')
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
					return True
				else:
					self.debug(1,"def check_d0wns_dnscryptports: failed value '%s'" % (value))
					return False
			return True
		except:
			return False

	def check_d0wns_names(self,name):
		self.debug(59,"def check_d0wns_names()")
		try:
			data = name.split('.')
			#print "def check_d0wns_names: data = '%s' len(data)='%s'" % (data,len(data))
			if len(data) == 5:
				if data[0].startswith("ns") and data[0].isalnum() and data[1].isalnum() and data[2].isalnum() and data[3].isalnum() and data[4].isalnum():
					self.d0wns_DNS[name] = {"countrycode":data[1]}
					return True
				elif data[0] == "2" and data[1] == "dnscrypt-cert" and data[2].isalnum() and data[3].isalnum() and data[4].isalnum():
					return True
				else:
					self.debug(1,"def check_d0wns_names: name failed value '%s'" % (name))
		except:
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
		except:
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
		except:
			return False

	def load_d0wns_dns_from_remote(self):
		return False
		if self.DEVMODE == True:
			self.debug(1,"def load_d0wns_dns_from_remote()")
			try:
				if not os.path.isfile(self.dns_d0wntxt):
					try:
						url = "https://%s/files/dns/d0wns_dns.static.txt" % (release_version.org_data()["VCP_DOMAIN"])
						HEADERS = self.make_useragent()
						r = requests.get(url,headers=HEADERS)
						fp = open(self.dns_d0wntxt,'wb')
						fp.write(r.content)
						fp.close()
						self.debug(1,"def load_d0wns_dns_from_remote: True")
						return True
					except:
						return False
				else:
					return True
			except:
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
			except:
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
		except:
			self.debug(1,"def show_about_dialog: failed")

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
			except:
				pass
			try:
				self.dialogWindow_form_ask_passphrase.destroy()
			except:
				pass
			try:
				self.destroy_mainwindow()
			except:
				pass
			try:
				self.destroy_accwindow()
			except:
				pass
			try:
				self.destroy_settingswindow()
			except:
				pass
			try:
				dialog = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
				dialog.set_position(Gtk.WindowPosition.CENTER)
				dialog.set_title(_("Quit oVPN.to Client"))
				try:
					dialog.set_icon(self.app_icon)
				except:
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
			except:
				pass
			if self.TAP_BLOCKOUTBOUND == True:
				self.win_firewall_whitelist_ovpn_on_tap(option="delete")
			if self.WIN_FIREWALL_ADDED_RULE_TO_VCP == True:
				self.win_firewall_add_rule_to_vcp(option="delete")
			self.debug(1,"close app")
			self.stop_systray_timer = True
			self.stop_systray_timer2 = True
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
					self.win_netsh_restore_dns_from_backup()
					self.debug(1,"Firewall rules restored and block outbound!")
					return True
				elif self.WIN_BACKUP_FIREWALL == True and self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == False:
					self.win_firewall_restore_on_exit()
					self.win_netsh_restore_dns_from_backup()
					self.debug(1,"Firewall: rules restored!")
					return True
				elif self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == True:
					self.win_firewall_block_on_exit()
					self.win_netsh_restore_dns_from_backup()
					self.debug(1,"Firewall: block outbound!")
					return True
				elif self.WIN_ALWAYS_BLOCK_FW_ON_EXIT == False:
					self.win_firewall_allowout()
					self.win_netsh_restore_dns_from_backup()
					self.debug(1,"Firewall: allow outbound!")
					return True
			else:
				try:
					self.dialog_ask_loadorunload_fw.destroy()
				except:
					pass
				try:
					dialog = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
					self.dialog_ask_loadorunload_fw = dialog
					dialog.set_position(Gtk.WindowPosition.CENTER)
					dialog.set_title(_("Firewall Settings"))
					try:
						dialog.set_icon(self.app_icon)
					except:
						pass
					dialog.set_transient_for(self.window)
					dialog.set_border_width(8)
					if self.WIN_BACKUP_FIREWALL == True:
						text = _("Restore previous firewall settings?\n\nPress 'YES' to restore your previous firewall settings!\nPress 'NO' to set profiles to 'blockinbound,blockoutbound'!")
						dialog.set_markup()
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
						self.win_netsh_restore_dns_from_backup()
						return True
					elif response == Gtk.ResponseType.YES:
						dialog.destroy()
						self.debug(1,"def ask_loadorunload_fw: dialog response = YES '%s'" % (response))
						if self.WIN_BACKUP_FIREWALL == True:
							self.win_firewall_restore_on_exit()
						else:
							self.win_firewall_allowout()
						self.win_netsh_restore_dns_from_backup()
						return True
					else:
						dialog.destroy()
						self.debug(1,"def ask_loadorunload_fw: dialog response = ELSE '%s'" % (response))
						return False
				except:
					self.debug(1,"def ask_loadorunload_fw: dialog failed")
					return False
		except:
			self.debug(1,"def ask_loadorunload_fw: failed")
			return False

	def remove_lock(self):
		self.debug(1,"def remove_lock()")
		try:
			LOCKFILE = self.lock_file
		except:
			return True
		if os.path.isfile(LOCKFILE):
			self.LOCK.close()
			self.debug(1,"def remove_lock: self.LOCK.close()")
			try:
				os.remove(LOCKFILE)
				self.debug(1,"def remove_lock: os.remove(LOCKFILE)")
				return True
			except:
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
			except:
				pass
			message.set_markup("%s"%(text))
			message.run()
			message.destroy()
		except:
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
				except:
					self.debug(1,"def init_localization: locale.getdefaultlocale() failed")
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
			except:
				self.debug(1,"def init_localization: %s not found, fallback to en"% (filename))
			if translation == False or filename == False:
				translation = gettext.NullTranslations()
			try:
				translation.install()
			except:
				self.debug(1,"def init_localization: translation.install() failed")
				return False
			self.APP_LANGUAGE = loc
			self.debug(1,"def init_localization: return self.APP_LANGUAGE = '%s'"% (self.APP_LANGUAGE))
			return True
		except:
			self.debug(1,"def init_localization: failed")

	def msgwarn(self,text,title):
		GLib.idle_add(self.msgwarn_glib,text,title)

	def msgwarn_glib(self,text,title):
		try:
			self.msgwarn_window.destroy()
		except:
			pass
		self.debug(1,"def msgwarn: %s"% (text))
		try:
			self.LAST_MSGWARN_WINDOW = int(time.time())
			self.debug(1,"def msgwarn: %s"% (text))
			dialogWindow = Gtk.MessageDialog(type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK)
			self.msgwarn_window = dialogWindow
			dialogWindow.set_position(Gtk.WindowPosition.CENTER)
			dialogWindow.set_title(title)
			dialogWindow.set_transient_for(self.window)
			dialogWindow.set_border_width(8)
			try:
				dialogWindow.set_icon(self.app_icon)
			except:
				pass
			dialogWindow.set_markup("%s"%(text))
			dialogWindow.run()
			dialogWindow.destroy()
		except:
			self.debug(1,"def msgwarn_glib: failed")

	def statusicon_size_changed(widget, size):
		self.debug(1,"def statusicon_size_changed() size = '%s'" % (size))

	def decode_icon(self,icon):
		#self.debug(49,"def decode_icon()")
		try:
			try:
				imgpixbuf = self.ICON_CACHE_PIXBUF[icon]
				if isinstance(imgpixbuf, GdkPixbuf.Pixbuf):
					self.debug(49,"def decode_icon: isinstance self.ICON_CACHE_PIXBUF[%s]"%(icon))
					return imgpixbuf
			except:
				try:
					self.debug(49,"def decode_icon(%s)" % (icon))
					base64_data = base64.b64decode(self.base64_icons(icon))
					base64_stream = Gio.MemoryInputStream.new_from_data(base64_data)
					imgpixbuf = GdkPixbuf.Pixbuf.new_from_stream(base64_stream)
					self.ICON_CACHE_PIXBUF[icon] = imgpixbuf
					return imgpixbuf
				except:
					return False
		except:
			self.debug(1,"def decode_icon: '%s' failed"%(icon))

	def decode_flag(self,flag):
		#self.debug(48,"def decode_flag()")
		try:
			try:
				imgpixbuf = self.FLAG_CACHE_PIXBUF[flag]
				if isinstance(imgpixbuf, GdkPixbuf.Pixbuf):
					self.debug(48,"def decode_flag: isinstance self.FLAG_CACHE_PIXBUF[%s] return"%(flag))
					return imgpixbuf
			except:
				try:
					self.debug(48,"def decode_flag(%s)" % (flag))
					flagfile = "%s.png" % (flag)
					base64_flag = self.FLAGS_B64[flagfile]
				except:
					base64_flag = self.FLAGS_B64["00.png"]
				base64_data = base64.b64decode(base64_flag)
				base64_stream = Gio.MemoryInputStream.new_from_data(base64_data)
				imgpixbuf = GdkPixbuf.Pixbuf.new_from_stream(base64_stream)
				self.FLAG_CACHE_PIXBUF[flag] = imgpixbuf
				return imgpixbuf
		except:
			self.debug(1,"def decode_flag: '%s' failed"%(flag))

	def base64_icons(self, icon):
		self.debug(1,"def base64_icons(%s)"%(icon))
		return icons_b64.base64_icons(icon)

	def debug(self,level,text):
		try:
			istrue = self.DEBUG
		except:
			istrue = False
		
		try:
			bindir = self.BIN_DIR
		except:
			bindir = False
		CDEBUG(level,text,istrue,bindir)
		return

def app():
	Systray()
	Gtk.main()

if __name__ == "__main__":
	app()
