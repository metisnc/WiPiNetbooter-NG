#!/usr/bin/env python3 -u
from evdev import *
from time import time
from time import sleep
from select import select
import os, subprocess, sys, logging

logging.basicConfig(filename="/var/log/menulauncher.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
sys.stderr.write = logger.error
sys.stdout.write = logger.info

osmfile = open('/sbin/piforce/osmpermode.txt')
osmmode = osmfile.readline()
osmfile.close

activedimm = sys.argv[1]
mode = sys.argv[2]

print("menulauncher script started")
print("active dimm is", activedimm)
print("mode is", mode)
print("osmmode is", osmmode)

def start_menu():
    print('Launching Menu ...')
    p = subprocess.Popen(['python3', '/sbin/piforce/dm_netboot/netdimm_menu', activedimm, '/boot/roms', '--verbose'], stdout=subprocess.PIPE)
    return p.pid

def detect_key_hold(hold_time_sec, activedimm, pid):
    dev = InputDevice('/dev/input/event0')
    state = {}
    buttonarray = []
    Running = True
    first = True
    while Running:
        r, _, _ = select([dev], [], [], 0.1)
        if (len(buttonarray) == 3 and 315 in buttonarray):
            print('Kill previous instance of netdimm_menu ...')
            if first:
                print('First run ...')
                os.system("kill -9 "+str(pid))
                first = False
            else:
                print('Subsequent run ...')
                os.system("kill -9 "+str(activepid))
            print('Launch the menu...')
            activepid = start_menu()
            buttonarray.clear()
            state.clear()
            sleep(10)
            #dev.close()
            #Running = False
        if r:
            for event in dev.read():
                if event.type == ecodes.EV_KEY:
                    # When the button is pressed, record the time
                    if event.value == 1:
                        state[event.code] = event.timestamp(), event
                    # When released, remove it from the state map and the array if it was previously held
                    if event.value == 0 and event.code in state:
                        del state[event.code]
                        if event.code in buttonarray:
                            buttonarray.remove(event.code)

        now = time()
        for code, ts_event in list(state.items()):
            ts, event = ts_event
            # Check hold time and add to array if greater
            if (now - ts) >= hold_time_sec:
                if not (code in buttonarray):
                    buttonarray.append(code)
                    yield event
                    print(buttonarray)
        continue

if (mode == 'openjvs'):
    print("Starting netdimm_menu script in OpenJVS mode")
    p1 = subprocess.Popen(['python3', '/sbin/piforce/dm_netboot/netdimm_menu', activedimm, '/boot/roms', '--verbose'], stdout=subprocess.PIPE)
    for event in detect_key_hold(3, activedimm, p1.pid):
        print('a button is being held')
else:
    print('Launch the menu...')
    print("Starting netdimm_menu script in default mode")
    if (osmmode == 'replay'):
        cp = subprocess.Popen(['python3', '/sbin/piforce/dm_netboot/netdimm_menu', activedimm, '/boot/roms', '--verbose', '--persistent'], preexec_fn=os.setsid)
    else:
        cp = subprocess.Popen(['python3', '/sbin/piforce/dm_netboot/netdimm_menu', activedimm, '/boot/roms', '--verbose'], preexec_fn=os.setsid)
