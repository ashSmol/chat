import time
import time
import unittest

from common.vars import ACTION, PRESENCE, TIME, USER_ACCOUNT, ACCOUNT_NAME, RESPONSE, ERROR
from server import ChatServer


class TestServer(unittest.TestCase):

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
