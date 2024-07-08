"""Connection to MCMS"""
import base64
import json
from typing import Any, Dict, List, Optional, Tuple, Union

import requests

from mcms.commands import StringCommand
from mcms.data import Block, GetBlockResponse, Location, Player

CommandInfo = Union[str, StringCommand, Tuple[str, str], Tuple[StringCommand, str]]

class Connection:

    """Connection to MCMS"""

    def __init__(self, address: str, port: int, credentials: Optional[Tuple[str, str]] = None):
        """
        Initializes a new instance of the Connection class with the provided address and port.

        Args:
            address (str): The address of the connection. This is the IP address of the server.
            port (int): Port of the connection. This is the port number on which the server is listening.
            credentials (Optional[Tuple[str, str]], optional): Tuple with username and password.
                This is optional and only needs to be provided if the server requires authentication.
                The tuple should contain the username as the first element and the password as the second element.
                Defaults to None, which means no authentication is used.

        Example:
            >>> connection = Connection("localhost", 8000)
            >>> connection = Connection("localhost", 8000, ("Admin", "123"))
        """
        # Construct the connection string from the provided address and port
        self._connection_string = f"http://{address}:{port}"
        # Store the credentials if provided, otherwise set it to None
        self._credentials = credentials

    def __str__(self):
        return self._connection_string

    def _encode_text(self, text: str) -> str:
        return base64.b64encode(text.encode(encoding="utf-8")).decode()

    def _is_ok(self, response: requests.Response) -> bool:
        ok = 200
        return response.status_code == ok

    def _process_response(self, object_to_dump, url: str, timeout: int) -> Tuple[int, Any]:
        """
        Process response:
        This method takes an object to dump and translate to JSON, an URL where to send the request,
        and a timeout in seconds. It sends a POST request to the URL with the encoded data as payload.
        If the response status code is not 200, it returns a tuple with the status code and an empty
        list. Otherwise, it returns a tuple with the status code and the JSON object in the response.

        Args:
            object_to_dump (object): The object to dump and translate to JSON.
            url (str): The URL where to send the request.
            timeout (int): The timeout in seconds.

        Returns:
            Tuple[int, Any]: A tuple with the status code and the JSON object in the response.
                             If the status code is not 200, the JSON object is an empty list.
        """
        # Dump the object to JSON and encode it
        # The object is converted to a JSON string and then encoded using base64
        # to ensure that it can be sent as payload in the HTTP request
        json_data = json.dumps(object_to_dump)
        encoded_data = self._encode_text(json_data)

        # Process the response
        # Send a POST request to the URL with the encoded data as payload
        response = requests.post(
            url, data=encoded_data, timeout=timeout, auth=self._credentials)

        # Check if the response status code is not 200
        # If it's not 200, return a tuple with the status code and an empty list
        if self._is_ok(response) is False:
            return (response.status_code, [])

        # If the response status code is 200, decode the JSON object in the response
        # and return a tuple with the status code and the JSON object
        return (response.status_code, json.loads(response.text))

    def execute_commands(self,
                          command: Union[CommandInfo, List[CommandInfo]],
                          timeout: Optional[int] = 10) -> Tuple[int, List[bool]]:
        """Execute a command or list of commands

        This method sends a command or a list of commands to the Minecraft server.
        The command can be of type:
        - String: This is a simple command string.
        - StringCommand: This is a command string object (see StringCommand class).
        - Tuple of string (command) and string (player name): This is a tuple with
          a command string and a player name. The command will be executed as if
          it was entered in the Minecraft server console by the specified player.
        - Tuple of StringCommand and string (player name): This is a tuple with
          a StringCommand object and a player name. The command will be executed as if
          it was entered in the Minecraft server console by the specified player.

        Args:
            command (Union[CommandInfo, List[CommandInfo]]): Command to execute.
            timeout (Optional[int], optional): Request timeout in seconds. Defaults to 10.

        Returns:
            Tuple[int, List[bool]]: Tuple with exit code and list of bool command results
        """
        # Helper function to convert a command to a dictionary
        def convert_to_dict(command: CommandInfo) -> Dict[str, str]:
            """Convert a command to a dictionary

            Args:
                command (CommandInfo): Command to convert.

            Returns:
                Dict[str, str]: Dictionary with "commandText" and "playerName" keys.

            Raises:
                ValueError: If command is not of the expected types.
            """
            msg = "Invalid command type"
            if isinstance(command, str):
                # Command is a simple string
                return {"commandText": command}
            elif isinstance(command, StringCommand):
                # Command is a StringCommand object
                return {"commandText": command.get_command_text()}
            elif isinstance(command, tuple):
                # Command is a tuple
                if isinstance(command[0], StringCommand):
                    # First element of the tuple is a StringCommand object
                    return {"commandText": command[0].get_command_text(), "playerName": command[1]}
                elif isinstance(command[0], str):
                    # First element of the tuple is a string
                    return {"commandText": command[0], "playerName": command[1]}
                else:
                    raise ValueError(msg)
            else:
                raise ValueError(msg)

        # URL for the command execution endpoint
        url = f"{self._connection_string}/runCommand"

        # Convert the command(s) to a list of dictionaries
        commands_list = []
        if isinstance(command, list):
            # If the command is a list, iterate over each element and convert it to a dictionary
            commands_list = [convert_to_dict(c) for c in command]
        else:
            # If the command is not a list, convert it to a dictionary
            commands_list = [convert_to_dict(command)]

        # Send the command(s) to the server and return the response
        return self._process_response(commands_list, url, timeout)

    def get_blocks(self,
                   location: Union[Location, List[Location]],
                   timeout: Optional[int] = 10) -> Tuple[int, List[GetBlockResponse]]:
        """
        Get blocks:
        This method retrieves one or more blocks from the Minecraft world.

        Args:
            location (Union[Location, List[Location]]): Location or list of locations
            timeout (Optional[int], optional): Timeout in seconds. Defaults to 10.

        Returns:
            Tuple[int, List[GetBlockResponse]]:
                Tuple of status code and list of GetBlockResponse.
                GetBlockResponse contains information about the retrieved block,
                including its location, state, and inventory.
        """

        # Prepare request
        # Construct the URL for the getBlock request
        url = f"{self._connection_string}/getBlock"

        # If location is a single Location object, convert it to a list
        block_request = location if isinstance(location, list) else [location]

        # Convert each Location object in block_request to its request data representation
        blocks_list = [item.to_request_data() for item in block_request]

        # Process response
        # Send the request and get the response
        status_code, block_response = self._process_response(blocks_list, url, timeout)

        # Join request and response
        # Combine the request (Location) and response (Dict[str, Any]) into a list of tuples
        # Each tuple contains the request (Location) and response (Dict[str, Any])
        block_source = list(zip(block_request, block_response))

        # Convert each tuple to a GetBlockResponse object
        # Parse the response data and create GetBlockResponse objects
        # GetBlockResponse contains information about the retrieved block,
        # including its location, state, and inventory.
        result = [GetBlockResponse.from_request_response_data(source[0], source[1]) for source in block_source]

        # Return the status code and the list of GetBlockResponse objects
        return (status_code, result)

    def set_blocks(self,
                   blocks: Union[Block, List[Block]],
                   timeout: Optional[int] = 10
                   ) -> Tuple[int, List[Tuple[bool, str]]]:
        """
        Set blocks:
        This method sets one or more blocks in the Minecraft world.

        Args:
            blocks (Union[Block, List[Block]]): Single block or list of blocks to set.
            timeout (Optional[int], optional): Optional timeout in seconds. Defaults to 10.

        Returns:
            Tuple[int, List[Tuple[bool, str]]]: Tuple of status code and list of
            (success, exception). This list contains a tuple for each block that was set.
            The tuple contains a boolean value indicating whether the set operation was
            successful and a string representing any exception that occurred during the set operation.
        """

        # Construct the URL for the setBlock API endpoint
        url = f"{self._connection_string}/setBlock"

        # Check if the blocks argument is a single block or a list of blocks
        list_of_blocks = blocks if isinstance(blocks, list) else [blocks]

        # Convert each block in the list to the request data format
        blocks_request = [b.to_request_data() for b in list_of_blocks]

        # Call the _process_response method to send the request and process the response
        return self._process_response(blocks_request, url, timeout)

    def get_players(self,
                    only_online: bool = True,  # noqa: FBT001, FBT002
                    timeout: Optional[int] = 10) -> Tuple[int, List[Player]]:
        """Get players

        Args:
            only_online (bool, optional): Only online players. Defaults to True.
            timeout (Optional[int], optional): Timeout in seconds. Defaults to 10.

        Returns:
            Tuple[int, List[Player]]: Tuple of status code and list of players
        """

        # Construct the URL for the getPlayers API endpoint
        url = f"{self._connection_string}/getPlayers"

        # Call the _process_response method to send the request and process the response
        # The response is a list of dictionaries representing the players.
        code, response = self._process_response(only_online, url, timeout)

        # Convert each dictionary in the list to a Player object
        # The Player object contains information about the player, such as their name, location, health, and items.
        players = [Player.from_request_data(p) for p in response]

        # Return a tuple containing the status code and the list of Player objects
        return code, players
