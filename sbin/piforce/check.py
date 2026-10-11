import os, collections, signal, sys, subprocess, socket, csv, logging
from time import sleep

def ping(host):
    command = ['fping', '-c', '1', host]
    return subprocess.call(command) == 0

logging.basicConfig(filename="/var/log/check.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
sys.stderr.write = logger.error
sys.stdout.write = logger.info

bootfile = open('/sbin/piforce/bootfile.txt')
bootmode = bootfile.readline()
bootfile.close
print("Boot mode is set to", bootmode)
powerfile = open('/sbin/piforce/powerfile.txt')
powermode = powerfile.readline()
powerfile.close
print("Power mode is set to", powermode)
nfcfile = open('/sbin/piforce/nfcmode.txt')
nfcmode = nfcfile.readline()
nfcfile.close
print("NFC mode is set to", nfcmode)
openfile = open('/sbin/piforce/openmode.txt')
openmode = openfile.readline()
openfile.close
print("OpenJVS mode is set to", openmode)
rotaryfile = open('/sbin/piforce/rotarymode.txt')
rotarymode = rotaryfile.readline()
rotaryfile.close
print("Rotary mode is set to", rotarymode)
srvfile = open('/sbin/piforce/servermode.txt')
srvmode = srvfile.readline()
srvfile.close
print("Server mode is set to", srvmode)

if (nfcmode == 'nfcon'):
    print("Starting NFC script")
    cp = subprocess.Popen(['python3', '/sbin/piforce/card_emulator/nfcread.py'], preexec_fn=os.setsid)

if (openmode == 'openon'):
    print("Starting OpenJVS with generic mapping")
    cp = subprocess.Popen(['openjvs', 'generic'], preexec_fn=os.setsid)

if (rotarymode == 'rotaryon'):
    print("Starting rotary script")
    cp = subprocess.Popen(['python3', '/sbin/piforce/rotary.py'], preexec_fn=os.setsid)

if os.path.exists('/boot/wifi.txt') == True:
    wififile = open('/boot/wifi.txt')
    wifi = wififile.readline()
    wififile.close
    if (wifi != ''):
        print("Wifi changes detected - running homewifi script")
        homewifi = 'sudo python /sbin/piforce/homewifi.py '+wifi
        os.system(homewifi)

if os.path.exists('/boot/reset.txt') == True:
    print("Reset.txt file detected - running hotspotrestore script")
    os.remove('/boot/reset.txt')
    hotspot = 'sudo python /sbin/piforce/hotspotrestore.py'
    os.system(hotspot)
    reboot = 'sudo reboot'
    os.system(reboot)

relayfile = open('/sbin/piforce/relaymode.txt')
relaymode = relayfile.readline()
relayfile.close
print("Relay mode is set to", relaymode)
zerofile = open('/sbin/piforce/zeromode.txt')
zeromode = zerofile.readline()
zerofile.close
print("Time hack zero mode is set to", zeromode)

if (bootmode == 'single'):
    print("Single boot mode is enabled - running singleboot script")
    cmd = 'sudo python3 /sbin/piforce/singleboot.py &'
    os.system(cmd)

if (powermode == 'auto-off'):
    print("Auto power off mode started - 10 minutes countdown")
    shutdwn = 'sudo shutdown -h -t 600'
    os.system(shutdwn)

