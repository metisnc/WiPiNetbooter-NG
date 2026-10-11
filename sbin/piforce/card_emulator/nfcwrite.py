#!/usr/bin/python -u
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardRequestTimeoutException
from smartcard.CardType import AnyCardType
from smartcard import util
from smartcard.util import *
from time import sleep
import sys
import os
import argparse

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

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', help='Mode of card write. Example: -m sega or -m namco or -m id8')
    parser.add_argument('-f', '--datafile', help='Card save data file.')
    parser.add_argument('-p', '--printfile', help='Card save print file.')
    args = parser.parse_args()
    writemode = args.mode
    cardfile = args.datafile
    if not args.printfile:
        print('<br>No print file provided')
    else:
        printfile = args.printfile

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
            print('Print Data Write Timeout<br>')
            print('Setting Control File Back To Reading Mode<br>')
            print('Card Write Failed<br>')
            controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
            controlfile.write('reading')
            controlfile.close
            exit(-1)

        # when a card is attached, open a connection
        sleep(0.1)
        conn = service.connection
        conn.connect()
        card_atr = toHexString(conn.getATR())
        #print("+Inserted: ",card_atr)

        if ("03 06 03 00 02" in card_atr):
            print("Mifare 4k card detected<br>")
            card_format = "mifare_4k"
            CHUNK_SIZE = 16
            card_size = 3072
        if ("03 06 03 00 01" in card_atr):
            print("Mifare 1k card detected<br>")
            card_format = "mifare_1k"
            CHUNK_SIZE = 16
            card_size = 720
        if ("03 06 03 00 03" in card_atr):
            print("NTAG card detected<br>")
            card_format = "ntag"
            CHUNK_SIZE = 4
            card_size = 504

        if (writemode == 'sega' and 'mifare' in card_format):
            cardstart = 0x04
            cardend = 0x3F
            #printstart = 0x17
            #printend = 0x3F
        if (writemode == 'sega' and card_format == 'ntag'):
            cardstart = 0x04
            cardend = 0x81
            #printstart = 0x3B
            #printend = 0x81
        if (writemode == 'namco' and 'mifare' in card_format):
            cardstart = 0x04
            cardend = 0x3F
            #printstart = 0x0B
            #printend = 0x3F
        if (writemode == 'namco' and card_format == 'ntag'):
            cardstart = 0x04
            cardend = 0x81
            #printstart = 0x19
            #printend = 0x81
        if (writemode == 'id8'):
            cardstart = 0x04
            cardend = 0xAF

        if (args.printfile):
            filenames = [cardfile,printfile]
            with open('/var/log/cardwrite', 'wb') as outfile:
                for fname in filenames:
                    with open(fname, 'rb') as infile:
                        outfile.write(infile.read())
            cardfile = '/var/log/cardwrite'

        file_size = os.stat(cardfile)
        if (file_size.st_size > card_size):
            print("ERROR: Data too large for card<br>")
            print('Setting Control File Back To Reading Mode<br>')
            print('Card Write Failed<br>')
            controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
            controlfile.write('reading')
            controlfile.close
            exit(-1)

        if ('mifare' in card_format):
            # set key and authenticate initial sector
            key = util.toBytes("FF 82 00 00 06 FF FF FF FF FF FF")
            loadkey, sw1, sw2 = conn.transmit(key)
            auth = util.toBytes("FF 86 00 00 05 01 00 04 60 00")
            authblock, sw1, sw2 = conn.transmit(auth)
            f = open(cardfile, 'rb')
            chunk = f.read(CHUNK_SIZE)
            blockcounter = 0
            authcounter = 1

            while chunk:
                for x in range(cardstart, cardend):
                    chunkdata_list = util.toBytes(chunk.hex())
                    xhex = hex(x).lstrip('0x')
                    if len(xhex) == 1:
                        xhex = "0"+str(xhex)
                    if len(chunkdata_list) < 16:
                        padding = 16 - len(chunkdata_list)
                        for p in range(0,padding):
                             chunkdata_list.append(0)
                    if (blockcounter % 4 == 0):
                        # authenticate sector
                        auth = util.toBytes("FF 86 00 00 05 01 00 "+xhex+" 60 00")
                        #print("Auth :",auth)
                        authsector, sw1, sw2 = conn.transmit(auth)
                        status = util.toHexString([sw1, sw2])
                        #print(status)
                    if (authcounter % 4 != 0):
                        # write data to block
                        command_list = (util.toBytes("FF D6 00 "+xhex+" 10 "))
                        write_data = [*command_list, *chunkdata_list]
                        #print("Write :",write_data)
                        writestuff, sw1, sw2 = conn.transmit(write_data)
                        status = util.toHexString([sw1, sw2])
                        #print(status)
                        chunk = f.read(CHUNK_SIZE) #read the next chunk
                    blockcounter += 1
                    authcounter += 1
                    if not chunk:
                        break
            f.close()

            status = util.toHexString([sw1, sw2])
            if (status == '90 00'):
                print('Data Write Successful<br>')
                lightbuzz = util.toBytes("FF 00 40 41 04 03 03 02 02")
                writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)
            else:
                print('Data Write Unsuccessful<br>')
                print('Setting Control File Back To Reading Mode<br>')
                print('Card Write Complete<br>')
                controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
                controlfile.write('reading')
                controlfile.close
                break

