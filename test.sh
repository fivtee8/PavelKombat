./stopserver.sh
fuser database.db 2>/dev/null | xargs kill -9
nohup python3 dbmanager.py > /dev/null 2> /dev/null &
python3 -m unittest discover tests --verbose 2> logs/test_out.txt
PID=$(ps aux | grep '[d]bmanagaer.py' | awk '{print $2}')
kill $PID 2> /dev/null
tail -5 logs/test_out.txt
echo The full log can be seen at logs/test_out.txt
echo Testing complete. The server has been killed - please relaunch the server if needed.