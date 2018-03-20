#!/usr/bin/python3 -u

from ns_snmp import NS_SNMP,Debug
from configparser import ConfigParser

Config = ConfigParser()
Config.read('/opt/nt-nanoswitch/config.ini')

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                Debug("skip: " + option)
        except:
            Debug.logException()
            dict1[option] = None
    return dict1

sensorsFile = ConfigSectionMap('Statistics')['sensors_file']
Debug('sFile' + sensorsFile)
ifacesNum = ConfigSectionMap('Interfaces')['number']
Debug('Number of interfaces for monitoring: ' + ifacesNum)
ifacesNum = int(ifacesNum)

snmp = NS_SNMP(".1.3.6.1.4.1.42779.3", ifacesNum, sensorsFile)
snmp.addOid(".1", NS_SNMP.STRING, "NanoSwitch 2");
Debug('three')

for i in range(1, ifacesNum + 1):
    snmp.addOid(".2." + str(i), NS_SNMP.INTEGER, 0);
for i in range(1, ifacesNum + 1):
    snmp.addOid(".3." + str(i), NS_SNMP.COUNTER, 0);
for i in range(1, ifacesNum + 1):
    snmp.addOid(".4." + str(i), NS_SNMP.COUNTER, 0);
for i in range(1, ifacesNum + 1):
    snmp.addOid(".5." + str(i), NS_SNMP.COUNTER, 0);
for i in range(1, ifacesNum + 1):
    snmp.addOid(".6." + str(i), NS_SNMP.COUNTER, 0);
for i in range(1, ifacesNum + 1):
    snmp.addOid(".7." + str(i), NS_SNMP.INTEGER, 0);
for i in range(1, ifacesNum + 1):
    snmp.addOid(".8." + str(i), NS_SNMP.INTEGER, 0);
for i in range(1, ifacesNum + 1):
    snmp.addOid(".9." + str(i), NS_SNMP.STRING, '0'); #sfp_rx_mode
for i in range(1, ifacesNum + 1):
    snmp.addOid(".10." + str(i), NS_SNMP.STRING, '0'); #sfp_temperature
for i in range(1, ifacesNum + 1):
    snmp.addOid(".11." + str(i), NS_SNMP.STRING, '0'); #sfp_power_tx
for i in range(1, ifacesNum + 1):
    snmp.addOid(".12." + str(i), NS_SNMP.STRING, '0'); #sfp_power_rx

snmp.addOid(".13", NS_SNMP.STRING, "0"); #ns_ver
snmp.addOid(".14", NS_SNMP.STRING, "0"); #firmware_ver
snmp.addOid(".15", NS_SNMP.STRING, "0"); #crystal temperature

snmp.respond()
