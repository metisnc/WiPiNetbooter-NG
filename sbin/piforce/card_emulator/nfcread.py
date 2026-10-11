from time import sleep
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import *
from smartcard import util
import glob
import codecs
import subprocess
import os

class transmitobserver(CardObserver):

    def __init__(self):
        self.cards = []

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        controlfile = open('/sbin/piforce/nfccontrol.txt', 'r')
        nfcstate = controlfile.read()
        controlfile.close
        if nfcstate != 'reading':
            self.cards = []

        for card in addedcards:
            if card not in self.cards:
                DropFolderGlobPath = "/var/log/activecard/*"
                status = ''
                cardresult = []
                printresult = []
                self.cards += [card]
                card_atr = toHexString(card.atr)
                print("+Inserted: ", card_atr)

                if ("03 06 03 00 02" in card_atr):
                    print("Mifare 4k card detected")
                    card_format = "mifare_4k"
                    cardstart = 0x04
                    cardend = 0xAF
                    datalength = 2056

                if ("03 06 03 00 01" in card_atr):
                    print("Mifare 1k card detected")
                    card_format = "mifare_1k"
                    cardstart = 0x04
                    cardend = 0x3F
                    datalength = 720

                if ("03 06 03 00 03" in card_atr):
                    print("NTAG card detected")
                    card_format = "ntag"
                    cardstart = 0x04
                    cardend = 0x81

                if ("mifare" in card_format and nfcstate == 'reading'):
                    card.connection = card.createConnection()
                    card.connection.connect()
                    key = util.toBytes("FF 82 00 00 06 FF FF FF FF FF FF")
                    loadkey, sw1, sw2 = card.connection.transmit(key)
                    auth = util.toBytes("FF 86 00 00 05 01 00 04 60 00")
                    authblock, sw1, sw2 = card.connection.transmit(auth)
                    blockcounter = 0
                    authcounter = 1
                    for x in range(cardstart, cardend):
                        xhex = hex(x).lstrip('0x')
                        if len(xhex) == 1:
                            xhex = "0"+str(xhex)
                        if (blockcounter % 4 == 0):
                            auth = util.toBytes("FF 86 00 00 05 01 00 "+xhex+" 60 00")
                            authsector, sw1, sw2 = card.connection.transmit(auth)
                        if (authcounter % 4 != 0):
                            get_data = util.toBytes("FF B0 00 "+xhex+" 10")
                            card_data, sw1, sw2 = card.connection.transmit(get_data)
                            cardresult = [*cardresult, *card_data]
                            status = util.toHexString([sw1, sw2])
                            #print(status)
                        blockcounter += 1
                        authcounter += 1

                if (card_format == "ntag" and nfcstate == 'reading'):
                    card.connection = card.createConnection()
                    card.connection.connect()
                    for x in range(cardstart, cardend):
                        xhex = hex(x).lstrip('0x')
                        if len(xhex) == 1:
                            xhex = "0"+str(xhex)
                        get_data = util.toBytes("FF B0 00 "+xhex+" 04")
                        card_data, sw1, sw2 = card.connection.transmit(get_data)
                        cardresult = [*cardresult, *card_data]
                        status = util.toHexString([sw1, sw2])

                if (status == "90 00" and nfcstate == 'reading'):

                    splitposition = 0
                    php = [60, 63, 112, 104, 112]
                    id8jp = [66, 77, 76, 32, 0, 0, 0, 0]
                    id8ex = [66, 78, 75, 32, 0, 0, 0, 0]
                    nfcgame = [110, 102, 99, 103, 97, 109, 101]
                    phpresult = [(i, i+len(php)) for i in range(len(cardresult)-len(php)+1) if cardresult[i:i+len(php)] == php]
                    id8jpresult = [(i, i+len(id8jp)) for i in range(len(cardresult)-len(id8jp)+1) if cardresult[i:i+len(id8jp)] == id8jp]
                    id8exresult = [(i, i+len(id8ex)) for i in range(len(cardresult)-len(id8ex)+1) if cardresult[i:i+len(id8ex)] == id8ex]
                    nfcgameresult = [(i, i+len(nfcgame)) for i in range(len(cardresult)-len(nfcgame)+1) if cardresult[i:i+len(nfcgame)] == nfcgame]

                    if phpresult:
                        splitposition = phpresult[0][0]
                    if (splitposition == 77):
                        savetype = 'NAMCO'
                        datalength = 77
                        printstart = 77
                    elif (splitposition == 84):
                        savetype = 'NAMCO'
                        datalength = 77
                        printstart = 80
                    elif (splitposition == 215):
                        savetype = 'SEGA'
                        datalength = 215
                        printstart = 215
                    elif (splitposition == 220):
                        savetype = 'SEGA'
                        datalength = 215
                        printstart = 216
                    elif (id8jpresult or id8exresult):
                        savetype = 'ID8'
                        printstart = 0
                    elif (nfcgameresult):
                        savetype = 'NFCGAME'
                        datalength = 215
                        printstart = 0
                    else:
                        savetype = 'UNKNOWN'
                        datalength = 215
                        printstart = 0

                    print('Data Read Successful')
                    print('Card detected is type: '+savetype)
                    lightbuzz = util.toBytes("FF 00 40 71 04 03 03 01 02")
                    writelightbuzz, sw1, sw2 = card.connection.transmit(lightbuzz)

                    if (printstart > 0):
                        text = codecs.decode(util.toHexString(cardresult[printstart:],PACK),'hex')
                        cardprinttext = (codecs.decode(text, 'utf-8')).strip('\x00')
                        cardsavehex = util.toHexString(cardresult[:printstart])
                    else:
                        cardsavehex = util.toHexString(cardresult)
                        cardprinttext = ""
                    cardvaluelist = []

                    for i in range(datalength):
                        cardpartvalue = int("0x" + cardsavehex[i*3 : i*3+2],0)
                        cardvaluelist.append(cardpartvalue)
                    nullcheck = cardvaluelist.count(cardvaluelist[0]) == len(cardvaluelist)
                    dropfoldercheck = glob.glob(DropFolderGlobPath)

                    if nullcheck:
                        print('All values are the same - card is blank')
                        if not dropfoldercheck:
                            print('Blank File Will Be Created For Card Save')
                            file = open('/sbin/piforce/nfcwriteback.txt', 'w')
                            file.write('yes')
                            file.flush()
                            file.close()
                        else:
                            print('Card Already Present in Drop Folder')
                    elif (savetype != 'UNKNOWN' and savetype != 'NFCGAME'):
                        cardbytes = b""
                        cardbytes = bytearray(cardvaluelist)
                        if not dropfoldercheck:
                            file = open('/var/log/activecard/NFC_Card', 'wb')
                            file.write(cardbytes)
                            file.flush()
                            file.close()
                            if (printstart > 0):
                                file = open('/var/log/printdata/NFC_Card.printdata.php', 'w')
                                file.write(cardprinttext)
                                file.flush()
                                file.close()
                            file = open('/sbin/piforce/nfcwriteback.txt', 'w')
                            file.write('yes')
                            file.flush()
                            file.close()
                            print("Valid Card Save Data Found")
                            print("No Card Present in Drop Folder")
                            print("Copying Card Data to Drop Folder")
                            print("Card Data Follows:")
                            print("")
                            print(cardsavehex)
                            print("")
                            if (printstart > 0):
                                print(cardprinttext)
                        else:
                            print("Valid Card Save Data Found")
                            print("Card Already Present in Drop Folder")
                            print("Card Data Follows:")
                            print("")
                            print(cardsavehex)
                            print("")
                            if (printstart > 0):
                                print(cardprinttext)
                    elif (savetype == 'NFCGAME'):
                        text = codecs.decode(util.toHexString(cardresult,PACK),'hex')
                        nfcgametext = (codecs.decode(text, 'utf-8')).strip('\x00')
                        nfcgame = nfcgametext.split(':')
                        print('Game is',nfcgame[1])
                        cp = subprocess.Popen(['python3', '/sbin/piforce/nfcloader.py', nfcgame[1]], preexec_fn=os.setsid)
                    else:
                        print('Data Found But Not Valid Card Data')
                        lightbuzz = util.toBytes("FF 00 40 71 04 03 03 01 02")
                        print(cardsavehex)
                        writelightbuzz, sw1, sw2 = card.connection.transmit(lightbuzz)
                else:
                    print("Data Read Failed")
                    lightbuzz = util.toBytes("FF 00 40 71 04 03 03 03 02")
                    writelightbuzz, sw1, sw2 = card.connection.transmit(lightbuzz)

        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))
            if card in self.cards:
                self.cards.remove(card)

if __name__ == '__main__':
    print("Present your NFC Smart Card")
    cardmonitor = CardMonitor()
    cardobserver = transmitobserver()
    cardmonitor.addObserver(cardobserver)
    x = False
    while not x:
        sleep(100)