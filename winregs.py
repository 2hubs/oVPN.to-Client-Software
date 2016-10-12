# -*- coding: utf-8 -*-
import os, sys, time, subprocess, netifaces, locale
from debug import debug
from winreg import *

def get_uninstall_progs():
	aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
	aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
	list = []
	for i in range(1024):
		try:
			keyname = EnumKey(aKey, i)
			asubkey = OpenKey(aKey, keyname)
			val = QueryValueEx(asubkey, "DisplayName")
			print(val)
			list.append(val)
		except WindowsError:
			pass
	return list

""" NETWORK ADAPTER """

def get_networkadapter_guids():
	return netifaces.interfaces()

def get_networkadapterlist_from_netsh(DEBUG):
	debug(1,"[winregs.py] def get_networkadapterlist_from_netsh()",DEBUG,True)
	string = "netsh.exe interface show interface"
	try:
		out = subprocess.check_output(string,shell=True)
		#debug(1,"[winregs.py] def get_networkadapterlist_from_netsh: out = '%s'"%(out),DEBUG,True)
		try:
			data = out.decode('utf-8').split('\r\n')
			#data = out.split('\\r\\n')
			debug(1,"[winregs.py] def get_networkadapterlist_from_netsh: data = '%s'"%(data),DEBUG,True)
			return data
		except Exception as e:
			debug(1,"[winregs.py] def get_networkadapterlist_from_netsh: failed #1, exception = '%s'"%(e),DEBUG,True)
	except Exception as e:
		debug(1,"[winregs.py] def get_networkadapterlist_from_netsh: failed #2, exception = '%s'"%(e),DEBUG,True)
	

def get_networkadapterlist_from_guids(DEBUG,iface_guids):
	iface_names = ['(unknown)' for i in range(len(iface_guids))]
	mapguids = {}
	reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
	key = OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
	for i in range(len(iface_guids)):
		try:
			reg_subkey = OpenKey(key, iface_guids[i] + r'\Connection')
			iface_name = QueryValueEx(reg_subkey, 'Name')[0]
			iface_names[i] = iface_name
			mapguids[iface_name] = '%s' % (iface_guids[i])
		except:
			pass
	debug(2,"[winregs.py] def get_networkadapterlist_from_guid: mapguids = '%s'" % (mapguids),DEBUG,True)
	data = { "iface_names":iface_names,"mapguids":mapguids }
	return data
	#return iface_names

def get_networkadapterlist(DEBUG):
	debug(1,"[winregs.py] def get_networkadapterlist()",DEBUG,True)
	try:
		newlist = []
		debug(1,"[winregs.py] def get_networkadapterlist: debug 01",DEBUG,True)
		list1 = get_networkadapterlist_from_guids(DEBUG,get_networkadapter_guids())["iface_names"]
		debug(1,"[winregs.py] def get_networkadapterlist: list1 = '%s'"%(list1),DEBUG,True)
		list2 = get_networkadapterlist_from_netsh(DEBUG)
		debug(1,"[winregs.py] def get_networkadapterlist: list2 = '%s'"%(list2),DEBUG,True)
		for name in list1:
			print(name)
			for line in list2:
				#print(line)
				#eline = line.encode('utf-8')
				#ename = name.encode('utf-8')
				#if eline.endswith(ename):
				#eline = line.encode('utf-8')
				#ename = bytes(name,'utf-8')
				#if line.endswith(name):
				if name in line:
					debug(1,"[winregs.py] def get_networkadapterlist: HIT name = '%s'"%(name),DEBUG,True)
					newlist.append(name)
					break
		return newlist
	except Exception as e:
		debug(1,"[winregs.py] def get_networkadapterlist: failed, exception = '%s'"%(e),DEBUG,True)
		return False

