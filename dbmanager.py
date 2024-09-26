import os
import time
import random

import aiosqlite
import uvicorn
import json
import dotenv
import asyncio
from asgiref.wsgi import WsgiToAsgi

import flask
from flask import Flask, request


async def create_app():
    my_app = Flask(__name__)
    global cur
    print("Configuring...")
    cur = await aiosqlite.connect('database.db')
    dotenv.load_dotenv()
    print("Finished")

    return my_app


app = asyncio.run(create_app())


"""
@app.before_request
async def before_request():
    global cur
    con = await aiosqlite.connect('database.db')
    cur = await con.cursor()
    dotenv.load_dotenv()
"""


@app.route('/')
async def hello():
    return {'message': 'You have reached the server! Everything is functional.'}


@app.route('/leaderboard/')
async def fetch_leaderboard():
    res = await (await cur.execute('SELECT firstname, clicks FROM Players')).fetchall()

    res = sorted(res, key=lambda x: int(x[1]))[-10:]
    res = [[x[0], str(x[1])] for x in res]

    return {"board": res[::-1]}


@app.route('/request/banned/<tgid>')
async def check_banned(tgid=0):
    res = await (await cur.execute(f'SELECT banned FROM Players WHERE tgid = {tgid}')).fetchone()

    if res is None:
        return {'banned': '2'}

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
        res = '-1'
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
        response = {'registered': '0'}
    else:
        response = {'registered': '1'}

    resp = flask.Response(json.dumps(response))
    resp.headers['Content-Type'] = 'application/json'

    return resp


@app.route('/botapi/register_user/<tgid>', methods=['GET'])
async def register(tgid=0):
    params = request.json

    name = params['name']
    last = params['last']
    usr = params['usr']
    ref = random.randint(0, 18446744073709551615)
    ref = hex(ref)[2:].upper()

    try:
        values_str = str(tgid) + ', 0, "' + '", "'.join([usr, name, last, "0"]) + '", ' + f'"{ref}", 0, 15'
        # print("Executing: " + f'INSERT INTO Players (tgid, username, firstname, lastname) VALUES ({values_str})')
        await cur.execute(f'INSERT INTO Players (tgid, time, username, firstname, lastname, banned, ref, is_reffed, strikes) VALUES ({values_str})')
        await cur.execute(f'UPDATE PLayers SET clicks = 0 WHERE tgid = {tgid}')
        await cur.execute('COMMIT')

        output = {'message': 'success'}

    except aiosqlite.OperationalError as e:
        output = {'message': f'operationalError!\n\n{e}'}

    except Exception as e:
        output = {f'message': f'Uncaught exception of type {e}'}

    resp = flask.Response(json.dumps(output))
    resp.headers['Content-Type'] = 'application/json'

    return resp


@app.route('/botapi/fetchref/<tgid>')
async def fetch_ref(tgid=0):
    ref = (await (await cur.execute(f'SELECT ref FROM Players WHERE tgid = {tgid}')).fetchone())[0]
    return {'ref': ref}


