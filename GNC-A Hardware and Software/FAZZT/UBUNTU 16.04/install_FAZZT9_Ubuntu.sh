#!/bin/bash

########################################################################
# FAZZT PROFESSIONAL CLIENT v 9.0 for Ubuntu 16.04 - Installation Script
########################################################################

clear

# 1 Change the apport to suppress errors
sed -i 's/enabled=1/enabled=0/g' /etc/default/apport

# 2 Install Apache 2 
apt-get install apache2 -y

# 3 Install PostgreSQL 
apt-get install postgresql -y
sudo -u postgres createdb fazzt
sudo -u postgres createuser fazzt

# 4 Install Kencast FAZZT v 9.0 
chmod +x Fazzt-Professional-Client*.sh
./Fazzt-Professional-Client*.sh
cp PC*.kcl /opt/Fazzt/license/
chmod 444 /opt/Fazzt/license/PC*.kcl
/etc/init.d/fazzt start

# 5 Create a folder for the ingestion
mkdir /data
mkdir /data/fazzt
chmod 777 -R /data/fazzt

# 6 Create the FAZZT Start Script
echo "#!/bin/bash" >> /usr/bin/fazzt9start.sh
echo "clear" >> /usr/bin/fazzt9start.sh
echo "# Start Fazzt 9 " >> /usr/bin/fazzt9start.sh
echo "clear" >> /usr/bin/fazzt9start.sh
echo "service fazzt start" >> /usr/bin/fazzt9start.sh
echo "echo" >> /usr/bin/fazzt9start.sh
echo "echo \"=== Fazzt Start Ok...===\"" >> /usr/bin/fazzt9start.sh
echo "echo" >> /usr/bin/fazzt9start.sh
echo "# Show pid Fazzt Started" >> /usr/bin/fazzt9start.sh
echo "ps -ef | grep /opt/Fazzt/bin/fazzt" >> /usr/bin/fazzt9start.sh
echo "echo" >> /usr/bin/fazzt9start.sh

# 7 Create the FAZZT Stop Script
echo "#!/bin/bash" >> /usr/bin/fazzt9stop.sh
echo "clear" >> /usr/bin/fazzt9stop.sh
echo "# kill Fazzt" >> /usr/bin/fazzt9stop.sh
echo "f=\`pidof fazzt\`" >> /usr/bin/fazzt9stop.sh
echo "kill -9" "$""f" >> /usr/bin/fazzt9stop.sh
echo "echo" >> /usr/bin/fazzt9stop.sh
echo "echo" >> /usr/bin/fazzt9stop.sh
echo "echo ""\"=== Fazzt Stop Ok... ===\"" >> /usr/bin/fazzt9stop.sh
echo "echo" >> /usr/bin/fazzt9stop.sh

# 8 Create the FAZZT Restart Script
echo "#!/bin/bash" >> /usr/bin/fazzt9restart.sh
echo "clear" >> /usr/bin/fazzt9restart.sh
echo "# kill Fazzt" >> /usr/bin/fazzt9restart.sh
echo "##############" >> /usr/bin/fazzt9restart.sh
echo "f=\`pidof fazzt\`" >> /usr/bin/fazzt9restart.sh
echo "kill -9" "$""f" >> /usr/bin/fazzt9restart.sh
echo "# Restart Fazzt" >> /usr/bin/fazzt9restart.sh
echo "##############" >> /usr/bin/fazzt9restart.sh
echo "service fazzt start" >> /usr/bin/fazzt9restart.sh
echo "clear" >> /usr/bin/fazzt9restart.sh
echo "echo ""\"=== Fazzt Stop Ok... ===\"" >> /usr/bin/fazzt9restart.sh 
echo "echo" >> /usr/bin/fazzt9restart.sh
echo "echo \"=== Fazzt Restart Ok...===\"" >> /usr/bin/fazzt9restart.sh
echo "ps -ef | grep /opt/Fazzt/bin/fazzt" >> /usr/bin/fazzt9restart.sh
echo "echo" >> /usr/bin/fazzt9restart.sh

# 9 Create the Fazzt9 Script
echo "#!/bin/bash" >> /usr/bin/fazzt9
echo "clear" >> /usr/bin/fazzt9
echo "start() {" >> /usr/bin/fazzt9
echo " sh /usr/bin/fazzt9start.sh" >> /usr/bin/fazzt9
echo "}" >> /usr/bin/fazzt9
echo "" >> /usr/bin/fazzt9
echo "stop() {" >> /usr/bin/fazzt9
echo " sh /usr/bin/fazzt9stop.sh" >> /usr/bin/fazzt9
echo "}" >> /usr/bin/fazzt9
echo "" >> /usr/bin/fazzt9
echo "restart() {" >> /usr/bin/fazzt9
echo " sh /usr/bin/fazzt9restart.sh" >> /usr/bin/fazzt9
echo "}" >> /usr/bin/fazzt9
echo "case ""$""1 ""in" >> /usr/bin/fazzt9
echo "  start|stop|restart) ""$""1;;" >> /usr/bin/fazzt9
echo "*) echo" "\"Run"" as"" $""0"" <start|stop|restart>\"""; exit 1;;" >> /usr/bin/fazzt9
echo "esac" >> /usr/bin/fazzt9
chmod +x /usr/bin/fazzt*
echo
echo "##########################################"
echo "#          Fazzt installed               #"
echo "#   Firefox will open automatically at:  #"
echo "#     http://127.0.0.1:4039/admin/       #"
echo "##########################################"
echo

firefox http://127.0.0.1:4039/admin/ &

