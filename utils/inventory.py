from utils.item import Item


class Inventory():
    def __init__(self, owner: int, name: str, limit: int = None):
        self._owner: int = owner
        self._name: str = name
        self._items: list[Item] = []
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
        return Inventory(data["owner"], data["limit"], [Item.load(item) for item in data["items"]])
        
    def save(self) -> dict:
        return {
            "owner": self._owner,
            "items": [item.save() for item in self._items]
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
    
    def __str__(self) -> str:
        return f"{self._name}'s Inventory:\n{len(self.items)}/{self.limit}"
