import unittest

from client import ChatClient
from common.vars import RESPONSE, ERROR, TIME


class TestAnswerProcessing(unittest.TestCase):

    def test_process_ans_ok(self):
        message = {RESPONSE: 200}
        self.assertEqual(ChatClient().process_ans(message), '200 : OK')

    def test_process_ans_fail(self):
        message = {
            RESPONSE: 400,
            ERROR: 'Incorrect request'
        }
        self.assertEqual(ChatClient().process_ans(message), '400 : Incorrect request')

    def test_process_ans_no_response(self):
        self.assertRaises(ValueError, ChatClient().process_ans, {ERROR: 'Bad Request'})

    def test_create_presense(self):
        presence_rq = ChatClient().create_presence()
        presence_rq[TIME] = 123.123
        self.assertEqual(presence_rq, {'action': 'presence', 'time': 123.123, 'user_account': {'acc_name': 'Guest'}})

    if __name__ == '__main__':
        unittest.main()
