import os

zipcommand = 'tar -cvzf wipilogs.tar.gz /var/log'
os.system(zipcommand)
os.rename('./wipilogs.tar.gz', '/var/www/logs/wipilogs.tar.gz')