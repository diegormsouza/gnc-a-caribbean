#!/bin/bash

#################################################################
# FAZZT PROFESSIONAL CLIENT INSTALLATION SCRIPT
#################################################################

clear

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

chkconfig iptables off
chkconfig ip6tables off

#################################################################
# MOFIDY THE SELINUX AND REBOOT
#################################################################

echo "Modifying the Selinux"
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
echo "Selinux Modificado -----------------"
sed -i 's/rhgb quiet/rhgb quiet selinux=0/g' /boot/grub/grub.conf

#################################################################
# PREPARE THE HTTPD FOR THE FAZZT CLIENT
#################################################################

yum install httpd.x86_64 httpd-devel.x86_64 -y
service httpd start
chkconfig --level 345 httpd on
/etc/init.d/httpd start

#################################################################
# INSTALL THE REPOSITORIES
#################################################################

echo "Adding repositories"
rpm -Uvh http://www.elrepo.org/elrepo-release-6-6.el6.elrepo.noarch.rpm
rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
rpm -ivh http://fedora.mirrors.pair.com/epel/6/i386/epel-release-6-8.noarch.rpm
echo "Repositories added"

#################################################################
# INSTALL THE POSTGRESQL 9.5
#################################################################

echo "Install the PostgreSQL 9.5"
yum install https://download.postgresql.org/pub/repos/yum/9.5/redhat/rhel-6-x86_64/pgdg-centos95-9.5-2.noarch.rpm -y
yum install postgresql95-server postgresql95 -y
yum install php-pgsql -y
service postgresql-9.5 initdb
service postgresql-9.5 start
chkconfig postgresql-9.5 on
service postgresql-9.5 restart

#################################################################
# EDIT THE POSTGRESQL 9.5 CONFIGURATION
# DO NOT CHANGE THE SPACES IN THE SED COMMAND, THEY ARE IMPORTANT
#################################################################

echo "   Changing the postgresql configuration file"
sed -i 's/#listen_addresses/listen_addresses/' /var/lib/pgsql/9.5/data/postgresql.conf
sed -i 's/localhost/*/' /var/lib/pgsql/9.5/data/postgresql.conf
sed -i 's/#port/port/' /var/lib/pgsql/9.5/data/postgresql.conf
sed -i 's/#autovacuum = on/autovacuum = off/' /var/lib/pgsql/9.5/data/postgresql.conf
echo "Postgresql configuration changed---------------"

#################################################################
# EDIT THE POSTGRESQL 9.5 CONFIGURATION
# DO NOT CHANGE THE SPACES IN THE SED COMMAND, THEY ARE IMPORTANT
#################################################################

echo "Change the pg_hba configuration file"
sed -i 's/    peer/    trust/' /var/lib/pgsql/9.5/data/pg_hba.conf
sed -i 's/32            ident/32            trust/g' /var/lib/pgsql/9.5/data/pg_hba.conf
sed -i 's/128                 ident/128                 trust/' /var/lib/pgsql/9.5/data/pg_hba.conf
sed -i '85i\host    all        all         0.0.0.0/0        trust' /var/lib/pgsql/9.5/data/pg_hba.conf
echo "Pg file changed----------------------"
echo "Changing the memory limits"
sed -i '49i\fazzt            soft    nofile          4096' /etc/security/limits.conf
sed -i '50i\fazzt            hard    nofile          4096' /etc/security/limits.conf
echo "Limit Modificado-------------------"
service postgresql-9.5 restart
sudo -u postgres createuser fazzt
sudo -u postgres createdb fazzt

#################################################################
# KENCAST FAZZT INSTALLATION
#################################################################

echo "####################################################"
echo "# Installing the KenCast Fazzt Professional Client #"
echo "####################################################"
cp Fazzt-Professional* /usr/local
cp PC17* /usr/local
cd /usr/local
yum --nogpgcheck install Fazzt-Professional-Client-*.rpm -y
lic=`ls PC17*`
cp /usr/share/Fazzt/bin/fconf /usr/bin
fconf set license $lic
/etc/init.d/fazzt checkdb
mkdir /data
mkdir /data/fazzt
chmod 777 -R /data/fazzt
/sbin/chkconfig --level 345 fazzt on
service fazzt restart
service restart httpd
service fazzt restartdb
echo "##########################################"
echo "#          Fazzt installed               #"
echo "# Open Firefox and access the following: #"
echo "#     http://127.0.0.1:4039/admin/       #"
echo "##########################################"
reboot
