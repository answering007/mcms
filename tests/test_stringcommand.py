import unittest

from mcms.commands import StringCommand
from mcms.connection import Connection


class TestStringCommand(unittest.TestCase):
    """ Test string command """
    def setUp(self):
        self.connection = Connection("localhost", 8000)
        self.ok = 200

    def test_single_command_say_hello(self):
        """test say hello command"""
        command = StringCommand("say hello")
        response = self.connection.execute_commands(command)
        self.assertEqual(response[0], self.ok)

    def test_multiple_command_say_hello(self):
        """test say hello command"""
        response = self.connection.execute_commands(commands_data=[
            (StringCommand("say first message"), None),
            ("say second message", None)])
        self.assertEqual(response[0], self.ok)
        self.assertEqual(response[1][0], True)
        self.assertEqual(response[1][1], True)


if __name__ == "__main__":
    unittest.main()
