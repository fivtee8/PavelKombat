#!/bin/bash

DBPID=$(ps aux | grep '[d]bmanagaer.py' | awk '{print $2}')
BOTPID=$(ps aux | grep '[b]ot.py' | awk '{print $2}')
NGROKPID=$(ps aux | grep '[n]grok' | awk '{print $2}')

kill $DBPID 2> /dev/null
kill $BOTPID 2> /dev/null
kill $NGROKPID 2> /dev/null