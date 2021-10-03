import json
import unittest

from common.utils import write_message_to_sock, read_message_from_sock
from common.vars import ENCODING


class TestUtils(unittest.TestCase):
    test_dict = {'test': 'test'}

    def test_write_to_sock(self):
        mock_sock = MockSocket(self.test_dict)
        write_message_to_sock(self.test_dict, mock_sock)
        self.assertEqual(mock_sock.send_message, mock_sock.recv_message)
        with self.assertRaises(Exception):
            write_message_to_sock(mock_sock, 'mock_sock')

    def test_read_from_socket(self):
        mock_socket = MockSocket(self.test_dict)
        self.assertEqual(read_message_from_sock(mock_socket), self.test_dict)


class MockSocket():
    def __init__(self, message):
        self.test_message = message
        self.send_message = None
        self.recv_message = None

    def send(self, message):
        json_test_message = json.dumps(self.test_message)
        self.send_message = json_test_message.encode(ENCODING)
        self.recv_message = message

    def recv(self, max_len):
        json_obj_message = json.dumps(self.test_message)
        return json_obj_message.encode(ENCODING)


if __name__ == '__main__':
    unittest.main()
