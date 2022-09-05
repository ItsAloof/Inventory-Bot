from utils.item import Item


class Inventory():
    def __init__(self, owner: int, name: str, limit: int = None, items: list[Item] = None) -> None:
        self._owner: int = owner
        self._name: str = name
        self._items: list[Item] = items if items else []
        self._limit = limit
    
    @property
    def owner(self):
        return self._owner
    @property
    def items(self) -> list[Item]:
        return self._items
    
    @property
    def find_item(self, name: str) -> Item | None:
        for item in self._items:
            if item.name == name:
                return item
        return None
    
    @property
    def limit(self) -> int:
        return self._limit
    
    @limit.setter
    def limit(self, value: int) -> None:
        self._limit = value

    @staticmethod
    def load(data: dict) -> 'Inventory':
        return Inventory(owner=data["owner"], name=data["name"], limit=data["limit"], items=[Item.load(item) for item in data["items"]])
        
    def save(self) -> dict:
        return {
            "owner": self._owner,
            "items": [item.save() for item in self._items],
            "limit": self._limit,
            "name": self._name
        }
    
    def can_add_item(self) -> bool:
        if not self._limit:
            return True
        return len(self.items) < self._limit
    
    def add_item(self, item: Item) -> bool:
        if self.can_add_item():
            self._items.append(item)
            return True
        else:
            return False

    def remove_item(self, index: int) -> Item | None:
        if index - 1 < len(self.items):
            item = self.items[item - 1]
            self.items.remove(item)
            return item
        else:
            return None
            
    def clear(self) -> None:
        self._items.clear()
    
    def __str__(self) -> str:
        return f"**{self._name}'s Inventory**\n{len(self.items)}/{self.limit if self.limit else '∞'} Items:\n" + "\n".join([f"{item}" for item in self.items])
