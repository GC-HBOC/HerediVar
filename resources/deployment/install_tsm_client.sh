wget https://public.dhe.ibm.com/storage/tivoli-storage-management/maintenance/client/v8r1/Linux/LinuxX86_DEB/BA/v8121/8.1.21.0-TIV-TSMBAC-LinuxX86_DEB.tar

tar -xvf 8.1.4.1-TIV-TSMBAC-LinuxX86_DEB.tar

sudo dpkg -i gskcrypt64-8.0.50.86.linux.x86_64.deb
sudo dpkg -i gskssl64-8.0.50.86.linux.x86_64.deb
sudo dpkg -i tivsm-api64.amd64.deb
sudo dpkg -i tivsm-ba.amd64.deb
sudo dpkg -i tivsm-apicit.amd64.deb
sudo dpkg -i tivsm-bacit.amd64.deb


touch /opt/tivoli/tsm/client/ba/bin/dsm.sys
# content:
# SERVERNAME <servername>
# TCPSERVERADDRESS <serveradress>
# PASSWORDACCESS GENERATE
# NODENAME <nodename>
# TCPCLIENTPORT <tcpclientport>
# TCPPORT <tcpport>
# WEBPorts <webports>
# SCHEDMODE PROMPTED
# MANAGEDSERVICES WEBCLIENT SCHEDULE
# Errorlogname /var/log/dsmerror.log
# Schedlogname /var/log/dsmsched.log
# ERRORLOGRETENTION 7 S
# SCHEDLOGRETENTION 7 S


touch /opt/tivoli/tsm/client/ba/bin/dsm.opt
# content:
# SErvername <servername>
# DOMAIN ALL-LOCAL


# check connection:
dsmc
# enter user_id & password
# enter "quit" to leave dsmc console
# password is then saved


systemctl enable dsmcad.service
systemctl start dsmcad.service


# check automatic backup here: /var/log/dsmsched.log