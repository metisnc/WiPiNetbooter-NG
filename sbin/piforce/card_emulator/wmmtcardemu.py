#!/usr/bin/env python3

"""
Wangan Midnight Maximum Tune - Card Reader Emulator v1.0
Programmed by: winteriscoming
Special thanks to: MetalliC

Additional code by: Chunksin

Card command constants referenced from Dolphin emulator Triforce branch.

Serial interface referenced from jpnevulator.py script.

jpnevulator info:

jpnevulator.py version 2.1.3
Copyright (C) 2015 Philipp Klaus
This is free software.  You may redistribute copies of it under the terms of
the GNU General Public License <http://www.gnu.org/licenses/gpl.html>.
There is NO WARRANTY, to the extent permitted by law.

"""

## WMMT Card Command Constants ##
CARD_INIT	        = "10"
CARD_GET_CARD_STATE	= "20"
CARD_IS_PRESENT		= "40"
CARD_LOAD_CARD		= "B0"
CARD_CLEAN_CARD		= "A0"
CARD_READ		= "33"
CARD_WRITE		= "53"
CARD_WRITE_TEXT		= "7C"
CARD_78			= "78"
CARD_7A			= "7A"
CARD_7D			= "7D"
CARD_D0			= "D0"
CARD_80			= "80"

import argparse
import sys
import time
import textwrap
from datetime import datetime as dt
import binascii
import serial
import os
import subprocess
import threading
import glob
from queue import Queue
from pathlib import Path
from time import sleep
import filecmp
import shutil
import shortuuid

def exists(path):
    try:
        os.stat(path)
    except OSError:
        return False
    return True

pidpath = '/sbin/piforce/card_emulator/pid.txt'

if exists(pidpath):
    with open(pidpath, "r") as pidfile:
        lastpid = pidfile.readline()
else:
    lastpidfile = open(pidpath, "w")
    lastpidfile.close()

try:
    print('---> Previous process PID:',lastpid)
    os.kill(int(lastpid), 9)
except:
    pass

currentpid = os.getpid()
bashCommand1 = 'sudo echo -n '+str(currentpid)+' | tee '+pidpath
os.system(bashCommand1)

nocard = True
stop_thread = False
if not os.path.exists('/var/log/activecard'):
    print('---> Creating temporary drop folder as /var/log/activecard')
    os.makedirs('/var/log/activecard')
if not os.path.exists('/var/log/printdata'):
    print('---> Creating temporary data folder as /var/log/printdata')
    os.makedirs('/var/log/printdata')
if not os.path.exists('/var/log/cardcheck'):
    print('---> Creating temporary data folder as /var/log/cardcheck')
    os.makedirs('/var/log/cardcheck')

def HexBytestoString(string):
    length=0;
    length=len(string)
    crc = 0
    stringval = ""
    fullstring=""
    for i in range (0,length,1):
        stringval = str(hex(string[i])) +'\\'
        fullstring=fullstring+stringval
        #print(hex(num))
    return fullstring

def autogen():
    BasePath = "/var/log/activecard/"
    BaseName = BasePath+"card"
    Suffix = shortuuid.ShortUUID().random(length=6)
    NewCardFileName = "_".join([BaseName, Suffix]) # Temp card file name generated
    return NewCardFileName

def emptydropfolder():
    DropFolderGlobPath = "/var/log/activecard/*"
    CardFiles = glob.glob(DropFolderGlobPath) # Empty the drop folder and printdata folder
    for f in CardFiles:
        os.remove(f)
        
def emptyprintfolder():
    PrintFolderGlobPath = "/var/log/printdata/*"
    PrintFiles = glob.glob(PrintFolderGlobPath)
    for f in PrintFiles:
        os.remove(f)

