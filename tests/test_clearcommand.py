import unittest

from mcms.commands import ClearCommand
from mcms.connection import Connection


class TestClearCommand(unittest.TestCase):
    """ Test clear command """
    def setUp(self):
        self.connection = Connection("localhost", 8000)
        self.player_name = "Papa"
        self.ok = 200

    def test_clear_command(self):
        """test clear command"""
        command = ClearCommand(player_name=self.player_name)
        response = self.connection.execute_commands(command)
        self.assertEqual(response[0], self.ok)


if __name__ == "__main__":
    unittest.main()
