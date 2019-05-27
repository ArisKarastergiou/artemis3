#!/bin/bash
dd=$1
ls -1d ${dd}* > ./list
for file in `cat ./list`
do
    cd $file
    psrname="${file##*_}"
    echo Processing  $psrname
    if [ ! -d /oxford_data2/PSRMonitor/data/$psrname ]; then
	mkdir /oxford_data2/PSRMonitor/data/$psrname
    fi
    cp *.ar /oxford_data2/PSRMonitor/data/$psrname
    echo Control Returned to ProcessPSR
    cd ../
done
