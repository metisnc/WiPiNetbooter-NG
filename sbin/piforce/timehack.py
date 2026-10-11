import os, collections, signal, sys, subprocess, socket
from time import sleep
sys.path.append('/sbin/piforce/dm_netboot/netdimm/')
from netdimm import NetDimm

def exists(path):
    try:
        os.stat(path)
    except OSError:
        return False
    return True

activedimm = sys.argv[1]
pidpath = '/var/log/'+activedimm

if exists(pidpath):
    lastpidfile = open(pidpath, "r")
    lastpid = lastpidfile.readline()
    lastpidfile.close()
else:
    lastpidfile = open(pidpath, "w")
    lastpidfile.close()

try:
    os.kill(int(lastpid), signal.SIGKILL)
except:
    pass

currentpid = os.getpid()

bashCommand1 = 'sudo echo -n '+str(currentpid)+' | tee /var/log/'+activedimm
os.system(bashCommand1)
print()

netdimm = NetDimm(activedimm, log=print)
print("time hack enabled")
while True:
    netdimm.set_time_hack(10)
    print("reset message sent")
    sleep(300)
exit()