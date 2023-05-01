#!/bin/bash

#################################################################
# SCRIPT TO STORE THE SIGNAL TO NOISE RATIO IN A LOG FILE 
# O.S.: Tested on CentOS 6.9
# Shared by: Demilson Quintão (PY2UEP)
#################################################################

while true;
 do STATION='MY-GNC-A-STATION';
   SAT=( $( cmcs -ip 192.168.0.11 -pw "Novra-S2" -shsat | tr -d '\n' | tr -s ' ' | sed -e 's/\t/ /g ; s/\/Second// ; s/dB//' ) );
   echo $(date +%Y" "%j" "%T" " | tr -d '\n') ${SAT[34]} ${SAT[39]} ${SAT[42]} >> $STATION".log" ;
   sleep  5;
 done
 
# Procedure:
# 1. Create a script file ( example: $ nano antenna.sh )
# 2. Copy and paste the script above, changing the station name, IP and password as appropriate. Save the file with Ctrl+X
# 3. Change the file permission ( example: $ chmod 755 antenna.sh )
# 4. Execute the script on the background: ( example: $ ./antenna.sh & )
# 5. Verify if the data is being recorded (use Ctrl+C to get out of the tail command) (example: $ tail -f MY-GNC-A-STATION.log )

# To interrupt the script, check the process ID and kill it:
# EXAMPLE:
# $ ps -ef | grep antenna.sh
# web 5182 5142 0 Aug28 pts/0 00:00:10 /bin/bash ./antenna.sh
# web 12685 24304 0 10:36 pts/8 00:00:00 grep antenna.sh
# $ kill 5182

# Check if the process was finished:
# EXAMPLE
# $ ps -ef | grep antenna.sh
# web 12685 24304 0 10:36 pts/8 00:00:00 grep antenna.sh
# $

# 