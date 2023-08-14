from utils.guild import GuildInventory
from utils.inventory import Inventory
from utils.item import Item
from typing import List

class Itemstore():
    def __init__(self, guild: GuildInventory, items: List[Item] = None) -> None:
        self._items = items if items is not None else []
        

    @property
    def items(self):
        return self._items
    
    @items.setter
    def items(self, value: List[Item]):
        self._items = value
    
    def get_item(self, id: str) -> Item | None:
        for item in self._items:
            if item.id == id:
                return item
        
        return None
    
    def buy_item(self, item: Item, user: Inventory) -> bool:
        item = item.load(**item.save())
        if not user.can_add_item():
            return False
        
        if user.balance > item.value:
            return False
        
        user.withdraw(item.value)
        user.add_item(item)
        
    def add_item(self, item: Item):
        self._items.append(item)
        
    def remove_item(self, id: str) -> bool:
        item = self.get_item(id)
        if item is None:
            return False
        
        self._items.remove(item)
        return True
    
    
    