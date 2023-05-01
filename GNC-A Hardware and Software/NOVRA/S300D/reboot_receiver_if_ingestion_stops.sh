#!/bin/bash

#################################################################
# SCRIPT TO REBOOT THE S300D RECEIVER IF THE INGESTION STOPS
# O.S.: Tested on CentOS 6.9
# Shared by: Demilson Quintão (PY2UEP)
#################################################################

# Location and file to be monitored
# The Heartbeat.txt file is updated every 5 minutes - 300 seconds
# Change /data/fazzt to your GNC-A ingestion dir
file_monitor="/data/fazzt/Heartbeat.txt"

# Calculates the file "age" in seconds
age=$(echo "$(($(date +%s) - $(date -r "$file_monitor" +%s)))")

# If it's too old (greater than 400 seconds), write it to watchdog.log and
# restart the receiver.
if [[ "$age" -gt 400 ]]; then
  # Change /dados/web to the desired location
  echo "Age:  $idade . Reboot the receiver @ $(date)"  >> /dados/web/watchdog.log
  cmcs -ip 192.168.0.11 -pw "Novra-S2" -reboot
fi