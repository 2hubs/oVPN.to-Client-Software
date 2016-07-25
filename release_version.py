print "join release_version.py"


def version_data():
	data = {
			"VERSION" : "0.5.8",
			"NAME":"%s Client" % (org_data()["ORG"]),
		}
	return data

def build_data():
	from datetime import date
	import time
	data = {
		"YEAR" : date.today().year,
		# *fixme* oops! way too much dynamic: built date changes realtime in app!
		#"MONTH" : date.today().month,
		#"DAY" : date.today().day,
		#"STAMP" : int(time.time())
	}
	return data

def org_data():
	data = {
			"ORG" : "oVPN.to",
			"ADD" : "Anonymous Services",
			"SITE" : "https://oVPN.to",
			"EMAIL" : "support@ovpn.to",
			"SUPPORT" : "https://vcp.ovpn.to/?site=support",
			"CHAT_URL" : "https://webirc.ovpn.to",
			"IRC_ADDR" : "irc://irc.ovpn.to:6697 (SSL)",
			"UPDATES" : "https://board.ovpn.to/v4/index.php?thread/57314-ovpn-client-for-windows-beta-binary-releases/&action=firstNew",
			"VCP_DOMAIN" : "vcp.ovpn.to",
			"API_POST" : "xxxapi.php",
			"API_DOMAIN" : "vcp.ovpn.to",
			"API_PORT" : "443",
		}
	return data

def setup_data():
	data = { 
			"script" : "ovpn_client.py",
			"version" : "0.%s" % (version_data()["VERSION"]),
			"name" : "%s for Windows" % (version_data()["NAME"]),
			# *fixme* oops, we are too much dynamic, realtime :D
			#"description" : "%s %s Built: %d-%02d-%02d (%d)" % (version_data()["NAME"],version_data()["VERSION"],build_data()["YEAR"],build_data()["MONTH"],build_data()["DAY"],build_data()["STAMP"]),
			"description" : "%s %s" % (version_data()["NAME"],version_data()["VERSION"]),
			"copyright" : "(C) 2010 - %s %s" % (build_data()["YEAR"],org_data()["ORG"]),
		}
	return data

print "version_data() = '%s'" % (version_data())
print "build_data() = '%s'" % (build_data())
print "org_data() = '%s'" % (org_data())
print "setup_data() = '%s'" % (setup_data())


import sys, os
if len(sys.argv) > 1:
	if sys.argv[1] == "SET_VERSION_FILES":
		
		def write_releasefile(key,file,content):
			if os.path.isfile(file):
				fp = open(file, "wb")
				fp.write(content)
				fp.close()
				print "%s written content '%s' to file '%s'" % (key,file,content)
		
		setrelease = {
			"inno" : { "file" : "inno.release", "content" : '#define Version "%s"' % (version_data()["VERSION"]) },
			"winb" : { "file" : "set_version.bat", "content" : 'set RELEASE=%s' % (version_data()["VERSION"]) },
			}
			
		for key, value in setrelease.items():
			write_releasefile(key,value["file"],value["content"])

print "leave release_version.py"