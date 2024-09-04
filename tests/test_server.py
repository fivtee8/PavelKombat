import json
import os
import unittest
import requests
import sqlite3
import dotenv
import time
import logging
import sys

logger = logging.getLogger('TestServer')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger('urllib3').setLevel('WARNING')
logger.info('Logging started')


class TestServer(unittest.TestCase):
    def test_hello(self):
        req = requests.get('http://127.0.0.1:5005/').json()
        message = req['message']

        self.assertEqual(message, 'You have reached the server! Everything is functional.', 'Hello message failed. Server down?')

    def test_dotenv(self):
        dotenv.load_dotenv()
        self.assertNotEqual(os.environ.get('botkey'), None)
        self.assertNotEqual(os.environ.get('BOT_TOKEN'), None)

    def test_table_exists(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        try:
            cur.execute('SELECT * FROM Players')
        except sqlite3.OperationalError:
            self.fail('Players table missing')

    def test_check_banned(self):
        # staging
        con = sqlite3.connect('database.db')
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
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

    def test_start_time(self):
        # staging
        con = sqlite3.connect('database.db')
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
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
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
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

    def test_register(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

        for name in ["hello", 'привет', '☃☃☃☃']:
            data = {'usr': 'usr', 'name': name,
                    'last': 'last'}
            data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}

            raw_message = requests.get('http://127.0.0.1:5005/botapi/register_user/1', data=data, headers=headers)
            try:
                message = raw_message.json()['message']
            except requests.exceptions.JSONDecodeError:
                self.fail('Request failed. Text: ' + raw_message.text)

            if message != 'success':
                self.assertEqual(0, 1, f'message: {message}; raw text: {raw_message.text}')

            username, firstname, lastname, clicks, banned, time_up, ref = cur.execute('SELECT username, firstname, lastname, clicks, banned, time, ref FROM Players WHERE tgid = 1').fetchone()

            ref_true = all([True for x in ref if x in '1234567890ABCDEF'])

            self.assertEqual(username, 'usr', 'Wrong username')
            self.assertEqual(lastname, 'last', 'lastname wrong')
            self.assertEqual(clicks, 0)
            self.assertTrue(ref_true)
            self.assertEqual(banned, '0')
            self.assertEqual(time_up, 0)
            self.assertEqual(firstname, name, f'Error registering name {name}')

            # test get ref

            response = requests.get('http://127.0.0.1:5005/botapi/fetchref/1').json()['ref']
            self.assertEqual(response, ref)


            # clean up
            cur.execute('DELETE FROM Players WHERE tgid < 20')
            cur.execute('COMMIT')

    def test_ref_denied(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, ref) VALUES (1, 100, "0", "testref")')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, is_reffed) VALUES (2, 100, "0", 1)')
        cur.execute('COMMIT')

        is_clicks = cur.execute('SELECT clicks FROM Players WHERE tgid = 2').fetchone()[0]
        self.assertEqual(is_clicks, 100)

        is_reffed = cur.execute('SELECT is_reffed FROM Players WHERE tgid = 2').fetchone()[0]
        self.assertEqual(is_reffed, 1)

        # test denied case
        message = requests.get('http://127.0.0.1:5005/botapi/doref/2/testref').json()['message']
        self.assertEqual(message, 'denied')

        # clean up
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

    def test_ref_invalid(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, is_reffed) VALUES (1, 100, "0", 0)')
        cur.execute('COMMIT')

        # test invalid case
        message = requests.get('http://127.0.0.1:5005/botapi/doref/1/thisisinvalid').json()['message']
        self.assertEqual(message, 'invalid')

        # clean up
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

    def test_ref_ok(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, ref) VALUES (1, 0, "0", "testref")')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, is_reffed) VALUES (2, 0, "0", 0)')
        cur.execute('COMMIT')

        # test
        message = requests.get('http://127.0.0.1:5005/botapi/doref/2/testref').json()['message']
        self.assertEqual(message, 'ok')

        player_clicks = cur.execute('SELECT clicks FROM Players WHERE tgid = 2').fetchone()[0]
        donor_clicks = cur.execute('SELECT clicks FROM Players WHERE tgid = 1').fetchone()[0]
        reffed = cur.execute('SELECT is_reffed FROM Players WHERE tgid = 2').fetchone()[0]

        self.assertEqual(player_clicks, 1000, f'clicks is {player_clicks}')
        self.assertEqual(donor_clicks, 500, f'clicks is {donor_clicks}')
        self.assertEqual(reffed, 1)

    def test_update_clicks(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, query_id, time) VALUES (1, 100, "0", "dev", 0)')
        cur.execute('COMMIT')

        # test good path
        try:
            response = requests.get('http://127.0.0.1:5005/put/clickcount/1/dev/11').json()
            self.assertEqual(response['banned'], '0')
            self.assertEqual(response['clicks'], '111')
        except requests.exceptions.JSONDecodeError:
            self.fail('Server error')

        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, query_id, time) VALUES (1, 100, "0", "dev", 0)')
        cur.execute('COMMIT')

        try:
            response = requests.get('http://127.0.0.1:5005/put/clickcount/1/wrongquery/11').json()
            self.assertEqual(response['banned'], '0')
            self.assertEqual(response['clicks'], '100')
            self.assertEqual(response['stale'], '1')
        except requests.exceptions.JSONDecodeError:
            self.fail('Server error')

        for click_count in [-1, 100, 'yabadaba']:
            cur.execute('DELETE FROM Players WHERE tgid < 20')
            cur.execute('INSERT INTO Players (tgid, clicks, banned, query_id, time) VALUES (1, 100, "0", "dev", 0)')
            cur.execute('COMMIT')

            try:
                response = requests.get(f'http://127.0.0.1:5005/put/clickcount/1/dev/{click_count}').json()
                self.assertEqual(response['banned'], '1')
                self.assertEqual(response['clicks'], '100')
            except requests.exceptions.JSONDecodeError:
                self.fail('Server error')

        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, query_id, time) VALUES (1, 100, "1", "dev", 0)')
        cur.execute('COMMIT')

        try:
            response = requests.get(f'http://127.0.0.1:5005/put/clickcount/1/dev/10').json()
            self.assertEqual(response['banned'], '1')
            self.assertEqual(response['clicks'], '100')
        except requests.exceptions.JSONDecodeError:
            self.fail('Server error')

        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, query_id, time) VALUES (1, 100, "0", "dev", 0)')
        cur.execute('COMMIT')

        try:
            response = requests.get(f'http://127.0.0.1:5005/put/clickcount/1/dev/10').json()
            self.assertEqual(response['banned'], '0')
            self.assertEqual(response['clicks'], '110')
            response = requests.get(f'http://127.0.0.1:5005/put/clickcount/1/dev/10').json()
            self.assertEqual(response['banned'], '1')
            self.assertEqual(response['clicks'], '110')
        except requests.exceptions.JSONDecodeError:
            self.fail('Server error')

        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, query_id, time) VALUES (1, 100, "0", "dev", 0)')
        cur.execute('COMMIT')

        try:
            response = requests.get(f'http://127.0.0.1:5005/put/clickcount/1/dev/10').json()
            self.assertEqual(response['banned'], '0')
            self.assertEqual(response['clicks'], '110')

            try:
                server_time = response['time']
            except KeyError:
                self.fail('Server does not return time parameter.')

            now = int(time.time() * 1000)
            ping = now - server_time

            logger.info(f'Server one-way ping: {ping}ms')

        except requests.exceptions.JSONDecodeError:
            self.fail('Server error')

        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, clicks, banned, query_id, time) VALUES (1, 100, "0", "dev", 0)')
        cur.execute('COMMIT')

        try:
            response = requests.get(f'http://127.0.0.1:5005/put/clickcount/1/dev/10').json()
            self.assertEqual(response['banned'], '0')
            self.assertEqual(response['clicks'], '110')
            time.sleep(5)
            response = requests.get(f'http://127.0.0.1:5005/put/clickcount/1/dev/10').json()
            self.assertEqual(response['banned'], '0')
            self.assertEqual(response['clicks'], '120')
        except requests.exceptions.JSONDecodeError:
            self.fail('Server error')

        # clean up
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

    def test_set_awaiting_query_id(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, banned, awaiting_query) VALUES (1, "0", 0)')
        cur.execute('COMMIT')

        dotenv.load_dotenv(dotenv_path='.env')
        key = os.environ.get('botkey')

        # test valid path
        try:
            response = requests.get(f'http://127.0.0.1:5005/botapi/set_await_query_id/1/{key}').json()['code']
            self.assertEqual(response, '0')

            result = cur.execute('SELECT awaiting_query FROM Players WHERE tgid = 1').fetchone()[0]
            self.assertEqual(result, 1)
        except requests.exceptions.JSONDecodeError:
            self.fail('Uncaught serverside exception')

        # test wrong botkey
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, banned, awaiting_query) VALUES (1, "0", 0)')
        cur.execute('COMMIT')

        try:
            response = requests.get(f'http://127.0.0.1:5005/botapi/set_await_query_id/1/666').json()['code']
            self.assertEqual(response, '2')
            result = cur.execute('SELECT awaiting_query FROM Players WHERE tgid = 1').fetchone()[0]
            self.assertEqual(result, 0)
        except requests.exceptions.JSONDecodeError:
            self.fail('Uncaught serverside exception')

        # clean up
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

    def test_set_query_id(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, banned, awaiting_query, query_id) VALUES (1, "0", 1, "stale")')
        cur.execute('COMMIT')

        try:
            requests.get(f'http://127.0.0.1:5005/put/query_id/1/dev').json()

            result = cur.execute('SELECT query_id FROM Players WHERE tgid = 1').fetchone()[0]
            self.assertEqual(result, "dev")
        except requests.exceptions.JSONDecodeError:
            self.fail('Uncaught serverside exception')

        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('INSERT INTO Players (tgid, banned, awaiting_query, query_id) VALUES (1, "0", 0, "stale")')
        cur.execute('COMMIT')

        try:
            response = requests.get(f'http://127.0.0.1:5005/put/query_id/1/dev').json()

            result = cur.execute('SELECT query_id FROM Players WHERE tgid = 1').fetchone()[0]
            self.assertEqual(result, "stale")
        except requests.exceptions.JSONDecodeError:
            self.fail('Uncaught serverside exception')

        cur.execute('DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')

    def test_leaderboard(self):
        # staging
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('DELETE FROM Players WHERE tgid < 20')

        for i in range(1, 11):
            cur.execute(f'INSERT INTO Players (tgid, firstname, clicks, banned) VALUES ({i}, "{i}", {i * 1000000}, "0")')

        cur.execute('COMMIT')

        try:
            response = requests.get(f'http://127.0.0.1:5005/leaderboard/').json()

            good_list = [[str(x), str(x * 1000000)] for x in range(1, 11)][::-1]

            self.assertEqual(good_list, response['board'])
        except json.JSONDecodeError:
            self.fail('Uncaught serverside exception')

        cur.execute(f'DELETE FROM Players WHERE tgid < 20')
        cur.execute('COMMIT')


if __name__ == '__main__':
    unittest.main()
