# -*- coding: utf-8 -*-
import os, subprocess, datetime
import release_version
from debug import debug

def set_task(DEBUG,AUTOSTART_DELAY_TIME):
    BIN_DIR = os.getcwd()
    DATE = datetime.datetime.now()
    USERNAME = os.getenv('username')

    lines = list()
    lines.append('<?xml version="1.0" encoding="UTF-16"?>')
    lines.append('<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">')
    lines.append('  <RegistrationInfo>')
    lines.append('    <Date>%s</Date>' % DATE.isoformat())
    lines.append('    <Author>%s %s</Author>' % (release_version.org_data()["ORG"],release_version.org_data()["ADD"]))
    lines.append('    <URI>\%s</URI>' % (release_version.version_data()["NAME"]))
    lines.append('  </RegistrationInfo>')
    lines.append('  <Triggers>')
    lines.append('    <LogonTrigger>')
    lines.append('      <Enabled>true</Enabled>')
    lines.append('      <UserId>%s</UserId>' % USERNAME)
    lines.append('      <Delay>PT%sS</Delay>' % AUTOSTART_DELAY_TIME)
    lines.append('    </LogonTrigger>')
    lines.append('  </Triggers>')
    lines.append('  <Principals>')
    lines.append('    <Principal id="Author">')
    lines.append('      <UserId>%s</UserId>' % USERNAME)
    lines.append('      <LogonType>InteractiveToken</LogonType>')
    lines.append('      <RunLevel>HighestAvailable</RunLevel>')
    lines.append('    </Principal>')
    lines.append('  </Principals>')
    lines.append('  <Settings>')
    lines.append('    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>')
    lines.append('    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>')
    lines.append('    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>')
    lines.append('    <AllowHardTerminate>false</AllowHardTerminate>')
    lines.append('    <StartWhenAvailable>false</StartWhenAvailable>')
    lines.append('    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>')
    lines.append('    <IdleSettings>')
    lines.append('      <StopOnIdleEnd>true</StopOnIdleEnd>')
    lines.append('      <RestartOnIdle>false</RestartOnIdle>')
    lines.append('    </IdleSettings>')
    lines.append('    <AllowStartOnDemand>true</AllowStartOnDemand>')
    lines.append('    <Enabled>true</Enabled>')
    lines.append('    <Hidden>false</Hidden>')
    lines.append('    <RunOnlyIfIdle>false</RunOnlyIfIdle>')
    lines.append('    <WakeToRun>false</WakeToRun>')
    lines.append('    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>')
    lines.append('    <Priority>7</Priority>')
    lines.append('    <RestartOnFailure>')
    lines.append('      <Interval>PT1M</Interval>')
    lines.append('      <Count>3</Count>')
    lines.append('    </RestartOnFailure>')
    lines.append('  </Settings>')
    lines.append('  <Actions Context="Author">')
    lines.append('    <Exec>')
    lines.append('      <Command>"%s\%s"</Command>' % (BIN_DIR,release_version.setup_data()["exename"]))
    lines.append('      <WorkingDirectory>%s</WorkingDirectory>' % (BIN_DIR))
    lines.append('    </Exec>')
    lines.append('  </Actions>')
    lines.append('</Task>')

    XMLFILE = "%s\\autostart.xml" % (BIN_DIR)
    remove_xml(DEBUG,XMLFILE)
    ind = open(XMLFILE, "wt")
    for line in lines:
        ind.write("%s\n"%(line))
    ind.close()
    if not os.path.exists(XMLFILE):
        return False

    if os.path.exists(XMLFILE):
        string = 'schtasks.exe /Create /XML "%s" /TN "%s"' % (XMLFILE,release_version.version_data()["NAME"])
        try:
            exitcode = subprocess.check_call("%s" % (string),shell=True)
            remove_xml(DEBUG,XMLFILE)
            if exitcode == 0:
                debug(1,"[schedule_task.py] def cb_switch_autostart: enable Ok",DEBUG,True)
                return True
            else:
                debug(1,"[schedule_task.py] def cb_switch_autostart: enable fail, exitcode = '%s'" % (exitcode),DEBUG,True)
                return False
        except:
            remove_xml(DEBUG,XMLFILE)
            debug(1,"[schedule_task.py] def cb_switch_autostart: enable failed",DEBUG,True)

def remove_xml(DEBUG,XMLFILE):
    if os.path.isfile(XMLFILE):
        try:
            os.remove(XMLFILE)
        except:
            debug(1,"[schedule_task.py] def remove_xml: could not remove XMLFILE '%s'" % (XMLFILE),DEBUG,True)
            pass

def delete_task(DEBUG):
    string = 'schtasks.exe /Delete /TN "%s" /f' % (release_version.version_data()["NAME"])
    try:
        exitcode = subprocess.check_call("%s" % (string),shell=True)
        if exitcode == 0:
            debug(1,"[schedule_task.py] def cb_switch_autostart: disable Ok",DEBUG,True)
            return True
        else:
            debug(1,"[schedule_task.py] def cb_switch_autostart: disable fail, exitcode = '%s'" % (exitcode),DEBUG,True)
            return False
    except:
        debug(1,"[schedule_task.py] def cb_switch_autostart: disable failed",DEBUG,True)
        return False
