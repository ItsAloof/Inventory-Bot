import random
from nextcord import User
class Blackjack():
    deck = {"Ace of Spades": 1, "Two of Spades": 2, "Three of Spades": 3, "Four of Spades": 4, "Five of Spades": 5, "Six of Spades": 6, "Seven of Spades": 7, "Eight of Spades": 8, "Nine of Spades": 9, "Ten of Spades": 10, "Jack of Spades": 10, "Queen of Spades": 10, "King of Spades": 10, "Ace of Hearts": 1, "Two of Hearts": 2, "Three of Hearts": 3, "Four of Hearts": 4, "Five of Hearts": 5, "Six of Hearts": 6, "Seven of Hearts": 7, "Eight of Hearts": 8, "Nine of Hearts": 9, "Ten of Hearts": 10, "Jack of Hearts": 10, "Queen of Hearts": 10, "King of Hearts": 10, "Ace of Clubs": 1, "Two of Clubs": 2, "Three of Clubs": 3, "Four of Clubs": 4, "Five of Clubs": 5, "Six of Clubs": 6, "Seven of Clubs": 7, "Eight of Clubs": 8, "Nine of Clubs": 9, "Ten of Clubs": 10, "Jack of Clubs": 10, "Queen of Clubs": 10, "King of Clubs": 10, "Ace of Diamonds": 1, "Two of Diamonds": 2, "Three of Diamonds": 3, "Four of Diamonds": 4, "Five of Diamonds": 5, "Six of Diamonds": 6, "Seven of Diamonds": 7, "Eight of Diamonds": 8, "Nine of Diamonds": 9, "Ten of Diamonds": 10, "Jack of Diamonds": 10, "Queen of Diamonds": 10, "King of Diamonds": 10}
    def __init__(self, user: User, wager: int) -> None:
        self._user = user
        self._wager = wager
        self._player_hand = []
        self._dealer_hand = []
        self.game_deck = []
        for i in range(3):
            self.game_deck.append(self.deck.keys())
        random.shuffle(self.game_deck)

    @property
    def user(self):
        return self._user
    
    @property
    def wager(self):
        return self._wager

    @property
    def player_hand(self):
        return self._player_hand

    @property
    def dealer_hand(self):
        return self._dealer_hand

    @property
    def get_total(self, player: bool) -> int:
        total = 0
        if player:
            for card in self._player_hand:
                total += self.deck[card]
        else:
            for card in self._dealer_hand:
                total += self.deck[card]
        return total

    def start(self):
        pass

    def hit(self, player: bool) -> int:
        index = random.randint(0, len(self.game_deck))
        card = self.game_deck.pop(index)
        if player:
            self._player_hand.append(card)
            if self.is_blackjack(True):
                self.gameover()
            return self.deck[card]

    def stand(self):
        while self.get_total(False) < 17:
            self.hit(False)
        self.gameover()


    def is_blackjack(self, player: bool) -> bool:
        if player:
            return self.get_total(True) == 21
        else:
            return self.get_total(False) == 21