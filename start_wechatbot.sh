#! /bin/bash 

DIR=log
LOG=`date +%Y%m%d%H%M%S`.log

mkdir -p ${DIR}

nohup   python  main.py "{ \"EnableInteracting\" : false }" 1> ${DIR}/QRCODE${LOG} 2> ${DIR}/${LOG} &

sleep 1
cat ${DIR}/QRCODE${LOG}

