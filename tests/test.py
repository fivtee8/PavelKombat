import json
import unittest
import requests
import sqlite3


class TestServer(unittest.TestCase):
    def test_hello(self):
        req = requests.get('http://127.0.0.1:5005/').json()
        message = req['message']

        self.assertEqual(message, 'You have reached the server! Everything is functional.', 'Hello message failed. Server down?')

    def test_table_exists(self):
        # staging
        con = sqlite3.connect('../database.db')
        cur = con.cursor()

        try:
            cur.execute('SELECT * FROM Players')
        except sqlite3.OperationalError:
            self.fail('Players table missing')

    def test_check_banned(self):
        # staging
        con = sqlite3.connect('../database.db')
        cur = con.cursor()

        cur.execute('INSERT INTO Players (tgid, banned) VALUES (1, "0")')
        cur.execute('COMMIT')

        try:
            req = requests.get('http://127.0.0.1:5005/request/banned/1').json()['banned']
        except Exception:
            self.fail('Server error - see server log')

        if req == '2':
            self.fail('Player not found in table.')

        self.assertEqual(req, '0')

        cur.execute('UPDATE Players SET banned = "1" WHERE tgid = 1')
        cur.execute('COMMIT')

        req = requests.get('http://127.0.0.1:5005/request/banned/1').json()['banned']

        if req == '2':
            self.fail('Player not found in table.')

        self.assertEqual(req, '1')

        # clean up
        cur.execute('DELETE FROM Players WHERE tgid = 1')
        cur.execute('COMMIT')

    def test_start_time(self):
        # staging
        con = sqlite3.connect('../database.db')
        cur = con.cursor()

        # test Params exist
        try:
            cur.execute('SELECT * FROM Params')
        except sqlite3.OperationalError:
            self.fail('Params table not initialized')

        # test time configured

        try:
            res = cur.execute('SELECT Value FROM Params WHERE Key = "starttime"').fetchone()[0]
            self.assertGreater(len(res), 3, 'invalid starttime')
        except sqlite3.OperationalError:
            self.fail('starttime value not set')

        # test server response
        try:
            req = requests.get('http://127.0.0.1:5005/request/starttime/').json()['time']
        except Exception:
            self.fail('server error in start_time')

        self.assertEqual(res, req, 'server time different than db time')

    def test_get_click(self):
        # staging
        con = sqlite3.connect('../database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid = 1')
        cur.execute('COMMIT')

        try:
            req = requests.get('http://127.0.0.1:5005/request/clickcount/1').json()['clicks']
            self.assertEqual(req, '-1')
        except Exception:
            self.fail('Server Error')

        cur.execute('INSERT INTO Players (tgid, clicks) VALUES (1, 5)')
        cur.execute('COMMIT')

        try:
            req = requests.get('http://127.0.0.1:5005/request/clickcount/1').json()['clicks']
            self.assertEqual(req, '5')
        except Exception:
            self.fail('Server Error')

        # clean up
        cur.execute('DELETE FROM Players WHERE tgid = 1')
        cur.execute('COMMIT')

    def test_register(self):
        # staging
        con = sqlite3.connect('../database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid = 1')
        cur.execute('COMMIT')

        for name in ["hello", 'привет', '☃☃☃☃']:
            data = {'usr': 'usr', 'name': name,
                    'last': 'last'}
            data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}

            try:
                raw_message = requests.get('http://127.0.0.1:5005/botapi/register_user/1', data=data, headers=headers)
                message = raw_message.json()['message']
            except requests.exceptions.JSONDecodeError:
                self.fail('Request failed. Text: ' + raw_message.text)

            if message != 'success':
                self.fail(message)

            username, firstname, lastname, clicks, banned = cur.execute('SELECT username, firstname, lastname, clicks, banned FROM Players WHERE tgid = 1').fetchone()

            self.assertEqual(username, 'usr', 'Wrong username')
            self.assertEqual(lastname, 'last', 'lastname wrong')
            self.assertEqual(clicks, 0)
            self.assertEqual(banned, '0')
            self.assertEqual(firstname, name, f'Error registering name {name}')

            # clean up
            cur.execute('DELETE FROM Players WHERE tgid = 1')
            cur.execute('COMMIT')
