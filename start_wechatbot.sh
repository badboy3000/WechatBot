#! /bin/bash 

LOG=`date +%Y%m%d%H%M%S`.log
nohup   python  main.py "{ \"EnableInteracting\" : false }" 1> QRCODE${LOG} 2> ${LOG} &

sleep 1
cat QRCODE${LOG}

