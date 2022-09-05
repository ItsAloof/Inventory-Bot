class Item():
    def __init__(self, name: str, description: str, value: int):
        self._name = name
        self._description = description
        self._value = value

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        self._description = value
    
    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    @staticmethod
    def load(data: dict) -> 'Item':
        return Item(data["name"], data["description"], data["value"])
    
    def save(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value
        }

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\n".format(self.name, self.description, self.value)