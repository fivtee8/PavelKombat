./stopserver.sh
fuser database.db 2>/dev/null | xargs kill -9 > /dev/null 2> /dev/null
./startserver.sh
python3 tests/clear_db.py
while ! nc -z localhost 4040; do
  sleep .2 # wait Ngrok to be available
done
python3 -m unittest discover tests --verbose 2> logs/test_out.txt
./stopserver.sh
tail -4 logs/test_out.txt
echo The full log can be seen at logs/test_out.txt
echo Testing complete. The server has been killed - please relaunch the server if needed.