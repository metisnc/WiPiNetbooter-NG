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

logging.basicConfig(filename="/var/log/singleboot.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
sys.stderr.write = logger.error
sys.stdout.write = logger.info

print("Single boot script started")
complete = False
todocount = 0

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

with open('/var/www/html/csv/dimms.csv', newline='') as csvfile:
    dimmreader = csv.DictReader(csvfile)
    rowslist = list(dimmreader)

for row in rowslist:
    row.update({'online':'no'})

while (complete == False):
    todocount = 0
    for row in rowslist:
        if (row['online'] == 'no' and row['defaultgame'] != 'none'):
            todocount = todocount + 1
        print(row['ipaddress'])
        if (row['online'] == 'no'):
            if (port_check(row['ipaddress'])):
                row.update({'online':'yes'})
                print(row)
                if (row['defaultgame'] == 'menu'):
                    print("Default game is menu - launching menulauncher script on", row['ipaddress'])
                    cp = subprocess.Popen(['python3', '/sbin/piforce/menulauncher.py', row['ipaddress'], mode], preexec_fn=os.setsid)
                elif (row['defaultgame'] != 'none'):
                    print("Default game is not menu - launching", row['defaultgame'])
                    cp = subprocess.Popen(['python3', '/sbin/piforce/wipiloader.py', row['defaultgame'], row['ipaddress'], relaymode, zeromode, row['openjvs'], row['openffb']], preexec_fn=os.setsid)
    if (todocount == 0):
        break