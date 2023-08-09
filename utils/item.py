import json
from uuid import UUID
import uuid

class Item():
    def __init__(self, name: str, description: str, value: float, currency: str = '$', id: UUID = None) -> None:
        self._name = name
        self._description = description
        self._value = value
        self._id = id if id is not None else uuid.uuid4()
        self._currency = currency

    @property
    def name(self) -> str:
        """The items name"""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value: str):
        self._id = value
    
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

    @staticmethod
    def load(data: dict, currency: str) -> 'Item':
        return Item(data["name"], data["description"], data["value"], currency, UUID(data["id"]))
    
    def toJSON(self):
        return json.dumps(self, default= lambda o: o.__dict__, sort_keys=True)
    
    def save(self) -> dict:
        return {
            "name": self._name,
            "description": self._description,
            "value": self._value,
            "id": str(self._id)
        }
    
    def _is_valid_operand(self, other: object):
        return (hasattr(other, "id"))
    
    def __eq__(self, other: object) -> bool:
        if self._is_valid_operand(other):
            return other.id == self.id

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return f"{self._name}: {self._description}\nValue: {self._currency}" + "{:,.2f}".format(self._value)