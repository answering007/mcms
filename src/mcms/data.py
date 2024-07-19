"""Data classes for Minecraft"""
from dataclasses import dataclass
from typing import Any, Dict, List

from mcms.enums import Facing
from mcms.utils import format_state, parse_block_data


@dataclass(kw_only=True)
class Location:
    """Minecraft location"""
    world: str = "world"
    x: float
    y: float
    z: float
    yaw: float = 0
    pitch: float = 0

    def get_facing(self) -> Facing:
        """Get facing

        Returns:
            Facing: Facing
        """
        levels = {
            (-45, 45): Facing.SOUTH,
            (45, 135): Facing.WEST,
            (135, 180): Facing.NORTH,
            (-180, -135):Facing.NORTH,
            (-135, -45): Facing.EAST}

        for borders, facing in levels.items():
            if self.yaw > borders[0] and self.yaw <= borders[1]:
                return facing
        return Facing.NORTH

    def to_request_data(self) -> Dict[str, Any]:
        """Convert location to request data

        Returns:
            Dict[str, Any]: Request data dictionary
        """
        return {"worldName": self.world,
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "yaw": self.yaw,
                "pitch": self.pitch}

    @classmethod
    def from_request_data(cls, data: Dict[str, Any]) -> "Location":
        """Create location from request data

        Args:
            data (Dict[str, Any]): Request data

        Returns:
            Location: Location
        """
        return cls(
            world=data["worldName"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            yaw=data["yaw"],
            pitch=data["pitch"])

@dataclass(kw_only=True)
class NamespacedKey:
    """Minecraft namespaced key"""
    namespace: str = "minecraft"
    name: str

    def get_full_name(self) -> str:
        """Get fill name

        Returns:
            str: namespace:name

        Examples:
            >>> NamespacedKey("minecraft", "chest").get_full_name()
            'minecraft:chest'
        """
        return f"{self.namespace}:{self.name}"

@dataclass
class Enchantment(NamespacedKey):
    """Minecraft enchantment"""
    level: int

    def to_request_data(self) -> Dict[str, Any]:
        """Convert enchantment to request data

        Returns:
            Dict[str, Any]: Request data dictionary
        """
        return {"key": self.name,
                "nameSpace": self.namespace,
                "level": self.level}

    @classmethod
    def from_request_data(cls, data: Dict[str, Any]) -> "Enchantment":
        """Create enchantment from request data

        Args:
            data (Dict[str, Any]): Request data

        Returns:
            Enchantment: Enchantment
        """
        return cls(
            namespace=data["nameSpace"],
            name=data["key"],
            level=data["level"])

@dataclass(kw_only=True)
class ItemStack(NamespacedKey):
    """Minecraft item stack"""
    index: int = -1
    count: int
    enchantments: List[Enchantment] = None

    def to_request_data(self) -> Dict[str, Any]:
        """Convert item stack to request data

        Returns:
            Dict[str, Any]: Request data dictionary
        """
        # enchantments
        enchantments = [] if self.enchantments is None else [e.to_request_data()
                                                             for e in self.enchantments]

        return {"materialKey": self.name,
                "materialNameSpaceKey": self.namespace,
                "Index": self.index,
                "Count": self.count,
                "enchantments": enchantments}

    @classmethod
    def from_request_data(cls, data: Dict[str, Any]) -> "ItemStack":
        """Create item stack from request data

        Args:
            data (Dict[str, Any]): Request data

        Returns:
            ItemStack: Item stack
        """
        enchantments = []
        if "enchantments" in data:
            enchantments = [Enchantment.from_request_data(enchantment)
                            for enchantment in data["enchantments"]]

        return cls(
            name=data["materialKey"],
            namespace=data["materialNameSpaceKey"],
            index=data["Index"],
            count=data["Count"],
            enchantments=enchantments)

@dataclass
class Block(NamespacedKey):
    """Minecraft block"""
    location: Location
    state: Dict[str, Any] = None
    inventory: List[ItemStack] = None

    def get_block_data_as_string(self) -> str:
        """Get block data as string

        Returns:
            str: Gets a string, which when passed into a method such as
            Server.createBlockData(java.lang.String)
            will unambiguously recreate this instance.

        Examples:
            >>> Block("minecraft", "chest", Location(world="world", x=161, y=66, z=119), {"facing":
            ... "west", "type": "single", "waterlogged": False}).get_block_data_as_string()
            'minecraft:chest[facing=west, type=single, waterlogged=False]'
        """
        result = self.get_full_name()
        if self.state is not None:
            result += format_state(self.state)
        return result

    def to_request_data(self) -> Dict[str, Any]:
        """Convert block to request data

        Returns:
            Dict[str, Any]: Request data dictionary
        """
        # Block data
        block_data = f"{self.namespace}:{self.name}"
        if self.state is not None:
            block_data += format_state(self.state)

        # items
        items = [] if self.inventory is None else [i.to_request_data() for i in self.inventory]

        # Location and block data
        return {"locationData": self.location.to_request_data(),
                "blockData": block_data,
                "items": items}

@dataclass
class GetBlockResponse:
    """Get block response"""
    success: bool
    exception: str = None
    result: Block = None

    @classmethod
    def from_request_response_data(cls, block_request: Location,
                block_response: Dict[str, Any]) -> "GetBlockResponse":
        """Parse get block response from request and response data

        Args:
            block_request (Location): Location of block
            block_response (Dict[str, Any]): Response data

        Returns:
            GetBlockResponse: Get block response
        """
        block = None
        if block_response["success"]:
            block_full_name, state = parse_block_data(block_response["result"])
            parts = block_full_name.split(":", 2)

            inventory = []
            if "items" in block_response:
                inventory = [ItemStack.from_request_data(item) for item in block_response["items"]]

            block = Block(
                namespace=parts[0],
                name=parts[1],
                location=block_request,
                state=state,
                inventory=inventory)

        return cls(
            success=block_response["success"],
            exception=block_response.get("exception", None),
            result=block
        )

@dataclass
class Player:
    """Minecraft player"""
    name: str
    is_online: bool
    uuid: str
    address: str
    location: Location
    health: float
    items: List[ItemStack]

    @classmethod
    def from_request_data(cls, data: Dict[str, Any]) -> "Player":
        """Create player from request data

        Args:
            data (Dict[str, Any]): Request data

        Returns:
            Player: Player
        """
        is_online = data["isOnline"]

        return cls(name=data["playerName"],
                   is_online=is_online,
                   uuid=data["UUID"],
                   location=Location.from_request_data(data["location"]) if is_online else None,
                   health=data["health"] if is_online else None,
                   address=data["address"] if is_online else None,
                   items=[ItemStack.from_request_data(item)
                          for item in data["items"]] if is_online else None)
