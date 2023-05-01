#!/bin/bash

#################################################################
# FAZZT PROFESSIONAL CLIENT INSTALLATION SCRIPT
# Version: Fazzt-Professional-Client-rhel7-10.0.0.1-1.x86_64.rpm
# O.S.: Tested on CentOS 7.9
# Date: February 13 2023
# Tested by: Diego Souza
#################################################################

clear

#################################################################
#Check to see if the script is being run as root
#################################################################

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "This script is required to be run as root"
    exit
fi

#################################################################
# ADD LINES TO THE SYSCTL.CONF FILE
#################################################################

echo "Adding lines to Sysctl"
echo "net.ipv4.conf.all.rp_filter = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.rp_filter = 0" >> /etc/sysctl.conf
echo "kernel.printk = 3 4 1 3" >> /etc/sysctl.conf
echo "net.ipv4.ipfrag_max_dist = 0" >> /etc/sysctl.conf
echo "Lines added"

#################################################################
# SHUT DOWN THE FIREWALL RULES
#################################################################

systemctl stop firewalld
systemctl disable firewalld

#################################################################
# MOFIDY THE SELINUX AND REBOOT
#################################################################

echo "Modifying the Selinux"
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
echo "Selinux Modified -----------------"
sed -i 's/rhgb quiet/rhgb quiet selinux=0/g' /etc/default/grub

#################################################################
# PREPARE THE HTTPD FOR THE FAZZT CLIENT
#################################################################

yum install httpd.x86_64 httpd-devel.x86_64 -y
systemctl enable httpd
systemctl start httpd

#################################################################
# INSTALL POSTGRESQL
#################################################################

echo "Install PostgreSQL"
yum install -y postgresql postgresql-server postgresql-devel
yum install -y php-pgsql
postgresql-setup initdb
systemctl enable postgresql
systemctl start postgresql

#################################################################
# EDIT THE POSTGRESQL CONFIGURATION
# DO NOT CHANGE THE SPACES IN THE SED COMMAND, THEY ARE IMPORTANT
#################################################################

echo "   Changing the postgresql configuration file"
sed -i 's/#listen_addresses/listen_addresses/' /var/lib/pgsql/data/postgresql.conf
sed -i 's/localhost/*/' /var/lib/pgsql/data/postgresql.conf
sed -i 's/#port/port/' /var/lib/pgsql/data/postgresql.conf
sed -i 's/#autovacuum = on/autovacuum = off/' /var/lib/pgsql/data/postgresql.conf
echo "Postgresql configuration changed---------------"

#################################################################
# EDIT THE POSTGRESQL CONFIGURATION
# DO NOT CHANGE THE SPACES IN THE SED COMMAND, THEY ARE IMPORTANT
#################################################################

echo "Change the pg_hba configuration file"
sed -i 's/    peer/    trust/' /var/lib/pgsql/data/pg_hba.conf
sed -i 's/32            ident/32            trust/g' /var/lib/pgsql/data/pg_hba.conf
sed -i 's/128                 ident/128                 trust/' /var/lib/pgsql/data/pg_hba.conf
sed -i '85i\host    all        	all         	0.0.0.0/0        	trust' /var/lib/pgsql/data/pg_hba.conf
echo "Pg file changed----------------------"
echo "Changing the memory limits"
sed -i '49i\fazzt            soft    nofile          4096' /etc/security/limits.conf
sed -i '50i\fazzt            hard    nofile          4096' /etc/security/limits.conf
echo "Limit Modified-------------------"
systemctl restart postgresql
sudo -u postgres createuser fazzt
sudo -u postgres createdb fazzt

#################################################################
# KENCAST FAZZT INSTALLATION
#################################################################

echo "####################################################"
echo "# Installing the KenCast Fazzt Professional Client #"
echo "####################################################"

if [ -e Fazzt-Professional-Client-rhel7-10.0.0.1-1.x86_64.rpm ]; then
    yum --nogpgcheck install -y Fazzt-Professional-Client-rhel7-10.0.0.1-1.x86_64.rpm
    cp /usr/share/Fazzt/bin/fconf /usr/bin
else
    echo "WARNING: Missing Fazzt-Professional-Client-rhel7-10.0.0.1-1.x86_64.rpm"
fi
if [ ! -e  PC17* ]; then
    echo "No Fazzt Client License file, do the followings after license file is obtained"
    echo "Run fconf set license <License File>"
    echo "Run /etc/init.d/fazzt checkdb"
else
    # loads license
    lic=`ls PC17*`
    fconf set license $lic
    systemctl enable fazzt
fi

#################################################################
# INGESTION DIRECTORY
#################################################################

# In this example, the ingestion directory is set to 
# /home/data/fazzt
# But this is not mandatory. Insert the dir of your preference.
# Also, this can be done manually after the installation.

echo ""
echo "Creating the ingestion directory"
echo ""

if [ ! -e /home/data/fazzt ]; then
    mkdir -p /home/data/fazzt
    chmod 777 -R /home/data/fazzt
fi

#################################################################
# INSTALLATION FINISHED
#################################################################

echo "##########################################"
echo "#          FAZZT installed               #"
echo "# Open Firefox and access the following: #"
echo "#     http://127.0.0.1:4039/admin/       #"
echo "##########################################"

# Execute the following commands after the installation, in sequence:

# systemctl restart httpd

# /sbin/restorecon -v /usr/lib64/httpd/modules/mod_fsp.so
# ausearch -c 'httpd' --raw | audit2allow -M my-httpd
# semodule -i my-httpd.pp

# systemctl start fazzt
# systemctl restart httpd
