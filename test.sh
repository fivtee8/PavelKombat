./stopserver.sh
python3 tests/clear_db.py
fuser database.db 2>/dev/null | xargs kill -9
./startserver.sh
curl http://127.0.0.1:5005/ > /dev/null 2> /dev/null
python3 -m unittest discover tests --verbose 2> logs/test_out.txt
./stopserver.sh
tail -4 logs/test_out.txt
echo The full log can be seen at logs/test_out.txt
echo Testing complete. The server has been killed - please relaunch the server if needed.