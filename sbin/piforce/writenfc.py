import sys

nfcfile = open('/var/log/nfcfile', 'w')
nfcfile.write(sys.argv[1])
nfcfile.close
