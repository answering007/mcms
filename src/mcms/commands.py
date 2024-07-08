"""Module providing classes for MCMS commands"""

from typing import Any, Dict, Optional, Tuple, Union

from mcms.enums import BlockChange, BlockHandling, Coordinate
from mcms.utils import format_coordinates, format_state, format_tags


class StringCommand:
    """Base class for commands with string representation"""
    def __init__(self, command_text: str):
        """String command

        Args:
            command_text (str): Text of the command
        """
        self._command_text = command_text

    def __str__(self):
        return f"{__class__.__name__}: {self.get_command_text()}"

    def get_command_text(self) -> str:
        """Returns the command text stored in the instance

        Returns:
            str: Command text
        """
        return self._command_text

    def _compose_command(self, *args) -> str:
        return " ".join([str(v) for v in args if v is not None])

class ClearCommand(StringCommand):
    """Class for clear command"""
    def __init__(self,
                 player_name: str,
                 item_name: Optional[str] = None,
                 amount: Optional[int] = None):
        """Clear command

        Args:
            player_name (str): Player name to apply command.
            item_name (str, optional): Name of the item to clear.
            Defaults to None (whole inventory).
            amount (int, optional): Max number to clear. Defaults to None.
        """
        self.player_name = player_name
        self.item_name = item_name
        self.amount = amount
        super().__init__(None)

    def get_command_text(self) -> str:
        command = f"clear {self.player_name}"
        command = self._compose_command(command, self.item_name, self.amount)

        return command

class GiveCommand(StringCommand):
    """Class for give command"""
    def __init__(self,
                 player_name: str,
                 item_name: str,
                 amount: int = 1,
                 tags: Optional[Dict[str, Any]] = None):
        """Give command

        Args:
            player_name (str): Player who needs to be given an item
            item_name (str): Item name
            amount (int, optional): Number of items to give. Defaults to 1.
            tags (Dict[str, Any], optional): Components dictionary. Defaults to None.
        """
        self.player_name = player_name
        self.item_name = item_name
        self.amount = amount
        self.tags = tags

        super().__init__(None)

    def get_command_text(self) -> str:
        command = f"give {self.player_name} {self.item_name}"
        if self.tags is not None:
            command += format_tags(self.tags)
        if self.amount > 1:
            command += f" {self.amount}"

        return command

class SetBlockCommand(StringCommand):
    """Class for setblock command"""
    def __init__(self,
                 x: Union[int, Tuple[str, int]],
                 y: Union[int, Tuple[str, int]],
                 z: Union[int, Tuple[str, int]],
                 block_name: str,
                 coordinate: Coordinate = None,
                 change: BlockChange = BlockChange.REPLACE,
                 state: Optional[Dict[str, Any]] = None,
                 tags: Optional[Dict[str, Any]] = None):
        """Setblock command

        Args:
            x (Union[int, Tuple[str, int]]): x coordinate
            y (Union[int, Tuple[str, int]]): y coordinate
            z (Union[int, Tuple[str, int]]): z coordinate
            block_name (str): Name of the block
            coordinate (Coordinate, optional): Type of the coordinate. Defaults to None.
            change (BlockChange, optional): Type of the change. Defaults to BlockChange.Replace.
            state (Optional[Dict[str, Any]], optional): State dictionary. Defaults to None.
            tags (Optional[Dict[str, Any]], optional): NBT-data dictionary. Defaults to None.
        """
        self.x = x
        self.y = y
        self.z = z
        self.block_name = block_name
        self.coordinate = coordinate
        self.change = change
        self.state = state
        self.tags = tags

        super().__init__(None)

    def get_command_text(self) -> str:
        coordinates = format_coordinates(self.x, self.y, self.z, self.coordinate)
        command = f"setblock {coordinates} {self.block_name}"

        if self.state is not None:
            command += format_state(self.state)

        if self.tags is not None:
            command += format_tags(self.tags)

        if self.change != BlockChange.REPLACE:
            command += f" {self.change}"

        return command