def cardpoll(threadname, q): # Card polling thread checks drop folder for card file
    global nocard
    global stop_thread
    DropFolderGlobPath = "/var/log/activecard/*" # Drop folder to monitor
    while True:
        while nocard is True:
            if glob.glob(DropFolderGlobPath):
                DropFile = glob.glob(DropFolderGlobPath)
                CardFileName = DropFile[0] # Update CardFileName to be original card file
                print('---> File detected in drop folder:', CardFileName)
                with open(CardFileName, "rb") as in_file: # Open original card file and read contents
                    CardBytes = in_file.read()
                    if len(CardBytes) == 77:
                        print('---> Card data is correct length for WMMT')
                        q.put(CardBytes) # Send card contents to the cardpoll queue
                    else:
                        print('---> Card data invalid length for WMMT')
                        print('---> Clearing card file from drop folder')
                        os.remove(CardFileName)
                nocard = False
            sleep(0.1)
            if stop_thread:
                break
        while nocard is False:
            if not glob.glob(DropFolderGlobPath):
                print("---> Drop folder is empty")
                nocard = True
            sleep(1)
            if stop_thread:
                break

try:
    clock = time.perf_counter
except AttributeError:
    clock = time.time

def port_def(string):
    port, alias = string, None
    return {'port': port, 'alias': alias}
    
def hex_format(chunk):
    try:
        return ' '.join('{:02X}'.format(byte) for byte in chunk)
    except ValueError:
        return ' '.join('{:02X}'.format(ord(byte)) for byte in chunk)

def CommandCode(CommandString):
    CurrentCommand = CommandString[CommandString.find("02")+ 6: CommandString.find("02")+ 8]
    return CurrentCommand

def CommandLookup(CommandString):
    if CommandString == "10": return "CARD_INIT(10)"
    if CommandString == "20": return "CARD_GET_CARD_STATE(20)"
    if CommandString == "40": return "CARD_IS_PRESENT(40)"
    if CommandString == "B0": return "CARD_LOAD_CARD(B0)"
    if CommandString == "A0": return "CARD_CLEAN_CARD(A0)"
    if CommandString == "53": return "CARD_WRITE(53)"
    if CommandString == "33": return "CARD_READ(33)"
    if CommandString == "7C": return "CARD_WRITE_TEXT(7C)"
    if CommandString == "78": return "CARD_78(78)"
    if CommandString == "7A": return "CARD_7A(7A)"
    if CommandString == "7D": return "CARD_7D(7D)"
    if CommandString == "D0": return "CARD_D0(D0)"
    if CommandString == "80": return "CARD_80(80)"
    return "UNKNOWN COMMAND!("+CommandString+")"

def ValidCommand(CommandString):
    if CommandString == "10": return 1
    if CommandString == "20": return 1
    if CommandString == "40": return 1
    if CommandString == "B0": return 1
    if CommandString == "A0": return 1
    if CommandString == "53": return 1
    if CommandString == "33": return 1
    if CommandString == "7C": return 1
    if CommandString == "78": return 1
    if CommandString == "7A": return 1
    if CommandString == "7D": return 1
    if CommandString == "D0": return 1
    if CommandString == "80": return 1
    return 0
    
def CardTranslationWMMT(ChihiroString,CardFileName,Mode):
    CARDString = ChihiroString[ChihiroString.find("02 4E 53 00 00 00 30 31 30")+27: ChihiroString.find("02 4E 53 00 00 00 30 31 30") +27 + 207]
    CardCRC = 0
    CARDString = "4B 33 31 30 30 " + CARDString + "03"
    i=0
    #print (CARDString)
    
    for i in range(75):
        CardPartValue = int("0x" + CARDString[i*3 : i*3+2],0)
        CardCRC = CardCRC^CardPartValue
    CardCRCText = hex(CardCRC)
    ConvertedCardValue = "02 " + CARDString + " " + CardCRCText[2:]
    print ("Converted Card Value: " + ConvertedCardValue)
    CardValueList = []
    
    for i in range(77):
        CardPartValue = int("0x" + ConvertedCardValue[i*3 : i*3+2],0)
        CardValueList.append(CardPartValue)
        
    CardBytes = b""
    CardBytes = bytearray(CardValueList)

    CardFileName = '/boot/config/cards/'+Mode+'/'+os.path.basename(CardFileName)

    with open(CardFileName, "wb") as out_file:
        out_file.write(CardBytes)
    print ("Saved Card Data to " + CardFileName)
    
    with open(CardFileName, "rb") as in_file:
        CardBytes = in_file.read()
    print ("Read in Card Data from " + CardFileName)
    
    return CardBytes, CardFileName

