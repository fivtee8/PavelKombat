#!/bin/bash

nohup python3 dbmanager.py > logs/dbout.txt 2>&1 &
nohup python3 bot.py > logs/botout.txt 2>&1 &
ngrok http 5005 --response-header-add="Access-Control-Allow-Origin: *" --response-header-add="Access-Control-Allow-Headers: *" --domain fond-pangolin-lately.ngrok-free.app > /dev/null 2>&1 &
echo Started server!