class FillCommand(StringCommand):
    """Class for fill command"""
    def __init__(self,
                 x1: Union[int, Tuple[str, int]],
                 y1: Union[int, Tuple[str, int]],
                 z1: Union[int, Tuple[str, int]],
                 x2: Union[int, Tuple[str, int]],
                 y2: Union[int, Tuple[str, int]],
                 z2: Union[int, Tuple[str, int]],
                 block_name: str,
                 coordinate: Coordinate = None,
                 block_handling: BlockHandling = None,
                 replace_block_name: Optional[str] = None):
        """Fill command

        Args:
            x1 (Union[int, Tuple[str, int]]): x1 coordinate
            y1 (Union[int, Tuple[str, int]]): y1 coordinate
            z1 (Union[int, Tuple[str, int]]): z1 coordinate
            x2 (Union[int, Tuple[str, int]]): x2 coordinate
            y2 (Union[int, Tuple[str, int]]): y2 coordinate
            z2 (Union[int, Tuple[str, int]]): z2 coordinate
            block_name (str): Name of the block
            coordinate (Coordinate, optional): Type of the coordinate. Defaults to None.
            block_handling (BlockHandling, optional): Type of the block handling. Defaults to None.
            replace_block_name (Optional[str], optional): Replace block name. Defaults to None.
        """
        self.x1 = x1
        self.y1 = y1
        self.z1 = z1
        self.x2 = x2
        self.y2 = y2
        self.z2 = z2
        self.block_name = block_name
        self.coordinate = coordinate
        self.block_handling = block_handling
        self.replace_block_name = replace_block_name

        super().__init__(None)

    def get_command_text(self) -> str:
        coordinates_start = format_coordinates(self.x1, self.y1, self.z1, self.coordinate)
        coordinates_end = format_coordinates(self.x2, self.y2, self.z2, self.coordinate)
        command = f"fill {coordinates_start} {coordinates_end} {self.block_name}"

        if self.block_handling is not None:
            command += f" {self.block_handling}"
            if self.block_handling == BlockHandling.REPLACE:
                if self.replace_block_name is None:
                    msg = "replace_block_name must be specified if block_handling is 'replace'"
                    raise ValueError(msg)
                command += f" {self.replace_block_name}"

        return command

class SummonCommand(StringCommand):
    """Class for summon command"""
    def __init__(self,
                 entity_name: str,
                 x: Optional[Union[int, Tuple[str, int]]] = None,
                 y: Optional[Union[int, Tuple[str, int]]] = None,
                 z: Optional[Union[int, Tuple[str, int]]] = None,
                 coordinate: Coordinate = None,
                 tags: Optional[Dict[str, Any]] = None):
        """Summon command

        Args:
            entity_name (str): Name of the entity
            x (Optional[Union[int, Tuple[str, int]]], optional): x coordinate. Defaults to None.
            y (Optional[Union[int, Tuple[str, int]]], optional): y coordinate. Defaults to None.
            z (Optional[Union[int, Tuple[str, int]]], optional): z coordinate. Defaults to None.
            coordinate (Coordinate, optional): Type of the coordinate. Defaults to None.
            tags (Optional[Dict[str, Any]], optional): NBT-data dictionary. Defaults to None.
        """
        self.entity_name = entity_name
        self.x = x
        self.y = y
        self.z = z
        self.coordinate = coordinate
        self.tags = tags

        super().__init__(None)

    def get_command_text(self) -> str:
        if self.x is not None and self.y is not None and self.z is not None:
            coordinates = format_coordinates(self.x, self.y, self.z, self.coordinate)
            command = f"summon {self.entity_name} {coordinates}"
        else:
            command = f"summon {self.entity_name}"

        if self.tags is not None:
            command += format_tags(self.tags)

        return command
