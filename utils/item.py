import json

class Item():
    def __init__(self, name: str, description: str, value: int, currency: str) -> None:
        self._name = name
        self._description = description
        self._value = value
        self._currency = currency

    @property
    def name(self) -> str:
        """The items name"""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
    
    @property
    def description(self) -> str:
        """The items description"""
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        self._description = value
    
    @property
    def value(self) -> str:
        """The items value"""
        return self._value
    
    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    @property
    def currency(self) -> str:
        """The items currency"""
        return self._currency
    
    @currency.setter
    def currency(self, value: str) -> None:
        self._currency = value

    @staticmethod
    def load(data: dict) -> 'Item':
        return Item(data["name"], data["description"], data["value"], data["currency"])
    
    def toJSON(self):
        return json.dumps(self, default= lambda o: o.__dict__, sort_keys=True)
    
    def save(self) -> dict:
        return {
            "name": self._name,
            "description": self._description,
            "value": self._value,
            "currency": self._currency
        }

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return f"{self._name}: {self._description}\nValue: {self._currency}" + "{:,}".format(self._value)