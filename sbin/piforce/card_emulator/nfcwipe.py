#!/usr/bin/python -u
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardRequestTimeoutException
from smartcard.CardType import AnyCardType
from smartcard import util
from time import sleep
import sys

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

sys.stdout = Unbuffered(sys.stdout)

if __name__ == '__main__':
    # respond to the insertion of any type of smart card

    card_type = AnyCardType()
    print('<br>Setting Control File To Writing Mode<br>')
    controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
    controlfile.write('writing')
    controlfile.flush()
    controlfile.close
    print('Control File Set To Writing Mode<br>')

    # create the request. Wait for up to x seconds for a card to be attached
    request = CardRequest(timeout=10, cardType=card_type)

    # listen for the card
    while True:
        service = None
        try:
            service = request.waitforcard()
        except CardRequestTimeoutException:
            print("ERROR: No card detected<br>")
            print('Print Data Wipe Timeout<br>')
            print('Setting Control File Back To Reading Mode<br>')
            print('Card Wipe Failed<br>')
            controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
            controlfile.write('reading')
            controlfile.close
            exit(-1)

    # when a card is attached, open a connection
        sleep(0.1)
        conn = service.connection
        conn.connect()
        card_atr = util.toHexString(conn.getATR())

        if ("03 06 03 00 02" in card_atr):
            print("Mifare 4k card detected<br>")
            card_format = "mifare_4k"
            cardstart = 0x04
            cardend = 0xFF
        if ("03 06 03 00 01" in card_atr):
            print("Mifare 1k card detected<br>")
            card_format = "mifare_1k"
            cardstart = 0x04
            cardend = 0x3F
        if ("03 06 03 00 03" in card_atr):
            print("NTAG card detected<br>")
            card_format = "ntag"
            cardstart = 0x04
            cardend = 0x81

        if (card_format == 'ntag'):
            for x in range(cardstart, cardend):
                xhex = hex(x).lstrip('0x')
                if len(xhex) == 1:
                    xhex = "0"+str(xhex)
                command_list = (util.toBytes("FF D6 00 "+xhex+" 04 00 00 00 00"))
                write_data = command_list
                writestuff, sw1, sw2 = conn.transmit(write_data)

        if ('mifare' in card_format):
            key = util.toBytes("FF 82 00 00 06 FF FF FF FF FF FF")
            loadkey, sw1, sw2 = conn.transmit(key)
            auth = util.toBytes("FF 86 00 00 05 01 00 04 60 00")
            authblock, sw1, sw2 = conn.transmit(auth)
            blockcounter = 0
            authcounter = 1
            for x in range(cardstart, cardend):
                xhex = hex(x).lstrip('0x')
                if len(xhex) == 1:
                    xhex = "0"+str(xhex)
                if (blockcounter % 4 == 0):
                    # authenticate sector
                    auth = util.toBytes("FF 86 00 00 05 01 00 "+xhex+" 60 00")
                    authsector, sw1, sw2 = conn.transmit(auth)
                    status = util.toHexString([sw1, sw2])
                    #print(status)
                if (authcounter % 4 != 0):
                    # write data to block
                    command_list = (util.toBytes("FF D6 00 "+xhex+" 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
                    write_data = command_list
                    writestuff, sw1, sw2 = conn.transmit(write_data)
                    #status = util.toHexString([sw1, sw2])
                    #print(status)
                blockcounter += 1
                authcounter += 1

        status = util.toHexString([sw1, sw2])
        if (status == '90 00'):
            lightbuzz = util.toBytes("FF 00 40 41 04 03 03 02 02")
            writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)
            print('Card Wipe Successful<br>')
            print('Setting Control File Back To Reading Mode<br>')
            controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
            controlfile.write('reading')
            controlfile.close
        break