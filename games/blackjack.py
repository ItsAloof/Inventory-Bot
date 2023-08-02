import random
from typing import Text
from discord import Interaction
from nextcord import User, TextChannel, Embed
import nextcord
class Blackjack(nextcord.ui.View):
    children = []
    deck = {"Ace of Spades": 1, "Two of Spades": 2, "Three of Spades": 3, "Four of Spades": 4, "Five of Spades": 5, "Six of Spades": 6, "Seven of Spades": 7, "Eight of Spades": 8, "Nine of Spades": 9, "Ten of Spades": 10, "Jack of Spades": 10, "Queen of Spades": 10, "King of Spades": 10, "Ace of Hearts": 1, "Two of Hearts": 2, "Three of Hearts": 3, "Four of Hearts": 4, "Five of Hearts": 5, "Six of Hearts": 6, "Seven of Hearts": 7, "Eight of Hearts": 8, "Nine of Hearts": 9, "Ten of Hearts": 10, "Jack of Hearts": 10, "Queen of Hearts": 10, "King of Hearts": 10, "Ace of Clubs": 1, "Two of Clubs": 2, "Three of Clubs": 3, "Four of Clubs": 4, "Five of Clubs": 5, "Six of Clubs": 6, "Seven of Clubs": 7, "Eight of Clubs": 8, "Nine of Clubs": 9, "Ten of Clubs": 10, "Jack of Clubs": 10, "Queen of Clubs": 10, "King of Clubs": 10, "Ace of Diamonds": 1, "Two of Diamonds": 2, "Three of Diamonds": 3, "Four of Diamonds": 4, "Five of Diamonds": 5, "Six of Diamonds": 6, "Seven of Diamonds": 7, "Eight of Diamonds": 8, "Nine of Diamonds": 9, "Ten of Diamonds": 10, "Jack of Diamonds": 10, "Queen of Diamonds": 10, "King of Diamonds": 10}
    def __init__(self, user: User, wager: int, channel: TextChannel) -> None:
        super().__init__(timeout=600)
        self._user = user
        self._wager = wager
        self._player_hand = []
        self._dealer_hand = []
        self.game_deck = []
        self._won = False
        self.channel = channel
        for i in range(3):
            self.game_deck.append(self.deck.keys())
        random.shuffle(self.game_deck)

    def setup(self):
        pass

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
    def won(self):
        return self._won

    @property
    def get_players_hand(self) -> int:
        return sum(self._player_hand)

    @property
    def get_dealers_hand(self) -> int:
        return sum(self._dealer_hand)

    def start(self):
        pass

    def table(self) -> Embed:
        '''
        Returns the instance of the game table in the form of a Discord :class:`Embed`.
        '''
        embed = Embed(title="Blackjack", color=0x060606)
        embed.add_field(name="Dealers Hand", value=self.get_dealers_hand(), inline=False)
        embed.add_field(name="Players Hand", value=self.get_players_hand(), inline=False)
        return embed
        

    @nextcord.ui.button(label="Hit", style=nextcord.ButtonStyle.green)
    def hit(self, interaction: Interaction) -> int:
        index = random.randint(0, len(self.game_deck))
        card = self.game_deck.pop(index)
        if card == 1:
            card = card if sum(self._player_hand) + 11 > 21 else 11
        self._player_hand.append(card)
        

    @nextcord.ui.button(label="Stand", style=nextcord.ButtonStyle.red)
    def stand(self, interaction: nextcord.Interaction):
        while self.get_total(False) < 17:
            index = random.randint(0, len(self.game_deck))
            card = self.game_deck.pop(index)
            self._dealer_hand.append(card)
            self.hit(False)

    def isGameover(self, interaction: Interaction):
        if self.get_players_hand() > 21:
            self._won = False
            return True
        elif self.get_dealers_hand() > 21:
            self._won = True
            return True
        elif self.get_players_hand() == 21:
            self._won = True
            return True
        elif self.get_dealers_hand() == 21:
            self._won = False
            return True
        else:
            return False

    def gameover(self):
        if self.won:
            if self.wager:
                self.channel.send(f"{self.user.mention} won {self.wager} coins!")
            else:
                self.channel.send(f"{self.user.mention} won!")
        else:
            if self.wager:
                self.channel.send(f"{self.user.mention} lost {self.wager} coins!")
            else:
                self.channel.send(f"{self.user.mention} lost!")