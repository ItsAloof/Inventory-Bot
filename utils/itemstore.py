from utils.guild import GuildInventory
from utils.item import Item
from typing import List

class Itemstore():
    def __init__(self, guild: GuildInventory, items: List[Item] = None) -> None:
        self._items = items if items is not None else []
        
    
    def get_item(self, id: str) -> Item | None:
        for item in self._items:
            if item.id == id:
                return item
        
        return None
    
    
    def remove_item(self, id: str) -> bool:
        ...
    
    
    