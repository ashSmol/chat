import json
import time
import unittest
from unittest import mock

from common.vars import ENCODING, ACTION, PRESENCE, TIME, USER_ACCOUNT, ACCOUNT_NAME, RESPONSE, ERROR
from server import ChatServer


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_socket = mock.Mock()
        self.mock_socket.recv.return_value = json.dumps({'some_data': 123}).encode(ENCODING)

    # def test_something(self):
    #     message = read_message_from_sock(self.mock_socket)
    #     self.assertEqual(message, {'some_data': 123})

    def test_process_message_ok(self):
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER_ACCOUNT: {
                ACCOUNT_NAME: "Guest"
            }
        }
        self.assertEqual(ChatServer().process_message(message), {RESPONSE: 200})

    def test_process_message_no_action(self):
        message = {
            TIME: time.time(),
            USER_ACCOUNT: {
                ACCOUNT_NAME: "Guest"
            }
        }
        self.assertEqual(ChatServer().process_message(message), {
            RESPONSE: 400,
            ERROR: 'Incorrect request'
        })

    def test_process_message_no_time(self):
        message = {
            ACTION: PRESENCE,
            USER_ACCOUNT: {
                ACCOUNT_NAME: "Guest"
            }
        }
        self.assertEqual(ChatServer().process_message(message), {
            RESPONSE: 400,
            ERROR: 'Incorrect request'
        })

    def test_process_message_wrong_account(self):
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER_ACCOUNT: {ACCOUNT_NAME: "account_name"
                           }
        }
        self.assertEqual(ChatServer().process_message(message), {
            RESPONSE: 400,
            ERROR: 'Incorrect request'
        })

    def test_process_message_no_user_account(self):
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
        }
        self.assertEqual(ChatServer().process_message(message), {
            RESPONSE: 400,
            ERROR: 'Incorrect request'
        })

    def test_process_message_bad_request(self):
        message = ''
        self.assertRaises(Exception, ChatServer().process_message(message))


if __name__ == '__main__':
    unittest.main()
