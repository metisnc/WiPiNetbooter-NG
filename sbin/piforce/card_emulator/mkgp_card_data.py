#!/usr/bin/env python3
import struct
import codecs
import sys
import os
import random
import shutil
import csv
import linecache
import argparse

def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help='Mode of MKGP card emulator. Example: -m mkgp or -m mkgp2')
parser.add_argument('-f', '--file', help='Raw print data file path.')
args = parser.parse_args()
mkgpmode = args.mode
rawprintfile = args.file

# Set up variables and paths

path = '/var/www/html/cards/'+mkgpmode+'/'
phppath = path+os.path.basename(rawprintfile)+".php"

# Set up constants to make code easier to read

controlchars = [b'\x11',b'\x14',b'\x1B\x73',b'\x1B\x67']
decreasefont = b'\x11'
increasefont = b'\x14'
updatefont = b'\x1B\x73'
printicon = b'\x1B\x67'

# Open the print packet and read in everything

with open(rawprintfile) as f:
    printpacket = f.read()

# Create printdata bytearray for data comparison

printdatalength = int((len(printpacket)-2)/3+1)
printdata = b''
printdatalist = []
for i in range(printdatalength):
    printdatapart = int("0x" + printpacket[i*3:i*3+2],0)
    printdatalist.append(printdatapart)
printdata = bytearray(printdatalist)

# Read in past the 7C command header

packetlen = printdata[:printdata.index(b'\x7C\x00\x00\x00')]

# Check and record packet length, remove one as zero numbered

if len(packetlen) > 1:
    packetlen = packetlen[len(packetlen)-1:]
packetlen = packetlen[0]

print('Packet length: '+str(packetlen))

# Trim the printdata removing header and EOM marker

trimmed_bytes_stream = printdata[printdata.index(b'\x7C\x00\x00\x00')+6:printdata.index(b'\x03')]

# Find which line this packet will start printing on then remove the line identifier

linestart = trimmed_bytes_stream[0]

# Detect if first line of new card print on existing card, if so reset all card values apart from card name

if (mkgpmode == 'mkgp2' and os.path.exists(phppath) and linestart == 1 and packetlen == 25) or (mkgpmode == 'mkgp' and os.path.exists(phppath) and linestart == 1 and packetlen == 32):
    print('New data being printed, blanking existing card data')
    with open(phppath, "r+") as fi:
        data = fi.readlines()
        data[1] = '$l1="";\n'
        data[2] = '$l2="";\n'
        data[3] = '$l3="";\n'
        data[4] = '$l4="";\n'
        data[5] = '$l5="";\n'
        data[6] = '$l6="";\n'
        data[7] = '$l7="";\n'
        data[8] = '$l8="";\n'
        data[9] = '$l9="";\n'
        data[10] = '$l10="";\n'
        data[12] = '$ia="";\n'
        fi.truncate(0)
        fi.seek(0, 0)
        fi.writelines(data)

# Check for existing printdata file, if none found create a blank one

if (not os.path.exists(phppath)):
    cardimage = random.choice(os.listdir("/var/www/html/cardimages/"+mkgpmode))
    with open("card_output","w") as fi:
        fi.write('<?php'+'\n')
        fi.write('$l1="";\n')
        fi.write('$l2="";\n')
        fi.write('$l3="";\n')
        fi.write('$l4="";\n')
        fi.write('$l5="";\n')
        fi.write('$l6="";\n')
        fi.write('$l7="";\n')
        fi.write('$l8="";\n')
        fi.write('$l9="";\n')
        fi.write('$l10="";\n')
        fi.write('$crd="'+cardimage+'";\n')
        fi.write('$ia="";\n')
        fi.write('?>'+'\n')
    shutil.move("./card_output", phppath)

print ("Line start: " + str(linestart))
trimmed_bytes_stream = trimmed_bytes_stream[1:]
trimmed_bytes_stream = trimmed_bytes_stream[:len(trimmed_bytes_stream)]

# Split the printlist into lines for processing catching edge cases first

replacement = trimmed_bytes_stream.replace(b'\x1B\x67\x0D',b'\x1B\x67\xFF')
replacement2 = replacement.replace(b'\x1B\x67\x11',b'\x1B\x67\xFE')
replacement3 = replacement2.replace(b'\x1B\x67\x14',b'\x1B\x67\xFD')
printlist = replacement3.split(b'\x0D')

