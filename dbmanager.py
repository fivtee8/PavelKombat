import os
import aiosqlite
import uvicorn
import json
import dotenv
from asgiref.wsgi import WsgiToAsgi

import flask
from flask import Flask, request

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)


@app.before_request
async def before_request():
    global cur
    con = await aiosqlite.connect('database.db')
    cur = await con.cursor()
    dotenv.load_dotenv()


@app.route('/')
async def hello():
    return {'message': 'You have reached the server! Everything is functional.'}


@app.route('/request/banned/<tgid>')
async def check_banned(tgid=0):
    res = await (await cur.execute(f'SELECT banned FROM Players WHERE tgid = {tgid}')).fetchone()

    if res is None:
        return {'banned': '0'}

    if res[0] == '0':
        return {'banned': '0'}

    return {'banned': '1'}


@app.route('/request/starttime/')
async def start_time():
    res = await cur.execute('SELECT Value FROM Params WHERE Key="starttime"')
    res = {'time': str((await res.fetchone())[0])}

    return res


@app.route('/request/clickcount/<playerid>')
async def return_click(playerid=0):
    res = await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {playerid}')).fetchone()

    if res is None:
        res = '0'
    else:
        res = str(res[0])

    res = {'clicks': res}

    return res

"""
# Old registration!
@app.route('/put/register/<tgid>/<usr>/<name>/<last>')
def register(tgid='', usr='', name='', last=''):
    try:
        values_str = str(tgid) + ', "' +  '", "'.join([usr, name, last, "0"]) + '"'
        # print("Executing: " + f'INSERT INTO Players (tgid, username, firstname, lastname) VALUES ({values_str})')
        cur.execute(f'INSERT INTO Players (tgid, username, firstname, lastname, banned) VALUES ({values_str})')
        cur.execute(f'UPDATE PLayers SET clicks = 0 WHERE tgid = {tgid}')
        cur.execute('COMMIT')
    except sqlite3.OperationalError:
        return {'message': 'operationalError!'}

    except Exception:
        return {'message': 'Other exception...'}

    return {'message': 'success'}
"""


@app.route('/botapi/check_registered/<tgid>')
async def check_registered(tgid=0):
    res = await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}')).fetchone()

    if res is None:
        return {'registered': '0'}
    else:
        return {'registered': '1'}


@app.route('/botapi/register_user/<tgid>', methods=['GET'])
async def register(tgid=0):
    params = request.json

    name = params['name']
    last = params['last']
    usr = params['usr']

    try:
        values_str = str(tgid) + ', "' + '", "'.join([usr, name, last, "0"]) + '"'
        # print("Executing: " + f'INSERT INTO Players (tgid, username, firstname, lastname) VALUES ({values_str})')
        await cur.execute(f'INSERT INTO Players (tgid, username, firstname, lastname, banned) VALUES ({values_str})')
        await cur.execute(f'UPDATE PLayers SET clicks = 0 WHERE tgid = {tgid}')
        await cur.execute('COMMIT')

        output = {'message': 'success'}

    except aiosqlite.OperationalError:
        output = {'message': 'operationalError!'}

    except Exception:
        output = {'message': 'Other exception...'}

    resp = flask.Response(json.dumps(output))
    resp.headers['Content-Type'] = 'application/html'

    return resp


@app.route('/botapi/set_await_query_id/<tgid>/<key>')
async def set_awaiting_query_id(tgid=0, key=0):
    if int(key) != int(os.getenv('botkey')):
        return {'code': '2'}

    try:
        await cur.execute(f'UPDATE Players SET awaiting_query = 1 WHERE tgid = {tgid}')
        await cur.execute('COMMIT')
    except aiosqlite.OperationalError:
        return {'code': '1'}

    return {'code': '0'}


@app.route('/botapi/unawait_query/<tgid>')
async def unawait_query(tgid=0):
    try:
        await cur.execute(f'UPDATE Players SET awaiting_query = 0 WHERE tgid = {tgid}')
        await cur.execute('COMMIT')
    except aiosqlite.OperationalError:
        return {'code': '1'}

    print('unawaited')
    return {'code': '0'}


@app.route('/put/query_id/<tgid>/<query_id>')
async def set_query_id(tgid=0, query_id=''):
    print('running')
    awaiting_query = ((await (await cur.execute(f'SELECT awaiting_query FROM Players WHERE tgid = {tgid}')).fetchone())[0] == 1)
    if awaiting_query:
        await cur.execute(f'UPDATE Players SET query_id = "{query_id}" WHERE tgid = {tgid}')
        await cur.execute(f'UPDATE Players SET awaiting_query = 0 WHERE tgid = {tgid}')
        await cur.execute('COMMIT')
        print('updated query')
    else:
        print(f'Unawaited query')

    return {}


@app.route('/put/clickcount/<tgid>/<query_id>/<count>')
async def update_clicks(tgid=0, query_id='', count=''):
    banned = False

    res = await (await cur.execute(f'SELECT banned FROM Players WHERE tgid = {tgid}')).fetchone()

    if res is None:
        return {'banned': 0, 'clicks': '0'}
    else:
        res = res[0]

    banned = bool(int(res))

    if banned:
        print('Thwarted banned request')

    try:
        count = float(count)
    except ValueError:
        banned = True

    if count - int(count) != 0:
        banned = True

    count = int(count)

    if count < 0 or count > 60:
        banned = True

    # Check if query_id matches

    good_query = await (await (await cur.execute(f'SELECT query_id FROM Players WHERE tgid = {tgid}')).fetchone())[0]

    if good_query != query_id:
        banned = True

    if banned:
        await cur.execute(f'UPDATE Players SET banned = "1" WHERE tgid = {tgid}')
        await cur.execute('COMMIT')
        return {'banned': '1'}

    current_clicks = await (await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}')).fetchone())[0]
    new_clicks = current_clicks + count
    await cur.execute(f'UPDATE Players SET clicks = {new_clicks} WHERE tgid = {tgid}')
    await cur.execute('COMMIT')

    return {'banned': '0', 'clicks': str(new_clicks)}


if __name__ == '__main__':
    # app.run(debug=True, port=5005)
    uvicorn.run(asgi_app, port=5005)
