import os, collections, signal, sys, subprocess, socket
from time import sleep

if (sys.argv[1] == 'multi') or (sys.argv[1] == 'single'):
   bootfile = open('/sbin/piforce/bootfile.txt', 'w')
   bootfile.write(sys.argv[1])
   bootfile.close
   
if (sys.argv[1] == 'auto-off') or (sys.argv[1] == 'always-on'):
   powerfile = open('/sbin/piforce/powerfile.txt', 'w')
   powerfile.write(sys.argv[1])
   powerfile.close

if (sys.argv[1] == 'simple') or (sys.argv[1] == 'advanced'):
   menufile = open('/sbin/piforce/menumode.txt', 'w')
   menufile.write(sys.argv[1])
   menufile.close

if (sys.argv[1] == 'relayon') or (sys.argv[1] == 'relayoff'):
   relayfile = open('/sbin/piforce/relaymode.txt', 'w')
   relayfile.write(sys.argv[1])
   relayfile.close

if (sys.argv[1] == 'hackon') or (sys.argv[1] == 'hackoff'):
   zerofile = open('/sbin/piforce/zeromode.txt', 'w')
   zerofile.write(sys.argv[1])
   zerofile.close

if (sys.argv[1] == 'openon') or (sys.argv[1] == 'openoff'):
   openfile = open('/sbin/piforce/openmode.txt', 'w')
   openfile.write(sys.argv[1])
   openfile.close

if (sys.argv[1] == 'ffbon') or (sys.argv[1] == 'ffboff'):
   ffbfile = open('/sbin/piforce/ffbmode.txt', 'w')
   ffbfile.write(sys.argv[1])
   ffbfile.close

if (sys.argv[1] == 'soundon') or (sys.argv[1] == 'soundoff'):
   soundfile = open('/sbin/piforce/soundmode.txt', 'w')
   soundfile.write(sys.argv[1])
   soundfile.close

if (sys.argv[1] == 'navon') or (sys.argv[1] == 'navoff'):
   navfile = open('/sbin/piforce/navmode.txt', 'w')
   navfile.write(sys.argv[1])
   navfile.close

if (sys.argv[1] == 'manual') or (sys.argv[1] == 'auto'):
   emufile = open('/sbin/piforce/emumode.txt', 'w')
   emufile.write(sys.argv[1])
   emufile.close

if (sys.argv[1] == 'nfcon') or (sys.argv[1] == 'nfcoff'):
   nfcfile = open('/sbin/piforce/nfcmode.txt', 'w')
   nfcfile.write(sys.argv[1])
   nfcfile.close
   if (sys.argv[1] == 'nfcon'):
      cmd = 'sudo python3 /sbin/piforce/card_emulator/nfcread.py &'
      os.system(cmd)

if (sys.argv[1] == 'osmon') or (sys.argv[1] == 'osmoff'):
   osmfile = open('/sbin/piforce/osmmode.txt', 'w')
   osmfile.write(sys.argv[1])
   osmfile.close

if (sys.argv[1] == 'filteron') or (sys.argv[1] == 'filteroff'):
   filterfile = open('/sbin/piforce/filtermode.txt', 'w')
   filterfile.write(sys.argv[1])
   filterfile.close

if (sys.argv[1] == 'once') or (sys.argv[1] == 'replay'):
   osmperfile = open('/sbin/piforce/osmpermode.txt', 'w')
   osmperfile.write(sys.argv[1])
   osmperfile.close

if (sys.argv[1] == 'rotaryon') or (sys.argv[1] == 'rotaryoff'):
   osmperfile = open('/sbin/piforce/rotarymode.txt', 'w')
   osmperfile.write(sys.argv[1])
   osmperfile.close

if (sys.argv[1] == 'hatserialon') or (sys.argv[1] == 'hatserialoff'):
   hatfile = open('/sbin/piforce/hatserial.txt', 'w')
   hatfile.write(sys.argv[1])
   hatfile.close

if (sys.argv[1] == 'light') or (sys.argv[1] == 'dark'):
   osmtheme = open('/sbin/piforce/osmtheme.txt', 'w')
   osmtheme.write(sys.argv[1])
   osmtheme.close
   if (sys.argv[1] == 'light'):
      cmd = 'sudo cp /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin.light /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin &'
      os.system(cmd)
   if (sys.argv[1] == 'dark'):
      cmd = 'sudo cp /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin.dark /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin &'
      os.system(cmd)

if (sys.argv[1] == 'red') or (sys.argv[1] == 'green') or (sys.argv[1] == 'teal') or (sys.argv[1] == 'blue') or (sys.argv[1] == 'violet') or (sys.argv[1] == 'yellow') or (sys.argv[1] == 'nocolour'):
   colourfile = open('/sbin/piforce/lcdcolour.txt', 'w')
   colourfile.write(sys.argv[1])
   colourfile.close

if (sys.argv[1] == 'serveron') or (sys.argv[1] == 'serveroff'):
   if (sys.argv[1] == 'serveron'):
      bootfile = open('/sbin/piforce/bootfile.txt', 'w')
      bootfile.write('single')
      bootfile.close
   if (sys.argv[1] == 'serveroff'):
      bootfile = open('/sbin/piforce/bootfile.txt', 'w')
      bootfile.write('multi')
      bootfile.close
   serverfile = open('/sbin/piforce/servermode.txt', 'w')
   serverfile.write(sys.argv[1])
   serverfile.close

if (sys.argv[1] == 'LCD16'):
   bashCommand1 = 'sudo echo -n LCD16 | tee /sbin/piforce/lcdmode.txt'
   os.system(bashCommand1)
   bashCommand2 = 'sudo systemctl enable lcd-piforce'
   os.system(bashCommand2)
   bashCommand3 = 'sudo cp /boot/config.txt.lcd16 /boot/config.txt'
   os.system(bashCommand3)
   sleep(5)
   shutdwn = 'sudo shutdown now'
   os.system(shutdwn)

if (sys.argv[1] == 'LCD35'):
   bashCommand1 = 'sudo echo -n LCD35 | tee /sbin/piforce/lcdmode.txt'
   os.system(bashCommand1)
   bashCommand2 = 'sudo systemctl disable lcd-piforce'
   os.system(bashCommand2)
   bashCommand3 = 'sudo cp /boot/config.txt.lcd35 /boot/config.txt'
   os.system(bashCommand3)
   sleep(5)
   shutdwn = 'sudo shutdown now'
   os.system(shutdwn)