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