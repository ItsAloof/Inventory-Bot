from discord import User
from utils.inventory import Inventory
from utils.item import Item
class GuildInventory():
    def __init__(self, guildId: int, guildName: str, inventory_size: int = None, items: list[Item] = []) -> None:
        self._inventory_limit = inventory_size
        self._guildId = guildId
        self._guildName = guildName
        self._inventories: list[Inventory] = items
    
    @property
    def guildId(self) -> int:
        return self._guildId
    
    @property
    def guildName(self) -> str:
        return self._guildName
    
    @property
    def inventories(self) -> list:
        return self._inventories
    
    @property
    def inventory_limit(self) -> int:
        return self._inventory_limit
    
    @inventory_limit.setter
    def inventory_limit(self, value: int) -> None:
        self._inventory_limit = value

    @staticmethod
    def load(data: dict) -> 'GuildInventory':
        return GuildInventory(data["guildId"], data["guildName"], data["inventory_limit"], [Inventory.load(inventory) for inventory in data["inventories"]])

    def save(self) -> dict:
        return {
            "guildId": self.guildId,
            "guildName": self.guildName,
            "inventories": [inventory.save() for inventory in self.inventories]
        }        

    def get_inventory(self, user: User) -> Inventory:
        for inventory in self._inventories:
            if inventory.owner == user:
                return inventory
        return self.create_inventory(owner=user)
    
    
    def create_inventory(self, owner: User) -> Inventory:
        inventory = Inventory(owner=owner.id, name=owner.name, limit=self.inventory_limit)
        self._inventories.append(inventory)
        return inventory

    def remove_inventory(self, owner: User) -> bool:
        inventory = self.get_inventory(owner)
        if inventory:
            self.inventories.remove(inventory)
            return True
        else:
            return False