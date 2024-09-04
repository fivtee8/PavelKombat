import unittest
import requests


class TestNgrok(unittest.TestCase):
    def test_ngrok_hello(self):
        headers = {'ngrok-skip-browser-warning': 'true'}
        response = requests.get('https://fond-pangolin-lately.ngrok-free.app/', headers=headers)

        try:
            new_response = response.json()['message']
            self.assertEqual(new_response, 'You have reached the server! Everything is functional.')
        except requests.exceptions.JSONDecodeError:
            self.fail(f'Connection to ngrok failed. This could be a server failure or a Ngrok failure. {response.text}')


if __name__ == '__main__':
    unittest.main()
