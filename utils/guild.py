from discord import User
from utils.inventory import Inventory
from utils.item import Item
class GuildInventory():
    def __init__(self, guildId: int, guildName: str, inventory_size: int = None, items: list[Item] = None, currency: str = "$") -> None:
        self._inventory_limit = inventory_size
        self._guildId = guildId
        self._guildName = guildName
        self._inventories: list[Inventory] = items if items else []
        self._currency = currency
    
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
        for inventory in self._inventories:
            inventory.limit = value
    
    @property
    def currency(self) -> str:
        return self._currency

    @currency.setter
    def currency(self, value: str) -> None:
        self._currency = value

    @staticmethod
    def load(data: dict) -> 'GuildInventory':
        return GuildInventory(data["guildId"], data["guildName"], data["inventory_limit"], [Inventory.load(inventory) for inventory in data["inventories"]], data["currency"])

    def save(self) -> dict:
        return {
            "guildId": self.guildId,
            "guildName": self.guildName,
            "currency": self.currency,
            "inventories": [inventory.save() for inventory in self._inventories] if self._inventories else [],
            "inventory_limit": self.inventory_limit
        }        

    def get_inventory(self, user: User) -> Inventory:
        for inventory in self._inventories:
            if inventory.owner == user.id:
                return inventory
        print(f"Could not find inventory for {user.name} ({user.id})")
        inventory = self.create_inventory(owner=user)
        return inventory
    
    
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

    def __str__(self) -> str:
        return f"Guild: {self._guildName} ({self._guildId}) - Inventories: {[inv for inv in self._inventories]}"