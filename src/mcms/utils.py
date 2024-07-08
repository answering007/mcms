"""Utils for MCMS"""
import re
from typing import Any, Dict, Tuple, Union

from mcms.enums import Coordinate


def format_state(state: Dict[str, Any]) -> str:
    """Format state dictionary

    Args:
        state (Dict[str, Any]): State dictionary to format

    Returns:
        str: Formatted state dictionary

    Examples:
        >>> format_state({"string_value": "mystring", "int_value": 1, "bool_value": True})
        '[string_value=mystring, int_value=1, bool_value=True]'
    """
    return "[" + ", ".join([f"{key}={value}" for key, value in state.items()]) + "]"


def parse_state(block_data: str) -> Dict[str, Any]:
    """Parse state data from string (block_data)

    Args:
        block_data (str): Block data to parse

    Returns:
        Dict[str, Any]: State dictionary

    Examples:
        >>> parse_state("minecraft:chest[string_value=mystring, int_value=1, bool_value=True]")
        {'string_value': 'mystring', 'int_value': 1, 'bool_value': True}
    """
    def parse_primitive(value: str) -> Any:
        if value.isdecimal() or value.isdigit():
            return int(value)
        elif value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            return value

    # get state
    state_data = re.findall(r"\[(.*?)\]", block_data)
    state = {}
    if len(state_data) == 0:
        return state
    pairs = state_data[0].split(",")
    for pair in pairs:
        key, value = pair.split("=")
        state[key.strip()] = parse_primitive(value.strip())
    return state


def parse_block_data(block_data: str) -> Tuple[str, Dict[str, Any]]:
    """Parse block data from string (block_data)

    Args:
        block_data (str): Block data to parse

    Returns:
        Tuple[str, Dict[str, Any]]: Block namespace data and state dictionary

    Examples:
        >>> parse_block_data("minecraft:chest[facing=west,type=single,waterlogged=false]")
        ('minecraft:chest', {'facing': 'west', 'type': 'single', 'waterlogged': False})
    """
    # get block name
    namespace_data = block_data.split("[", 1)[0]

    # get state
    state_data = parse_state(block_data)
    return namespace_data, state_data


def format_tags(tags: Dict[str, Any]) -> str:
    """Format tags dictionary

    Args:
        tags (Dict[str, Any]): Tags dictionary to format

    Returns:
        str: Formatted tags dictionary

    Examples:
        >>> format_tags({"Enchantments": [{"id": "sharpness", "lvl": 999}, {"id": "unbreaking", "lvl": 999}]})
        '{Enchantments:[{id:"sharpness",lvl:999},{id:"unbreaking",lvl:999}]}'
    """
    def format_type(value) -> str:
        if isinstance(value, dict):
            return format_tags(value)
        elif isinstance(value, list):
            return "[" + ",".join([format_type(item) for item in value]) + "]"
        elif isinstance(value, str):
            return f'"{value}"'
        else:
            return str(value)
    result = "{" + ",".join([f"{key}:{format_type(value)}" for key,
                            value in tags.items()]) + "}"
    return result


def format_coordinates(x: Union[int, Tuple[str, int]],
                       y: Union[int, Tuple[str, int]],
                       z: Union[int, Tuple[str, int]],
                       coordinate: Coordinate = None) -> str:
    """Format coordinates

    Args:
        x (Union[int, Tuple[str, int]]): X coordinate (int or tuple of string("~", "^") and int)
        y (Union[int, Tuple[str, int]]): Y coordinate (int or tuple of string("~", "^") and int)
        z (Union[int, Tuple[str, int]]): Z coordinate (int or tuple of string("~", "^") and int)
        coordinate (Coordinate, optional): Coordinate type for all coordinates. Defaults to None.
        If None, all coordinates will be formatted according to the coordinate type value.

    Returns:
        str: Formatted coordinates

    Examples:
        >>> format_coordinates(("~", 0), ("^", 70), 161)
        '~0 ^70 161'
        >>> format_coordinates(196, 11, 57, Coordinate.RELATIVE)
        '~196 ~11 ~57'
    """
    def format_single(x: Tuple[str, int]) -> str:
        if isinstance(x, tuple):
            if coordinate is not None:
                return f"{coordinate}{x[1]}"
            else:
                return f"{x[0]}{x[1]}"
        elif coordinate is not None:
            return f"{coordinate}{x}"
        else:
            return str(x)

    return f"{format_single(x)} {format_single(y)} {format_single(z)}"
