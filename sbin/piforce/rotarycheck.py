import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)
GPIO.setup(19, GPIO.IN)
GPIO.setup(20, GPIO.IN)
GPIO.setup(21, GPIO.IN)

position = 0

pin1 = GPIO.input(18)
if not pin1:
    position += 1
pin2 = GPIO.input(19)
if not pin2:
    position += 2
pin3 = GPIO.input(20)
if not pin3:
    position += 4
pin4 = GPIO.input(21)
if not pin4:
    position += 8

print(position)