import re
import sys
import time
import collections

def switch(x):
    return {
        'link': '.2.',
        'rx_packets': '.3.',
        'rx_bytes': '.4.',
        'tx_packets': '.5.',
        'tx_bytes': '.6.',
        'rx_crc_fail': '.7.',
        'tx_crc_fail': '.8.',
        'sfp_rx_mode': '.9.',
        'sfp_temperature': '.10.',
        'sfp_power_tx': '.11.',
        'sfp_power_rx': '.12.'
    }.get(x, 'unknown')

class Debug:
    def __init__(self, data):
        if type(data) is list:
            with open("/tmp/d.log", "w") as f:
                for i in data:
                    f.write(time.strftime("%H:%M:%S") +
                            " DEBUG: " + str(i) + "\n")
        else:
            with open("/opt/nt-nanoswitch/d.log", "w") as f:
                f.write(time.strftime("%H:%M:%S") +
                        " DEBUG: " + str(data) + "\n")

    @staticmethod
    def logException():
        exc_type, exc_value, exc_traceback = sys.exc_info()
        Debug("Exception type: " + str(exc_type))
        Debug("Exception val: " + str(exc_value))
        Debug("Exception trace: " + str(exc_traceback))

class Utils:
    @staticmethod
    def isfloat(value):
      try:
        float(value)
        return True
      except ValueError:
        return False


class NS_SNMP:
    INTEGER = "integer"
    STRING = "string"
    IPADDR = "ipaddress"
    NETADDR = "NetworkAddress"
    GAUGE = "gauge"
    COUNTER = "counter64"
    TIME = "timeticks"
    OBJ = "objectid"
    OPAQUE = "opaque"


    def __init__(self, oid, _ifacesNum, _sensorsFile):
        self.rootOid = oid
        self.sensorsLastReadTime = 0
        self.tree = {}
        self.treeKeys = []
        self.ifacesNum = _ifacesNum
        self.sensorsFile = _sensorsFile


    def addOid(self, oid, type, value):
        self.tree.update({oid: { 'type' : type, 'value' : value }})
        self.treeKeys.append(oid)
        self.lastOid = self.rootOid + oid


    def getVals(self, line, cntrName):
        res = []
        str = line[len(cntrName + ": "): -2]
        for i in str.split(';'):
            if i.isdigit():
                res.append(int(i))
            elif Utils.isfloat(i):
                res.append(float(i))
            else:
                res.append(i)
        return res


    def getCounters(self, line, cntrName):
        oid = switch(cntrName)
        vals = self.getVals(line, cntrName)
        try:
            for i in range(0, self.ifacesNum):
                if oid == '.3.' or oid == '.5.':
                    self.tree[ oid + str(i+1)]['value'] = vals[i]/1000
                elif oid == '.4.' or oid == '.6.':
                    self.tree[ oid + str(i+1)]['value'] = vals[i]/1000000
                else:
                    self.tree[ oid + str(i+1)]['value'] = vals[i]
        except Exception as e:
            Debug.logException()
            print("NONE")
            return
        else:
            return


    def readSensors(self):
        Debug('read counters')
        with open("/opt/NS2/NS_STAT/ns_counters.log") as f:
            for line in f:
                if 'link' in line:
                    self.getCounters(line, 'link')
                elif 'rx_packets' in line:
                    self.getCounters(line, 'rx_packets');
                elif 'rx_bytes' in line:
                    self.getCounters(line, 'rx_bytes');
                elif 'tx_packets' in line:
                    self.getCounters(line, 'tx_packets');
                elif 'tx_bytes' in line:
                    self.getCounters(line, 'tx_bytes');
                elif 'rx_crc_fail' in line:
                    self.getCounters(line, 'rx_crc_fail');
                elif 'tx_crc_fail' in line:
                    self.getCounters(line, 'tx_crc_fail');
                else:
                    Debug("unknown counter: " + line);

        Debug('read sensors')
        with open(self.sensorsFile) as f:
            for line in f:
                if 'sfp_rx_mode' in line:
                    self.getCounters(line, 'sfp_rx_mode');
                elif 'sfp_temperature' in line:
                    self.getCounters(line, 'sfp_temperature');
                elif 'sfp_power_tx' in line:
                    self.getCounters(line, 'sfp_power_tx');
                elif 'sfp_power_rx' in line:
                    self.getCounters(line, 'sfp_power_rx');
                elif 'ns_version' in line:
                    # Debug('ns_version')
                    self.tree['.13']['value'] = line[len('ns_version: '): -2]
                elif 'firmware_version' in line:
                    # Debug('fm_version')
                    self.tree['.14']['value'] = line[len('firmware_version: '): -2]
                elif 'temperature' in line:
                    # Debug('temperature')
                    self.tree['.15']['value'] = line[len('temperature: '): -2]
                else:
                    Debug("unknown counter: " + line);

        Debug('END')

    
    def getOid(self, requestedOid):
        requestedOid = requestedOid.strip()

        try:
            print(requestedOid)
            print(self.tree[ requestedOid[len(self.rootOid):] ]['type'])
            print(self.tree[ requestedOid[len(self.rootOid):] ]['value'])

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Debug("Exception type: " + str(exc_type))
            Debug("Exception val: " + str(exc_value))
            Debug("Exception trace: " + str(exc_traceback))
            print("NONE")
            return

        else:
            return

    def getNextOid(self, requestedOid):
        branchRoots = ['.2','.3','.4','.5','.6', '.7', '.8']
        if requestedOid == self.rootOid:
            first = self.treeKeys[0]
            print(self.rootOid + first)
            print(self.tree[first]['type'])
            print(self.tree[first]['value'])
            return

        try:
            currOid = requestedOid[len(self.rootOid):]
        except Exception:
            Debug.logException()
            print('NONE')
            return
        else:

            if requestedOid == self.lastOid:
                # print(requestedOid)
                print('NONE')
                return

            elif currOid in branchRoots:
                currOid += '.1'
                print(self.rootOid + currOid)
                print(self.tree[currOid]['type'])
                print(self.tree[currOid]['value'])
                return

            elif currOid in self.treeKeys:
                # Debug(self.treeKeys)
                # last = self.tree.keys()[len(self.tree) - 1]
                idx = self.treeKeys.index(currOid) + 1
                try:
                    nextItem = self.tree[self.treeKeys[idx]]
                except Exception:
                    Debug.logException()
                    return
                else:
                    print(self.rootOid + self.treeKeys[idx])
                    print(nextItem['type'])
                    print(nextItem['value'])
                    return
            else:
                print('NONE')
                return


    def respond(self):
        self.readSensors()
        if len(sys.argv) > 1: # pass
            if sys.argv[1] == "-n":
                self.getNextOid(sys.argv[2])
            elif sys.argv[1] == "-g":
                self.getOid(sys.argv[2])
        else: # pass_persist
            while True:
                buff = sys.stdin.readline().strip()
                if buff == '':
                    exit(0)

                if time.time() - self.sensorsLastReadTime > 5:
                    self.readSensors()
                    self.sensorsLastReadTime = time.time()

                if "PING" in buff:
                    Debug("PONG")
                    print("PONG")

                elif "getnext" in buff:
                    oid = sys.stdin.readline().strip()
                    self.getNextOid(oid)

                elif "get" in buff:
                    oid = sys.stdin.readline().strip()
                    self.getOid(oid)