def get_networkadapter_guid(DEBUG,adaptername):
	guids = get_networkadapterlist_from_guids(DEBUG,get_networkadapter_guids())["mapguids"]
	guid = guids[adaptername]
	debug(1,"[winregs.py] def get_networkadapter_guid: adaptername = '%s' guid = '%s'" % (adaptername,guid),DEBUG,True)
	return guid
	#return get_networkadapterlist_from_guids(get_networkadapter_guids())["mapguids"][adaptername]

def get_tapadapters(DEBUG,OPENVPN_EXE,INTERFACES):
	try:
		print("get_tapadapters debug 00")
		if os.path.isfile(OPENVPN_EXE):
			cmdstring = '"%s" --show-adapters' % (OPENVPN_EXE)
			print("get_tapadapters debug 01a, cmdstring = '%s'"%(cmdstring))
			TAPADAPTERS = subprocess.check_output(cmdstring,shell=True)
			print("get_tapadapters debug 01b, TAPADAPTERS = '%s'"%(TAPADAPTERS))
			TAPADAPTERS = TAPADAPTERS.decode('utf-8').split('\r\n')
			print("get_tapadapters debug 01c, TAPADAPTERS = '%s'"%(TAPADAPTERS))
			TAPADAPTERS.pop(0)
			TAP_DEVS = list()
			print("get_tapadapters debug 01")
			for line in TAPADAPTERS:
				if len(line) > 0:
					print("get_tapadapters debug 02, line = '%s'"%(line))
					#eline = line.encode('utf-8')
					#print("get_tapadapters debug 02, eline = '%s'"%(eline))
					for INTERFACE in INTERFACES:
						print("get_tapadapters debug 03, INTERFACE = '%s'"%(INTERFACE))
						if INTERFACE in line:
							print("get_tapadapters debug 03 HIT")
							INTERFACES.remove(INTERFACE)
							TAP_DEVS.append(INTERFACE)
							break
				"""
				for INTERFACE in INTERFACES:
					print("get_tapadapters debug 03, INTERFACE = '%s'"%(INTERFACE))
					
					
					search = string.encode('utf-8')
					eline = line.encode('utf-8')
					print("get_tapadapters debug 03, eline = '%s'"%(eline))

					#
					#if line.startswith("'%s' {"%(INTERFACE)):
					if eline.startswith(search):
						INTERFACES.remove(INTERFACE)
						TAP_DEVS.append(INTERFACE)
						break
				"""
			return { "INTERFACES":INTERFACES,"TAP_DEVS":TAP_DEVS }
	except Exception as e:
		debug(1,"[winregs.py] def get_tapadapters: failed, exception = '%s'"%(e),DEBUG,True)
		return False

def get_interface_infos_from_guid(DEBUG,guid):
	debug(1,"[winregs.py] def get_interface_infos_from_guid: '%s'" % (guid),DEBUG,True)
	"""
	winregs.get_interface_infos_from_guid("{XXXXXXXX-YYYY-ZZZZ-AAAA-CCCCDDDDEEEE}")
	return = {
			'AddressType': 0, 'DefaultGateway': [u'192.168.1.1'], 'SubnetMask': [u'255.255.255.0'],
			'NameServer': u'8.8.8.8,8.8.4.4', 'IPAddress': [u'192.168.1.123'], 
			'DhcpServer': u'255.255.255.255', 'DhcpIPAddress': u'0.0.0.0'}, 'DhcpSubnetMask': u'255.0.0.0'
	"""
	values = { "AddressType":False, "DefaultGateway":False, "IPAddress":False, "SubnetMask":False, "NameServer":False, "DhcpIPAddress":False, "DhcpServer":False, "DhcpSubnetMask":False }
	reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
	key = OpenKey(reg, r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\%s' % (guid))
	for keyname,value in values.items():
		try:
			values[keyname] = QueryValueEx(key, keyname)[0]
		except:
			pass
	debug(1,"[winregs.py] get_interface_infos_from_guid: '%s'" % (values),DEBUG,True)
	return values