# Prepare to start scanning for special characters, these will be removed and their type and position recorded

linecount = 1
currentline = 0
charposarray = []
linesplit = []
charconv = ''

# Process each line in turn

for line in printlist:
    linepart = line
    controlcharscount = 0
    offset = 0

# Process each special character in turn, per line

    for char in controlchars:
        controlcharscount += line.count(char)

# If a special character has been found, begin processing

        if (line.count(char) > 0):
            prevpos = 0
            pos = 0

# For each character record it's associated parameter and position and compare with any found previously

            for _ in range(0,line.count(char)):
                param1 = 0
                param2 = 0
                parametercount = 0
                if char == updatefont:
                    parametercount = 2
                if char == printicon:
                    parametercount = 1
                pos = line.find(char, prevpos)
                print(str(char)+" found at position "+str(pos+offset))
                prevpos = pos
                if parametercount > 0:
                    linepart = line[pos+2:]
                    parameter1 = linepart[:1]
                    param1 = ' '.join('{:02X}'.format(byte) for byte in parameter1)
                    print ("Parameter 1 is: "+ param1)
                    if parametercount > 1:
                        linepart = line[pos+4:]
                        parameter2 = linepart[:1]
                        param2 = ' '.join('{:02X}'.format(byte) for byte in parameter2)
                        print ("Parameter 2 is: "+ param2)
                prevpos = pos
                charconv = ''.join('{:02X}'.format(byte) for byte in char)

# If the character is an icon, add to array with position and icon reference, update the offset by 2 to account for absolute position on the card

                if charconv == '1B67':
                    charposarray.append([linestart+(linecount-1),pos+offset,param1])
                    charposarray.sort()
                    offset -= 2
                linepart = line

# Now the clever bit, create a new line using the bytes before and after the character found, if at the start of a line it can be simply removed
# The \x1F character is a custom character in the font to correct spacing, the same width as the icons

                if pos > 0:
                    offset = offset+len(char)+parametercount
                    lastpart=linepart[pos+len(char)+parametercount:]
                    print("Lastpart: "+str(lastpart))
                    if charconv == '1B67':
                        firstpart=linepart[:pos]+b'\x1F'
                    else:
                        firstpart=linepart[:pos]
                    print("Firstpart: "+str(firstpart))
                    linesplit.append(firstpart)
                    linepart=linepart[pos:]
                else:
                    offset = offset+len(char)+parametercount
                    print ("The special case happens at the beginning of the line section - removing it")
                    linepart=linepart[len(char):]
                line = firstpart+lastpart
                print(' '.join('{:02X}'.format(byte) for byte in line))
    
# Decode the remaining text and prepare data to be written to the printdata php file
    
    print(line.decode('shift-jis'))
    print ("Control characters found in line "+str(linecount)+": " + str(controlcharscount))
    phpfile = open(phppath)
    phplines = phpfile.readlines()
    phpdata = ''.join(phplines[linestart+currentline].split('"')[1::2])+str(line.decode('shift-jis'))
    print(phpdata)
    replace_line(phppath, linestart+currentline, '$l'+str(linestart+currentline)+'="'+phpdata+'";\n')
    linecount += 1
    currentline += 1

# If the cancel size character is detected, add 1 to the currentline variable due to the large font just printed

    if charconv == '14':
        currentline += 1

# Create php array for icons to be printed

if len(charposarray) > 0:

    iconarray = '"'
    iconcount = 0
    print(charposarray)
    for charpos in charposarray:
        iconarray += ''.join(str(i) for i in charpos)
        iconcount += 1
        if iconcount < len(charposarray):
            iconarray += ','
    iconarray += '"'

    print(iconarray)
    iconline = linecache.getline(phppath, 13)

# Check if there is already icon data present, if so append it

    if iconline == '$ia="";\n':
        replace_line(phppath, 12, '$ia='+iconarray+';\n')
    else:
        print('Icons present')
        appendarray = iconline[:-3]+','+iconarray[1:]
        print(iconline)
        print(appendarray)
        replace_line(phppath, 12, appendarray+';\n')
