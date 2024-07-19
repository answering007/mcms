"""Module providing enums for MCMS"""
from enum import Enum


class BlockChange(Enum):
    """Block change types"""
    REPLACE = "replace"
    DESTROY = "destroy"
    KEEP = "keep"

    def __str__(self):
        return self.value

class BlockHandling(Enum):
    """Block handling types"""
    HOLLOW = "hollow"
    OUTLINE = "outline"
    REPLACE = "replace"
    DESTROY = "destroy"
    KEEP = "keep"

    def __str__(self):
        return self.value

class Facing(Enum):
    """Block facing types"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    def __str__(self):
        return self.value

class Coordinate(Enum):
    """Coordinate types"""
    ABSOLUTE = ""
    RELATIVE = "~"
    LOCAL = "^"

    def __str__(self):
        return self.value
