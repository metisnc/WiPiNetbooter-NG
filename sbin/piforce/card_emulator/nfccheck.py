#!/usr/bin/python -u
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardRequestTimeoutException
from smartcard.CardType import AnyCardType
from smartcard.util import *
from smartcard import util
from time import sleep
import os
import sys
import codecs

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
    cardstart = 0x04
    cardend = 0x81
    cardresult = []
    printresult = []
    cardtype = 'none'

    open('/var/log/cardcheck/NFC_Check', 'w').close()
    print('<br><b>Card Data Check</b><br>')
    print('<br>Setting Control File To Checking Mode<br>')
    controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
    controlfile.write('checking')
    controlfile.flush()
    controlfile.close
    print('Control File Set To Checking Mode<br>')

    # create the request. Wait for up to x seconds for a card to be attached
    request = CardRequest(timeout=10, cardType=card_type)

    # listen for the card
    while True:
        service = None
        try:
            service = request.waitforcard()
        except CardRequestTimeoutException:
            print("ERROR: No card detected<br>")
            break

        sleep(0.1)
        conn = service.connection
        conn.connect()
        card_atr = toHexString(conn.getATR())

        if ("03 06 03 00 02" in card_atr):
            print("Mifare 4k card detected<br>")
            card_format = "mifare_4k"
            cardstart = 0x04
            cardend = 0xAF
            datalength = 2056

        if ("03 06 03 00 01" in card_atr):
            print("Mifare 1k card detected<br>")
            card_format = "mifare_1k"
            cardstart = 0x04
            cardend = 0x3F
            datalength = 720

        if ("03 06 03 00 03" in card_atr):
            print("NTAG card detected<br>")
            card_format = "ntag"
            cardstart = 0x04
            cardend = 0x81

        if ("mifare" in card_format):
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
                    auth = util.toBytes("FF 86 00 00 05 01 00 "+xhex+" 60 00")
                    authsector, sw1, sw2 = conn.transmit(auth)
                if (authcounter % 4 != 0):
                    get_data = util.toBytes("FF B0 00 "+xhex+" 10")
                    card_data, sw1, sw2 = conn.transmit(get_data)
                    cardresult = [*cardresult, *card_data]
                    status = util.toHexString([sw1, sw2])
                blockcounter += 1
                authcounter += 1

        if (card_format == "ntag"):
            for x in range(cardstart, cardend):
                xhex = hex(x).lstrip('0x')
                if len(xhex) == 1:
                    xhex = "0"+str(xhex)
                get_data = util.toBytes("FF B0 00 "+xhex+" 04")
                card_data, sw1, sw2 = conn.transmit(get_data)
                cardresult = [*cardresult, *card_data]
                status = util.toHexString([sw1, sw2])

        if (status == "90 00"):

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

            print('Data Read Successful<br>')
            print('Card detected is type: '+savetype+'<br>')
            lightbuzz = util.toBytes("FF 00 40 71 04 03 03 01 02")
            writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)

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
            if nullcheck:
                print('All values are the same - card is blank<br>')
            elif ('?>' in cardprinttext):
                if ('53 45 47 41 42 46 46 37' in cardsavehex):
                    cardtype = 'idas'
                    cardregion = 'en'
                if ('53 45 47 41 42 45 4D 37' in cardsavehex):
                    cardtype = 'idas'
                    cardregion = 'jp'
                if ('53 45 47 41 42 46 53 30' in cardsavehex):
                    cardtype = 'id2'
                    cardregion = 'en'
                if ('53 45 47 41 42 46 4B 32' in cardsavehex):
                    cardtype = 'id2'
                    cardregion = 'jp'
                if ('53 45 47 41 42 48 52 33' in cardsavehex):
                    cardtype = 'id3'
                    cardregion = 'en'
                if ('53 45 47 41 42 48 48 33' in cardsavehex):
                    cardtype = 'id3'
                    cardregion = 'jp'
                if ('53 45 47 41 42 47 47 34' in cardsavehex):
                    cardtype = 'fzero'
                if ('1135B,1155C,1175D' in cardprinttext):
                    cardtype = 'mkgp'
                if ('1133C,1153D,1173E' in cardprinttext):
                    cardtype = 'mkgp2'
                if ('ＨＰ／B"' in cardprinttext):
                    cardtype = 'wmmt'
                if ('ＨＰ／B  ' in cardprinttext):
                    cardtype = 'wmmt2'
                file = open('/var/www/html/cards/'+cardtype+'/NFC_Check.printdata.php', 'w')
                file.write(cardprinttext)
                file.flush()
                file.close()
                print("Valid Card Save Data Found<br>")
                #print("Copying Card Data to Web Folder<br>")
            elif (savetype == 'NFCGAME'):
                text = codecs.decode(util.toHexString(cardresult,PACK),'hex')
                nfcgametext = (codecs.decode(text, 'utf-8')).strip('\x00')
                nfcgame = nfcgametext.split(':')
                nfcgame = nfcgame[1].split('-')
                print('Game is',nfcgame[1],'<br>')
            else:
                print('Data Found But Not Valid Card Data<br>')
                lightbuzz = util.toBytes("FF 00 40 71 04 03 03 01 02")
                writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)
        else:
            print("Data Read Failed<br>")
            lightbuzz = util.toBytes("FF 00 40 71 04 03 03 03 02")
            writelightbuzz, sw1, sw2 = conn.transmit(lightbuzz)
        break

    file = open('/var/log/cardcheck/NFC_Check', 'w')
    file.write(cardtype)
    file.flush()
    file.close()
    if ('id' in cardtype):
        file = open('/var/log/cardcheck/NFC_Region', 'w')
        file.write(cardregion)
        file.flush()
        file.close()
    print('Setting Control File Back To Reading Mode<br>')
    print('Card Check Complete<br>')
    controlfile = open('/sbin/piforce/nfccontrol.txt', 'w')
    controlfile.write('reading')
    controlfile.close
