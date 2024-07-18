#!/bin/bash

python3 dbmanager.py > /dev/null &
ngrok http 5005 --response-header-add="Access-Control-Allow-Origin: *" --response-header-add="Access-Control-Allow-Headers: *" --domain fond-pangolin-lately.ngrok-free.app > /dev/null