@app.route('/botapi/doref/<tgid>/<ref>')
async def do_ref(tgid=0, ref=''):
    # check if reffed
    is_reffed = (await (await cur.execute(f'SELECT is_reffed FROM Players WHERE tgid = {tgid}')).fetchone())[0]
    is_reffed = bool(int(is_reffed))

    if is_reffed:
        output = {'message': 'denied'}
    else:
        donor_id = await (await cur.execute(f'SELECT tgid FROM Players WHERE ref = "{ref}"')).fetchone()

        if donor_id is None:
            output = {'message': 'invalid'}
        elif donor_id == tgid:
            output = {'message': 'selfref'}
        else:
            donor_id = donor_id[0]

            # update donor clicks
            old_donor_clicks = (await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {donor_id}')).fetchone())[0]
            new_donor_clicks = old_donor_clicks + 500
            await cur.execute(f'UPDATE Players SET clicks = {new_donor_clicks} WHERE tgid = {donor_id}')

            # update player clicks
            old_player_clicks = (await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}')).fetchone())[0]
            new_player_clicks = old_player_clicks + 1000
            await cur.execute(f'UPDATE Players SET clicks = {new_player_clicks} WHERE tgid = {tgid}')
            await cur.execute(f'UPDATE Players SET is_reffed = 1 WHERE tgid = {tgid}')

            await cur.execute('COMMIT')

            output = {'message': 'ok'}

    resp = flask.Response(json.dumps(output))
    resp.headers['Content-Type'] = 'application/json'

    return resp


@app.route('/botapi/<key>/registername/<tgid>')
async def register_name(key=0, tgid=0):
    if int(key) != int(os.getenv('botkey')):
        return

    text = request.json['text']

    await cur.execute(f'INSERT INTO userdata (tgid, text) VALUES ({tgid}, "{text}")')
    await cur.execute('COMMIT')


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
    awaiting_query = ((await (await cur.execute(f'SELECT awaiting_query FROM Players WHERE tgid = {tgid}')).fetchone())[0] == 1)
    if awaiting_query:
        await cur.execute(f'UPDATE Players SET query_id = "{query_id}" WHERE tgid = {tgid}')
        await cur.execute(f'UPDATE Players SET awaiting_query = 0 WHERE tgid = {tgid}')
        await cur.execute('COMMIT')
    else:
        print(f'Unawaited query')

    return {}


async def process_energy(tgid, spent_energy):
    old_time, old_energy = await (await cur.execute(f'SELECT energy_time, energy FROM Players WHERE tgid = {tgid}')).fetchone()[0]

    # calculate energy per second
    eph = await (await cur.execute('SELECT Value FROM Params WHERE Key = "eph"')).fetchone()[0]
    epms = eph / (60*60*1000)

    timediff = time.time() * 1000 - old_time
    energy_delta = int(time * epms)
    new_energy = old_energy + energy_delta - spent_energy

    if new_energy > eph:
        new_energy = eph

    await cur.execute(f'UPDATE TABLE Players SET energy = {new_energy}, energy_time = {time.time() * 1000} WHERE tgid = {tgid}')
    await cur.execute('COMMIT')


@app.route('/put/clickcount/<tgid>/<query_id>/<count>')
async def update_clicks(tgid=0, query_id='', count=''):
    banned = False
    strike = False

    res = await (await cur.execute(f'SELECT banned FROM Players WHERE tgid = {tgid}')).fetchone()
    last_time = await (await cur.execute(f'SELECT time FROM Players WHERE tgid = {tgid}')).fetchone()
    print(last_time)

    if res is None:
        return {'stale': '0', 'banned': 0, 'clicks': '0'}
    else:
        res = res[0]
        last_time = int(last_time[0])

    banned = bool(int(res))

    if banned:
        print('Thwarted banned request')

    try:
        count = float(count)
    except ValueError:
        banned = True
    else:
        if count - int(count) != 0:
            banned = True

        count = int(count)

        if count < 0 or count > 120:
            banned = True

        # Check if query_id matches

        good_query = (await (await cur.execute(f'SELECT query_id FROM Players WHERE tgid = {tgid}')).fetchone())[0]

        if good_query != query_id:
            return {'stale': '1', 'banned': '0', 'clicks': str(
                (await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}')).fetchone())[0])}

        # check time
        ms_time = int(time.time() * 1000)
        now = int(time.time())

        if now - last_time < 4:
            strike = True

        old_strikes = (await (await cur.execute(f'SELECT strikes FROM Players WHERE tgid = {tgid}')).fetchone())[0]

        if old_strikes < 0:
            banned = True

    if banned:
        await cur.execute(f'UPDATE Players SET banned = "1" WHERE tgid = {tgid}')
        await cur.execute('COMMIT')
        return {'stale': '0', 'banned': '1', 'clicks': str((await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}')).fetchone())[0])}

    if strike:
        new_strikes = (await (await cur.execute(f'SELECT strikes FROM Players WHERE tgid = {tgid}')).fetchone())[0] - 1
        await cur.execute(f'UPDATE Players SET strikes = {new_strikes} WHERE tgid = {tgid}')

    current_clicks = (await (await cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}')).fetchone())[0]
    new_clicks = current_clicks + count
    await cur.execute(f'UPDATE Players SET clicks = {new_clicks}, time = {now} WHERE tgid = {tgid}')
    await cur.execute('COMMIT')

    await process_energy(tgid, count)

    return {'stale': '0', 'time': ms_time, 'banned': '0', 'clicks': str(new_clicks), 'energy': str(await (await cur.execute(f'SELECT energy FROM Players WHERE tgid = {tgid}')).fetchone())}


if __name__ == '__main__':
    # app.run(debug=True, port=5005)
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(asgi_app, port=5005)
