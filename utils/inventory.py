from utils.item import Item


class Inventory():
    def __init__(self, owner: int, name: str, limit: int = None, items: list[Item] = None, starting_balance: int = 0) -> None:
        self._owner: int = owner
        self._name: str = name
        self._items: list[Item] = items if items else []
        self._limit = limit
        self._balance = starting_balance
    
    @property
    def owner(self) -> int:
        """The owner of the inventory"""
        return self._owner
    @property
    def items(self) -> list[Item]:
        return self._items

    @property
    def balance(self) -> int:
        """The balance for the player within the guild"""
        return self._balance
    
    @balance.setter
    def balance(self, value: int) -> None:
        self._balance = value

    def deposit(self, amount: int) -> bool:
        if amount > 0:
            self._balance += amount
            return True
        return False
    
    def withdraw(self, amount: int) -> bool:
        if amount > 0 and amount <= self._balance:
            self._balance -= amount
            return True
        return False
    
    def format_balance(self, currency: str) -> str:
        """Returns a formatted string of a users balance"""
        return f"{currency}" + "{:,}".format(self.balance)
    
    @property
    def find_item(self, name: str) -> Item | None:
        """
        Finds an item in the inventory by name
        
        Parameters
        ----------
        name: :class:`str`
            The name of the item to find
        """
        for item in self._items:
            if item.name == name:
                return item
        return None
    
    @property
    def limit(self) -> int:
        """The maximum number of items the inventory can hold"""
        return self._limit
    
    @limit.setter
    def limit(self, value: int) -> None:
        self._limit = value

    @staticmethod
    def load(data: dict) -> 'Inventory':
        """Loads an inventory from json data"""
        return Inventory(owner=data["owner"], name=data["name"], limit=data["limit"], items=[Item.load(item) for item in data["items"]], starting_balance=data["balance"])
        
    def save(self) -> dict:
        """Saves the inventory to json data"""
        return {
            "owner": self._owner,
            "items": [item.save() for item in self._items],
            "limit": self._limit,
            "name": self._name,
            "balance": self._balance
        }
    
    def can_add_item(self) -> bool:
        """Checks if the inventory can add an item"""
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
