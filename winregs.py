# -*- coding: utf-8 -*-
import os, sys, time, subprocess, netifaces, locale
from winreg import *
# .py file imports
from debug import debug
import encodes


decoding = 'utf_8'
# debug(1,"[winregs.py] def abcd1234: failed, exception = '%s'"%(e),DEBUG,True)



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

def get_networkadapter_guids(DEBUG):
    return netifaces.interfaces()

def get_networkadapterlist_from_netsh(DEBUG):
    encodes.logencoding(DEBUG)
    debug(1,"[winregs.py] def get_networkadapterlist_from_netsh()",DEBUG,True)
    cmdstring = "netsh.exe interface show interface"
    try:
        output = subprocess.check_output(cmdstring,shell=True)
        debug(1,"[winregs.py] def get_networkadapterlist_from_netsh: output = '%s'"%(output),DEBUG,True)
        output0 = encodes.code_fiesta(DEBUG,'decode',output,'get_networkadapterlist_from_netsh').strip().splitlines()
        debug(1,"[winregs.py] def get_networkadapterlist_from_netsh: output0 = '%s'"%(output0),DEBUG,True)
        return output0
    except Exception as e:
        debug(1,"[winregs.py] def get_networkadapterlist_from_netsh: failed, exception = '%s'"%(e),DEBUG,True)

def get_networkadapterlist_from_guids(DEBUG,iface_guids,silent):
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
    if silent == False:
        debug(1,"[winregs.py] def get_networkadapterlist_from_guid: mapguids = '%s'" % (mapguids),DEBUG,True)
    data = { "iface_names":iface_names,"mapguids":mapguids }
    return data

def get_networkadapterlist(DEBUG,silent):
    debug(1,"[winregs.py] def get_networkadapterlist()",DEBUG,True)
    try:
        newlist = []
        list1 = get_networkadapterlist_from_guids(DEBUG,get_networkadapter_guids(DEBUG),silent)["iface_names"]
        debug(2,"[winregs.py] def get_networkadapterlist: list1 = '%s'"%(list1),DEBUG,True)
        list2 = get_networkadapterlist_from_netsh(DEBUG)
        debug(2,"[winregs.py] def get_networkadapterlist: list2 = '%s'"%(list2),DEBUG,True)
        for name in list1:
            if name == "(unknown)" or name.startswith("isatap."):
                continue
            debug(1,"[winregs.py] def get_networkadapterlist: for name '%s' in list1"%(name),DEBUG,True)
            for line in list2:
                debug(1,"[winregs.py] def get_networkadapterlist: for line '%s' in list2"%(line),DEBUG,True)
                # dont remove 3 spaces! user can't set spaces infront of names but output has some!
                if line.endswith("   %s"%(name)):
                    debug(1,"[winregs.py] def get_networkadapterlist: HIT name = '%s'"%(name),DEBUG,True)
                    newlist.append(name)
                    break
        return newlist
    except Exception as e:
        debug(1,"[winregs.py] def get_networkadapterlist: failed, exception = '%s'"%(e),DEBUG,True)
        return False

def get_networkadapter_guid(DEBUG,adaptername,silent):
    guids = get_networkadapterlist_from_guids(DEBUG,get_networkadapter_guids(DEBUG),silent)["mapguids"]
    guid = guids[adaptername]
    if silent == False:
        debug(1,"[winregs.py] def get_networkadapter_guid: adaptername = '%s' guid = '%s'" % (adaptername,guid),DEBUG,True)
    return guid

def get_tapadapters(DEBUG,OPENVPN_EXE,INTERFACES):
    try:
        if os.path.isfile(OPENVPN_EXE):
            cmdstring = '"%s" --show-adapters' % (OPENVPN_EXE)
            output = subprocess.check_output(cmdstring,shell=True)
            output0 = encodes.code_fiesta(DEBUG,'decode',output,'get_tapadapters').strip().splitlines()
            debug(1,"[winregs.py] def get_tapadapters: output0 = '%s'"%(output0),DEBUG,True)
            if "[name, GUID]" in output0[0]:
                output0.pop(0)
                debug(1,"[winregs.py] def get_tapadapters: output0.pop(0)"%(output0),DEBUG,True)
            TAPADAPTERS = output0
            TAP_DEVS = list()
            for INTERFACE in INTERFACES:
                GUID = get_networkadapter_guid(DEBUG,INTERFACE,False)
                for line in TAPADAPTERS:
                    debug(1,"[winregs.py] def get_tapadapters: line = '%s'"%(line),DEBUG,True)
                    if len(line) > 0:
                        if GUID in line:
                            debug(1,"[winregs.py] def get_tapadapters: INTERFACE '%s' HIT"%(INTERFACE),DEBUG,True)
                            INTERFACES.remove(INTERFACE)
                            TAP_DEVS.append(INTERFACE)
                            break
            return { "INTERFACES":INTERFACES,"TAP_DEVS":TAP_DEVS }
    except Exception as e:
        debug(1,"[winregs.py] def get_tapadapters: failed, exception = '%s'"%(e),DEBUG,True)
        return False

def get_interface_infos_from_guid(DEBUG,guid,silent):
    if silent == False:
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
    if silent == False:
        debug(1,"[winregs.py] get_interface_infos_from_guid: '%s'" % (values),DEBUG,True)
    return values