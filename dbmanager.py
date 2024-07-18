import os
import sqlite3
import json
import dotenv

import flask
from flask import Flask, request

app = Flask(__name__)


@app.before_request
def before_request():
    global cur
    con = sqlite3.connect('database.db')
    cur = con.cursor()


@app.route('/request/starttime/')
def start_time():
    res = cur.execute('SELECT Value FROM Params WHERE Key="starttime"')
    res = {'time': str(res.fetchone()[0])}

    return res


@app.route('/request/clickcount/<playerid>')
def return_click(playerid=0):
    res = cur.execute(f'SELECT clicks FROM Players WHERE tgid = {playerid}').fetchone()

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
def check_registered(tgid=0):
    res = cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}').fetchone()

    if res is None:
        return {'registered': '0'}
    else:
        return {'registered': '1'}


@app.route('/botapi/register_user/<tgid>', methods=['GET'])
def register(tgid=0):
    params = request.json

    name = params['name']
    last = params['last']
    usr = params['usr']

    try:
        values_str = str(tgid) + ', "' + '", "'.join([usr, name, last, "0"]) + '"'
        # print("Executing: " + f'INSERT INTO Players (tgid, username, firstname, lastname) VALUES ({values_str})')
        cur.execute(f'INSERT INTO Players (tgid, username, firstname, lastname, banned) VALUES ({values_str})')
        cur.execute(f'UPDATE PLayers SET clicks = 0 WHERE tgid = {tgid}')
        cur.execute('COMMIT')

        output = {'message': 'success'}

    except sqlite3.OperationalError:
        output = {'message': 'operationalError!'}

    except Exception:
        output = {'message': 'Other exception...'}

    resp = flask.Response(json.dumps(output))
    resp.headers['Content-Type'] = 'application/html'

    return resp


@app.route('/botapi/set_await_query_id/<tgid>/<key>')
def set_awaiting_query_id(tgid=0, key=0):
    if int(key) != int(os.getenv('botkey')):
        return {'code': '2'}

    try:
        cur.execute(f'UPDATE Players SET awaiting_query = 1 WHERE tgid = {tgid}')
        cur.execute('COMMIT')
    except sqlite3.OperationalError:
        return {'code': '1'}

    return {'code': '0'}


@app.route('/botapi/unawait_query/<tgid>')
def unawait_query(tgid=0):
    try:
        cur.execute(f'UPDATE Players SET awaiting_query = 0 WHERE tgid = {tgid}')
        cur.execute('COMMIT')
    except sqlite3.OperationalError:
        return {'code': '1'}

    print('unawaited')
    return {'code': '0'}


@app.route('/put/query_id/<tgid>/<query_id>')
def set_query_id(tgid=0, query_id=''):
    print('running')
    awaiting_query = (cur.execute(f'SELECT awaiting_query FROM Players WHERE tgid = {tgid}').fetchone()[0] == 1)
    if awaiting_query:
        cur.execute(f'UPDATE Players SET query_id = "{query_id}" WHERE tgid = {tgid}')
        cur.execute(f'UPDATE Players SET awaiting_query = 0 WHERE tgid = {tgid}')
        cur.execute('COMMIT')
        print('updated query')
    else:
        print(f'Unawaited query')


@app.route('/put/clickcount/<tgid>/<query_id>/<count>')
def update_clicks(tgid=0, query_id='', count=''):
    banned = False

    res = cur.execute(f'SELECT banned FROM Players WHERE tgid = {tgid}').fetchone()

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

    #Check if query_id matches

    good_query = cur.execute(f'SELECT query_id FROM Players WHERE tgid = {tgid}').fetchone()[0]

    if good_query != query_id:
        banned = True

    if banned:
        cur.execute(f'UPDATE Players SET banned = "1" WHERE tgid = {tgid}')
        cur.execute('COMMIT')
        return {'banned': '1'}

    current_clicks = cur.execute(f'SELECT clicks FROM Players WHERE tgid = {tgid}').fetchone()[0]
    new_clicks = current_clicks + count
    cur.execute(f'UPDATE Players SET clicks = {new_clicks} WHERE tgid = {tgid}')
    cur.execute('COMMIT')

    return {'banned': '0', 'clicks': str(new_clicks)}


if __name__ == '__main__':
    app.run(debug=True, port=5005)