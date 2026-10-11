import os, collections, signal, sys, subprocess, socket, csv, logging
from time import sleep

def ping(host):
    command = ['fping', '-c', '1', host]
    return subprocess.call(command) == 0

def port_check(host):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((host, int(10703)))
      s.shutdown(2)
      return True
   except:
      return False

logging.basicConfig(filename="/var/log/nfcloader.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
sys.stderr.write = logger.error
sys.stdout.write = logger.info

print("NFC loader script started")
complete = False
todocount = 0

nfcgame = sys.argv[1]
print('Game requested is',nfcgame)
if (nfcgame == 'menu'):
    type = 'Sega Naomi2'
else:
    systemcode = nfcgame.split('-')
    if (systemcode[0] == 'n1' or systemcode[0] == 'aw'):
        type = 'Sega Naomi'
    if (systemcode[0] == 'n2'):
        type = 'Sega Naomi2'
    if (systemcode[0] == 'tf'):
        type = 'Sega Triforce'
    if (systemcode[0] == 'ch'):
        type = 'Sega Chihiro'

relayfile = open('/sbin/piforce/relaymode.txt')
relaymode = relayfile.readline()
relayfile.close
zerofile = open('/sbin/piforce/zeromode.txt')
zeromode = zerofile.readline()
zerofile.close
openjvsfile = open('/sbin/piforce/openmode.txt')
openjvsmode = openjvsfile.readline()
openjvsfile.close

if (openjvsmode == 'openon'):
    mode = 'openjvs'
else:
    mode = 'default'

with open('/var/www/html/csv/romsinfo.csv', newline='') as romcsvfile:
    romreader = csv.DictReader(romcsvfile)
    romrowslist = list(romreader)

for row in romrowslist:
    if (nfcgame == row['romname']):
        openjvsmapping = row['openjvs']
        openffbmapping = row['openffb']

with open('/var/www/html/csv/dimms.csv', newline='') as dimmcsvfile:
    dimmreader = csv.DictReader(dimmcsvfile)
    dimmrowslist = list(dimmreader)

netdimmcount = 0

for row in dimmrowslist:
    if (type in row['type']):
        print(row['ipaddress'])
        if (port_check(row['ipaddress'])):
            activedimm = row['ipaddress']
            netdimmcount += 1

if netdimmcount == 1:
    if (nfcgame == 'menu'):
        print("NFC game is menu - launching menulauncher script on", activedimm)
        cp = subprocess.Popen(['python3', '/sbin/piforce/menulauncher.py', activedimm, mode], preexec_fn=os.setsid)
    else:
        print("NFC game is not menu - launching", nfcgame)
        cp = subprocess.Popen(['python3', '/sbin/piforce/wipiloader.py', nfcgame, activedimm, relaymode, zeromode, openjvsmapping, openffbmapping], preexec_fn=os.setsid)

elif netdimmcount == 0:
    print('No dimms available')
elif netdimmcount > 1:
    print('Multiple dimms available')