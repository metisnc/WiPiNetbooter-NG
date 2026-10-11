import RPi.GPIO as GPIO
from queue import Queue, Empty
import time
import os
import subprocess

queue = Queue()
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)
GPIO.setup(19, GPIO.IN)
GPIO.setup(20, GPIO.IN)
GPIO.setup(21, GPIO.IN)

def my_callback():
    print('Rotary Turned!','\n')
    openjvscheck = subprocess.getoutput("pgrep openjvs -a | awk '{ print $3 }'")
    if (openjvscheck != ''):
        openjvskillcmd = 'killall -9 openjvs'
        os.system(openjvskillcmd)
        print("Starting OpenJVS with no mapping file")
        openjvscmd = 'sudo openjvs &'
        os.system(openjvscmd)

GPIO.add_event_detect(18, GPIO.BOTH, queue.put, bouncetime=250)
GPIO.add_event_detect(19, GPIO.BOTH, queue.put, bouncetime=250)
GPIO.add_event_detect(20, GPIO.BOTH, queue.put, bouncetime=250)
GPIO.add_event_detect(21, GPIO.BOTH, queue.put, bouncetime=250)

while True:
    if not queue.empty():
        my_callback()
        channel = queue.get_nowait()
        time.sleep(0.01)
        queue.queue.clear()
    time.sleep(0.1)
    pass

