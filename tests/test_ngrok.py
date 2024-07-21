import unittest
import requests


class TestNgrok(unittest.TestCase):
    def test_ngrok_hello(self):
        try:
            response = requests.get('https://fond-pangolin-lately.ngrok-free.app/').json()['message']
            self.assertEqual(response, 'You have reached the server! Everything is functional.')
        except requests.exceptions.JSONDecodeError:
            self.fail('Connection to ngrok failed. This could be a server failure or a Ngrok failure. Run server tests.')


if __name__ == '__main__':
    unittest.main()
