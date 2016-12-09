#! /bin/bash 

procname="python main.py"
filename=""
for item in `ls *.log | grep -v QRCODE`
do
    filename=${item}
done

echo    -en "Log filename : ${filename}\n"

lastline=0
currtext=`cat ${filename}`
currline=`echo -en "${currtext}" | awk 'END {print NR}'`
lastline=`expr ${currline} - 100`
if [ ${lastline} -lt 0 ]
then
    lastline=0
fi

while true
do
    datetext=`date`
    pid=`ps aux | grep "${procname}" | grep -v grep | awk '{print $2}'`
    proctext=`top -b -n 1 -p ${pid} | head -n 8 | tail -n 1 | awk '{print " "$12" TIME:"$11" CPU:"$9" MEM:"$10}'`
    echotext="${datetext}${proctext}"
    echo    -en "\r\033[47;30;1m${echotext}\033[K\033[0m"

    currtext=`cat ${filename}`
    currline=`echo -en "${currtext}" | awk 'END {print NR}'`
    incrline=`expr ${currline} - ${lastline}`
    lastline=${currline}

    if [ ${incrline} -gt 0 ]
    then
        echo    -en "\n"
        echotext=`echo "${currtext}" | tail -n ${incrline}`
        echo    "${echotext}"
    fi

    sleep   1

done