def main():
    CardBytes = b""
    ReadInput = ""
    CurrentCommand = ""
    PriorCommand = ""
    HaveCard = 0
    StepNum = 0
    CleanStep = 0
    Init = 1
    CardLoaded = 0
    GotNewCardData = 0
    Ejected = 0
    LoadCardStepNum = 0
    NewCardFileName = autogen()
    DropFolderGlobPath = "/var/log/activecard/*"
    PrintFolderGlobPath = "/var/log/printdata/*"
    DropFolderPath = "/var/log/activecard/"
    CardFolderRoot = "/boot/config/cards"
    NFCCardFound = False
    NFCCardMatch = False
    NFCCardWrite = ""
    CardWriteFlag = False
    CopyNFCphp = False
    rawfilename = ""
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-cp', '--comport', type=port_def, metavar='COMPORT', help="The serial device. Example: -t COM1")
    parser.add_argument('-f', '--cardfile', help='Name of card file to load. Example: -f CardHexFile')
    parser.add_argument('-m', '--mode', help='Mode of WMMT card emulator. Example: -m wmmt or -m wmmt2')
    
    args = parser.parse_args()

    if not args.comport:
        parser.error('Please specify a serial port! Example: -cp COM1')
        sys.exit(0)
        
    if not args.cardfile:
        print('---> No Card file name provided, using autogen and switching to real time mode') # If no card file name specified default to autogen
        CardFileName = NewCardFileName
    else:
        CardFileName = args.cardfile

    if not args.mode:
        parser.error('Please specify an ID mode! Example: -m wmmt or -m wmmt2')
        sys.exit(0)

    CardFiles = glob.glob(DropFolderGlobPath) # Clear out any existing files from the drop folder before the polling queue starts up
    for f in CardFiles:
        os.remove(f)

    PrintFiles = glob.glob(PrintFolderGlobPath) # Clear out any existing files from the printdata folder
    for f in PrintFiles:
        os.remove(f)
    
    wmmtmode = args.mode
    comport = args.comport
    comport['alias'] = "Chihiro"
    comport['buffer'] = b''
    comport['ser'] = serial.Serial(comport['port'], baudrate=9600, timeout=0, parity=serial.PARITY_NONE, bytesize = serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE)
    comport['last_byte'] = clock()
    #comport['ser'].setRTS(True)
    
    print ("COM port opened and named:", comport['alias'])
    #print("CTS:", comport['ser'].getCTS())

    cardpollq = Queue() # Card polling queue defined and started
    cardpollthread = threading.Thread(target=cardpoll, args=("CardPollingThread", cardpollq))
    cardpollthread.daemon = True
    cardpollthread.start()

    try:
        with open(CardFileName, "rb") as in_file:
            CardBytes = in_file.read()
        print ("---> Read in Card Data from " + CardFileName)
        
        if CardBytes == b"":
            print ("---> " + CardFileName + " card file is empty.  You will have to select to create a new card in the game.")
            HaveCard=0
        else:
            print ("---> " + CardFileName + " appears to contain data.  This card data will be loaded when a game is started.")
            HaveCard=1
    except:
        print ("---> New random filename " + CardFileName + " generated. It will be available for purchase as a new card in the game.")
        HaveCard=0
    

    try:
        while True:
            sleep(0.001)
            new_data = comport['ser'].read()
            if len(new_data) > 0:
                comport['buffer'] += new_data
                comport['last_byte'] = clock()

            if comport['buffer'] and (clock() - comport['last_byte']) > 100000/1E6:
                line = '{0}: {1}\n'.format(dt.now().isoformat(' '), comport['alias'])
                
                sys.stdout.write(line)
                while comport['buffer']:
                    chunk = comport['buffer'][:250]
                    comport['buffer'] = comport['buffer'][250:]
                    fmt = "{{hex:{0}s}}".format(250*3)
                    line = fmt.format(hex=hex_format(chunk))
                    line = line.strip()
                    ReadInput += " " + line
                    line += '\n'
                    
                    sys.stdout.write(line)

                    if not cardpollq.empty(): # Check cardpoll queue for data
                        CardBytes = cardpollq.get_nowait()
                        CardData = CardBytes
                        DropFile = glob.glob(DropFolderGlobPath)
                        if (os.path.basename(DropFile[0]) == 'NFC_Card'): # If the dropped file is called NFC_Card search for existing copy
                            NFCCardFound = True
                            print('---> NFC Data file detected, checking for match')
                            for root, subdirectories, files in os.walk(CardFolderRoot):
                                for file in files:
                                    if not NFCCardMatch:
                                        if filecmp.cmp(DropFile[0], os.path.join(root, file), shallow=False) and not NFCCardMatch:
                                            CardFileName = DropFolderPath+file
                                            shutil.move(DropFile[0], CardFileName)
                                            NFCCardMatch = True
                                            print('---> Match found locally for NFC data:', CardFileName)
                                            
                            if NFCCardFound and not NFCCardMatch:
                                CardFileName = NewCardFileName # No match found for the NFC data so treat as a new card - php data to be handled at card save
                                shutil.move(DropFile[0], NewCardFileName)
                                print('---> No match found locally for NFC data')
                                print('---> Card will be treated as autogen with existing PHP data')
                                CopyNFCphp = True # Set a flag for the php data to be copied out at save time                                
                        else:
                            CardFileName = DropFile[0] # Update CardFileName

                        NFCCardFound = False # Reset the NFCCard variables for the next card swipe
                        NFCCardMatch = False
                        print('---> Card file detected:', CardFileName)
                        print('---> Card file read into memory')
                        print('---> Card file processed from drop folder')
                        HaveCard = 1

                    if len(ReadInput)>9:
                        CurrentCommand = CommandCode(ReadInput)
                        PriorCommand = ReadInput
                        print ("Command Code is: " + CurrentCommand + ": " +CommandLookup(CurrentCommand))
                        if CurrentCommand == CARD_CLEAN_CARD:
                            CleanStep=0
                        if CurrentCommand == CARD_WRITE_TEXT:
                            rawprintpath = '/var/log/printdata/'
                            rawfilename = rawprintpath+os.path.basename(CardFileName)+".printdata"
                            rawfile = open(rawfilename, "w")
                            rawcardoutput = ReadInput.lstrip()
                            rawfile.write(rawcardoutput)
                            rawfile.close()
                            print('---> Print data detected and exported for processing')
                            print('---> Data exported: '+rawcardoutput)
                            if (rawfilename != ""):
                                cp = subprocess.run(["python3", "/sbin/piforce/card_emulator/wmmt_card_data.py", "-m", wmmtmode, "-f", rawfilename])
                                rawfilename = ""
                                print('---> Card print data processed')

                    if ValidCommand(CurrentCommand) and len(ReadInput)>9:
                        print ("Reader Emulator: Acknowledging:  06")
                        output =b"\x06"
                        comport['ser'].write(output)
                        ReadInput=""
                        
                    if CurrentCommand == CARD_INIT and "05" in ReadInput:
                        ReadInput=""
                        output =b"\x02\x06\x10\x30\x30\x30\x03\x25"
                        comport['ser'].write(output)
                        print ("Reader Emulator: Sending Init Reply(10):  02 06 10 30 30 30 03 25 - Initializing Variables")
                        ReadInput=""
                        StepNum=0
                        CleanStep=0
                        CleanFinal=0

                    if CurrentCommand == CARD_78 and "05" in ReadInput:
                        output =b"\x02\x06\x78\x30\x30\x30\x03\x4D"
                        print ("Reader Emulator: Sending 78 Reply:  02 06 78 30 30 30 03 4D")
                        comport['ser'].write(output)
                        ReadInput=""
                        
                    if CurrentCommand == CARD_CLEAN_CARD and "05" in ReadInput:
                        if CleanStep == 3:
                            ReadInput=""
                            output =b"\x02\x06\xA0\x30\x30\x30\x03\x95"
                            print ("Reader Emulator: Sending: CARD_CLEAN_CARD(A0) Reply Step 3:  02 06 A0 30 30 30 03 95")
                            comport['ser'].write(output)
                        if CleanStep == 2:
                            ReadInput=""
                            output =b"\x02\x06\xA0\x34\x30\x30\x03\x91"
                            print ("Reader Emulator: Sending: CARD_CLEAN_CARD(A0) Reply Step 2:  02 06 A0 34 30 30 03 91")
                            comport['ser'].write(output)
                            CleanStep=3
                        if CleanStep == 1:
                            ReadInput=""
                            output =b"\x02\x06\xA0\x31\x30\x30\x03\x97"
                            print ("Reader Emulator: Sending: CARD_CLEAN_CARD(A0) Reply Step 1:  02 06 A0 31 30 33 03 97")
                            comport['ser'].write(output)
                            CleanStep=2
                        if CleanStep == 0:
                            ReadInput=""
                            output =b"\x02\x06\xA0\x30\x30\x33\x03\x96"
                            print ("Reader Emulator: Sending: CARD_CLEAN_CARD(A0) Reply Step 0:  02 06 A0 30 30 33 03 96")
                            comport['ser'].write(output)
                            CleanStep=1
                        
                    if CurrentCommand == CARD_LOAD_CARD and "05" in ReadInput:
                        if StepNum == 1:
                            output =b"\x02\x06\xB0\x31\x30\x32\x03\x86"
                            print ("Reader Emulator: Sending: CARD_LOAD_CARD Command(B0) Reply Step 1: 02 06 B0 31 30 32 03 86")
                            comport['ser'].write(output)
                            StepNum=2
                        if StepNum == 0:
                            output =b"\x02\x06\xB0\x31\x30\x30\x03\x84"
                            print ("Reader Emulator: Sending: CARD_LOAD_CARD Command(B0) Reply Step 0: 02 06 B0 31 30 30 03 84")
                            comport['ser'].write(output)
                            StepNum=1
                        ReadInput=""
                        
                    if CurrentCommand == CARD_IS_PRESENT and "05" in ReadInput:
                        output =b"\x02\x06\x40\x30\x30\x30\x03\x75"
                        print ("Reader Emulator: Sending: Card Is Present Command(40) Reply: 02 06 40 30 30 30 03 75")
                        comport['ser'].write(output)
                        ReadInput=""
                        
                    if CurrentCommand == CARD_GET_CARD_STATE and "05" in ReadInput:
                        output =b"\x02\x06\x20\x31\x30\x30\x03\x14"
                        print ("Reader Emulator: Sending: CARD_GET_CARD_STATE Command(20) Reply: 02 06 20 31 30 30 03 14")
                        comport['ser'].write(output)
                        ReadInput=""
                        
                    if CurrentCommand == CARD_7D and "05" in ReadInput:
                        output =b"\x02\x06\x7D\x31\x30\x30\x03\x49"
                        print ("Reader Emulator: Sending: CARD_7D Command(7D) Reply: 02 06 7D 31 30 30 03 49")
                        comport['ser'].write(output)
                        ReadInput=""
                        
                    if CurrentCommand == CARD_WRITE and "05" in ReadInput:
                        output =b"\x02\x06\x53\x31\x30\x30\x03\x67"
                        print ("Received new card data!")
                        CardBytes, CardFileName = CardTranslationWMMT(PriorCommand,CardFileName,wmmtmode)
                        print (CardBytes)
                        print ("Reader Emulator: Sending: CARD_WRITE Command(53) Reply: 02 06 53 31 30 30 03 67")
                        comport['ser'].write(output)
                        CardWriteFlag = True
                        ReadInput=""
                        
                    if CurrentCommand == CARD_WRITE_TEXT and "05" in ReadInput:
                        output =b"\x02\x06\x7C\x31\x30\x30\x03\x48"
                        print ("Reader Emulator: Sending: CARD_WRITE_TEXT Command(7C) Reply: 02 06 7C 31 30 30 03 48")
                        comport['ser'].write(output)
                        ReadInput=""
                        
                    if CurrentCommand == CARD_80 and "05" in ReadInput:
                        output =b"\x02\x06\x80\x30\x30\x30\x03\xB5"
                        print ("Reader Emulator: Sending: CARD_80 Command(80) Reply - CARD EJECTED: 02 06 80 30 30 30 03 B5")
                        comport['ser'].write(output)
                        PrintDataFile = "/var/www/html/cards/"+wmmtmode+"/"+os.path.basename(CardFileName)+".printdata.php"
                        WriteBackFile = open('/sbin/piforce/nfcwriteback.txt') # Check NFC writeback setting
                        NFCCardWrite = WriteBackFile.readline()
                        WriteBackFile.close()
                        if (CopyNFCphp and CardWriteFlag): # If the data has come from a new unknown NFC card - move its associated printdata php file to the correct location
                            print('---> Moving NFC Card print data file')
                            shutil.copy("/var/log/printdata/NFC_Card.printdata.php", PrintDataFile)
                            os.remove("/var/log/printdata/NFC_Card.printdata.php")
                            CopyNFCphp = False # Reset CopyNFCphp variable for next card swipe
                        if (NFCCardWrite == 'yes' and CardWriteFlag):
                            print('---> Writing card data to NFC card')
                            print('---> NFC data file:', CardFileName)
                            print('---> NFC print file:', PrintDataFile)
                            cp = subprocess.Popen(["python3","/sbin/piforce/card_emulator/nfcwrite.py", "-m", "namco", "-f", CardFileName, "-p", PrintDataFile])
                        StepNum=0
                        CardLoaded =0
                        GotNewCardData=0
                        Ejected =1
                        HaveCard = 0
                        emptydropfolder() # Empty the drop folder as card has been ejected
                        CardBytes = b"" # Reset CardBytes
                        CardFileName = autogen() # Set CardFileName to new autogen name
                        print("---> New card name generated: " + CardFileName)
                        CardWriteFlag = False
                        ReadInput=""

                    if HaveCard==0:
                        if CurrentCommand == CARD_READ and "05" in ReadInput:
                            output =b"\x02\x06\x33\x30\x30\x34\x03\x02"
                            print ("Reader Emulator: Sending: Read Command(33) Reply - No Card:  02 06 33 30 30 34 03 02")
                            comport['ser'].write(output)
                            ReadInput=""
                            
                    if HaveCard==1:
                        if "02 09 33 00 00 00 32 31 30 03 0A" in PriorCommand and CurrentCommand == CARD_READ and "05" in ReadInput:
                            output =b"\x02\x06\x33\x31\x30\x30\x03\x07"
                            print ("Reader Emulator: Sending: Read Command(33) Reply - Have Card:  02 06 33 31 30 30 03 07")
                            comport['ser'].write(output)
                            ReadInput=""
                            
                        if CurrentCommand == CARD_READ and "05" in ReadInput:
                            output = CardBytes
                            print ("Reader Emulator: Sending: Read Command(33) Reply - Have Card - Sending Card Data")
                            print (CardBytes)
                            comport['ser'].write(output)
                            ReadInput=""

                    if ReadInput:
                        print ("ERROR: Emulator is ignoring or does not know how to respond to: " + ReadInput )
                        ReadInput=""
                    
                sys.stdout.flush()
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__": main()
