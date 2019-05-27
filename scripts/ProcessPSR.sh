#!/bin/bash
dd=$1
ls -1d ${dd}* > ./list
for file in `cat ./list`
do
    cd $file
    psrname="${file##*_}"
    date=${file:0:8}
    echo Processing  $psrname $date
    bash -x /data/Commissioning/PSRMonitor/Artemis3/${psrname}_HBA_lane1_Proc.sh
    bash -x /data/Commissioning/PSRMonitor/Artemis3/${psrname}_HBA_lane2_Proc.sh
    bash -x /data/Commissioning/PSRMonitor/Artemis3/${psrname}_HBA_lane3_Proc.sh
    bash -x /data/Commissioning/PSRMonitor/Artemis3/${psrname}_HBA_lane4_Proc.sh
    echo Control Returned to ProcessPSR
    cd ../
done