#            if (args.printfile):
#                # set key and authenticate initial sector
#                key = util.toBytes("FF 82 00 00 06 FF FF FF FF FF FF")
#                loadkey, sw1, sw2 = conn.transmit(key)
#                if (writemode == 'sega'):
#                    auth = util.toBytes("FF 86 00 00 05 01 00 16 60 00")
#                    authblock, sw1, sw2 = conn.transmit(auth)
#                if (writemode == 'namco'):
#                    auth = util.toBytes("FF 86 00 00 05 01 00 0A 60 00")
#                    authblock, sw1, sw2 = conn.transmit(auth)
#                f = open(printfile, 'rb')
#                chunk = f.read(CHUNK_SIZE)
#                while chunk:
#                    for x in range(printstart, printend):
#                        chunkdata_list = util.toBytes(chunk.hex())
#                        xhex = hex(x).lstrip('0x')
#                        if len(xhex) == 1:
#                            xhex = "0"+str(xhex)
#                        if len(chunkdata_list) < 16:
#                            padding = 16 - len(chunkdata_list)
#                            for p in range(0,padding):
#                                 chunkdata_list.append(0)
#                        if (blockcounter % 4 == 0):
#                            # authenticate sector
#                            auth = util.toBytes("FF 86 00 00 05 01 00 "+xhex+" 60 00")
#                            print("Auth :",auth)
#                            authsector, sw1, sw2 = conn.transmit(auth)
#                        if (authcounter % 4 != 0):
#                            # write data to block
#                            command_list = (util.toBytes("FF D6 00 "+xhex+" 10 "))
#                            write_data = [*command_list, *chunkdata_list]
#                            print("Write :",write_data)
#                            writestuff, sw1, sw2 = conn.transmit(write_data)
#                            status = util.toHexString([sw1, sw2])
#                            print(status)
#                            chunk = f.read(CHUNK_SIZE) #read the next chunk
#                        blockcounter += 1
#                        authcounter += 1
#                        if not chunk:
#                            break
#                f.close()
#                status = util.toHexString([sw1, sw2])
#                if (status == '90 00'):
#                    lightbuzz = util.toBytes("FF 00 40 41 04 03 03 02 02")
#                    writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)
#                    print('Print Write Successful<br>')
#                else:
#                    print('Print Write Unsuccessful<br>')
#                    print('Setting Control File Back To Reading Mode<br>')
#                    print('Card Write Complete<br>')
#                    controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
#                    controlfile.write('reading')
#                    controlfile.close
#                    break
                
        if (card_format == 'ntag'):
            f = open(cardfile, 'rb')
            chunk = f.read(CHUNK_SIZE)
            while chunk:
                for x in range(cardstart, cardend):
                    xhex = hex(x).lstrip('0x')
                    if len(xhex) == 1:
                        xhex = "0"+str(xhex)
                    if chunk:
                        chunkdata_list = util.toBytes(chunk.hex())
                        if len(chunkdata_list) < 4:
                            padding = 4 - len(chunkdata_list)
                            for p in range(0,padding):
                                chunkdata_list.append(0)
                        command_list = (util.toBytes("FF D6 00 "+xhex+" 04 "))
                        write_data = [*command_list, *chunkdata_list]
                        writestuff, sw1, sw2 = conn.transmit(write_data)
                        chunk = f.read(CHUNK_SIZE) #read the next chunk
                    else:
                        command_list = (util.toBytes("FF D6 00 "+xhex+" 04 00 00 00 00"))
                        write_data = command_list
                        writestuff, sw1, sw2 = conn.transmit(write_data)
            f.close()
            status = util.toHexString([sw1, sw2])
            if (status == '90 00'):
                print('Data Write Successful<br>')
                lightbuzz = util.toBytes("FF 00 40 41 04 03 03 02 02")
                writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)
            else:
                print('Data Write Unsuccessful<br>')
                print('Setting Control File Back To Reading Mode<br>')
                print('Card Write Complete<br>')
                controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
                controlfile.write('reading')
                controlfile.close
                break

#            f = open(printfile, 'rb')
#            chunk = f.read(CHUNK_SIZE)
#            while chunk:
#                for x in range(printstart, printend):
#                    chunkdata_list = util.toBytes(chunk.hex())
#                    xhex = hex(x).lstrip('0x')
#                    if len(xhex) == 1:
#                        xhex = "0"+str(xhex)
#                    if len(chunkdata_list) < 4:
#                        padding = 4 - len(chunkdata_list)
#                        for p in range(0,padding):
#                            chunkdata_list.append(0)
#                    command_list = (util.toBytes("FF D6 00 "+xhex+" 04 "))
#                    write_data = [*command_list, *chunkdata_list]
#                    writestuff, sw1, sw2 = conn.transmit(write_data)
#                    chunk = f.read(CHUNK_SIZE) #read the next chunk
#                    if not chunk:
#                        break
#            f.close()
#            status = util.toHexString([sw1, sw2])
#            if (status == '90 00'):
#                lightbuzz = util.toBytes("FF 00 40 41 04 03 03 02 02")
#                writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)
#                print('Print Write Successful<br>')
#            else:
#                print('Print Write Unsuccessful<br>')
#                print('Setting Control File Back To Reading Mode<br>')
#                print('Card Write Complete<br>')
#                controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
#                controlfile.write('reading')
#                controlfile.close
#                break

        status = util.toHexString([sw1, sw2])
        if (status == '90 00'):
            print('Card Write Successful<br>')
            controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
            controlfile.write('reading')
            controlfile.close
            break
        else:
            print('Data Write Error<br>')
            print('Setting Control File Back To Reading Mode<br>')
            print('Card Write Complete<br>')
            controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
            controlfile.write('reading')
            controlfile.close
            break