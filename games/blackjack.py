from decimal import Decimal
import random
from typing import Optional, Text, Union
from discord import Interaction
from nextcord import User, TextChannel, Embed
import nextcord
from nextcord.emoji import Emoji
from nextcord.enums import ButtonStyle
from nextcord.interactions import Interaction
from nextcord.partial_emoji import PartialEmoji
from games.game import GameState, Game
from utils.guild import GuildInventory
from utils.inventory import Inventory
from utils.pgsql import Query
from typing import List
import datetime

class BlackjackView(nextcord.ui.View):
    def __init__(self, *, timeout: float | None = 300, auto_defer: bool = True, blackjack: 'Blackjack') -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.game = blackjack
        self.hit_btn = HitButton(game=blackjack)
        self.stand_btn = StandButton(game=blackjack)
        self.add_item(self.hit_btn)
        self.add_item(self.stand_btn)

class StandButton(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = "Stand", disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 2, game: 'Blackjack') -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.game = game
        
    
    async def callback(self, interaction: Interaction) -> None:
        assert self.view is not None
        self.view: BlackjackView
        
        self.view.hit_btn.disabled = True
        self.view.stand_btn.disabled = True
        
        self.game._players_turn = False
        
        self.game.game_over()
        self.game.payout()
        await interaction.response.edit_message(view=self.view, embed=self.game.game_embed())
    
    
class HitButton(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.green, label: str | None = "Hit", disabled: bool = False, custom_id: str | None = "blackjack-hit-btn", url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 2, game: 'Blackjack') -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.game = game
        
        
    async def callback(self, interaction: Interaction) -> None:
        self.game.hit()
        self.win_msg = None
        
        if not self.game.game_over():
            await interaction.response.edit_message(view=self.view, embed=self.game.game_embed())
    
class Blackjack(Game):
    children = []
    deck = {
    "Ace of Spades": {"emoji": ":spades:", "value": 1},
    "2 of Spades": {"emoji": ":spades:", "value": 2},
    "3 of Spades": {"emoji": ":spades:", "value": 3},
    "4 of Spades": {"emoji": ":spades:", "value": 4},
    "5 of Spades": {"emoji": ":spades:", "value": 5},
    "6 of Spades": {"emoji": ":spades:", "value": 6},
    "7 of Spades": {"emoji": ":spades:", "value": 7},
    "8 of Spades": {"emoji": ":spades:", "value": 8},
    "9 of Spades": {"emoji": ":spades:", "value": 9},
    "10 of Spades": {"emoji": ":spades:", "value": 10},
    "Jack of Spades": {"emoji": ":spades:", "value": 10},
    "Queen of Spades": {"emoji": ":spades:", "value": 10},
    "King of Spades": {"emoji": ":spades:", "value": 10},
    
    "Ace of Hearts": {"emoji": ":hearts:", "value": 1},
    "2 of Hearts": {"emoji": ":hearts:", "value": 2},
    "3 of Hearts": {"emoji": ":hearts:", "value": 3},
    "4 of Hearts": {"emoji": ":hearts:", "value": 4},
    "5 of Hearts": {"emoji": ":hearts:", "value": 5},
    "6 of Hearts": {"emoji": ":hearts:", "value": 6},
    "7 of Hearts": {"emoji": ":hearts:", "value": 7},
    "8 of Hearts": {"emoji": ":hearts:", "value": 8},
    "9 of Hearts": {"emoji": ":hearts:", "value": 9},
    "10 of Hearts": {"emoji": ":hearts:", "value": 10},
    "Jack of Hearts": {"emoji": ":hearts:", "value": 10},
    "Queen of Hearts": {"emoji": ":hearts:", "value": 10},
    "King of Hearts": {"emoji": ":hearts:", "value": 10},
    
    "Ace of Clubs": {"emoji": ":clubs:", "value": 1},
    "2 of Clubs": {"emoji": ":clubs:", "value": 2},
    "3 of Clubs": {"emoji": ":clubs:", "value": 3},
    "4 of Clubs": {"emoji": ":clubs:", "value": 4},
    "5 of Clubs": {"emoji": ":clubs:", "value": 5},
    "6 of Clubs": {"emoji": ":clubs:", "value": 6},
    "7 of Clubs": {"emoji": ":clubs:", "value": 7},
    "8 of Clubs": {"emoji": ":clubs:", "value": 8},
    "9 of Clubs": {"emoji": ":clubs:", "value": 9},
    "10 of Clubs": {"emoji": ":clubs:", "value": 10},
    "Jack of Clubs": {"emoji": ":clubs:", "value": 10},
    "Queen of Clubs": {"emoji": ":clubs:", "value": 10},
    "King of Clubs": {"emoji": ":clubs:", "value": 10},
    
    "Ace of Diamonds": {"emoji": ":diamonds:", "value": 1},
    "2 of Diamonds": {"emoji": ":diamonds:", "value": 2},
    "3 of Diamonds": {"emoji": ":diamonds:", "value": 3},
    "4 of Diamonds": {"emoji": ":diamonds:", "value": 4},
    "5 of Diamonds": {"emoji": ":diamonds:", "value": 5},
    "6 of Diamonds": {"emoji": ":diamonds:", "value": 6},
    "7 of Diamonds": {"emoji": ":diamonds:", "value": 7},
    "8 of Diamonds": {"emoji": ":diamonds:", "value": 8},
    "9 of Diamonds": {"emoji": ":diamonds:", "value": 9},
    "10 of Diamonds": {"emoji": ":diamonds:", "value": 10},
    "Jack of Diamonds": {"emoji": ":diamonds:", "value": 10},
    "Queen of Diamonds": {"emoji": ":diamonds:", "value": 10},
    "King of Diamonds": {"emoji": ":diamonds:", "value": 10}
}

    def __init__(self, player: Inventory, guild: GuildInventory, wager: float, sql: Query) -> None:
        super().__init__(player, guild, wager, sql)
        self._player_hand = []
        self._dealer_hand = []
        self.game_deck = []
        self._players_turn = True
        self._dealer_bj = False
        self._player_bj = False
        
        for i in range(3):
            self.game_deck.extend(list(self.deck.keys()))
        random.shuffle(self.game_deck)

        self.setup()

    def setup(self):
        self._player_hand.extend([self.draw_card(), self.draw_card()])
        self._dealer_hand.append(self.draw_card())
    
    def draw_card(self):
        return self.game_deck.pop()
        
    def suit_to_emoji(self, card: str):
        return self.deck.get(card)['emoji']
    
    def get_card_value(self, card: str):
        return self.deck.get(card)['value']
    
    def sum_cards(self, hand: List[str]):
        return sum([self.get_card_value(card) for card in hand])
    
    def dealers_turn(self):
        while(self.sum_cards(self.dealer_hand) < 17):
            self.hit(False)
        
    def hit(self, player: bool = True):
        if player:
            self.player_hand.append(self.draw_card())
        else:
            self.dealer_hand.append(self.draw_card())
        
    
    def game_over(self) -> bool:
        player_value = self.sum_cards(self.player_hand)
        
        if player_value > 21:
            self.gamestate = GameState.LOST
            return True
        
        if player_value == 21:
            self._player_bj = True
            self.wager *= 2
            self.hit(False)
            if self.sum_cards(self.dealer_hand) == 21:
                self.gamestate = GameState.DRAW
                self._dealer_bj = True
                return True
            else:
                self.gamestate = GameState.WON
                return True
        
        
        if self._players_turn:
            return False

        self.dealers_turn()
        dealer_value = self.sum_cards(self.dealer_hand)
        
        if dealer_value == 21:
            self.gamestate = GameState.LOST
            self._dealer_bj = True
            return True
        
        if dealer_value > 21:
            self.gamestate = GameState.WON
            return True
        
        if dealer_value > player_value:
            self.gamestate = GameState.LOST
            return True
        
        if dealer_value == player_value:
            self.gamestate = GameState.DRAW
            return True
        
        if player_value < 21 and player_value > dealer_value:
            self.gamestate = GameState.WON
            return True
        
        return False

    @property
    def player_hand(self):
        return self._player_hand

    @property
    def dealer_hand(self):
        return self._dealer_hand

    def start(self):
        pass

    def game_embed(self, timestamp=None):
        # Create an embed instance
        embed = Embed(title="Blackjack Game", color=self.gamestate.value)

        # Set the timestamp (if provided, otherwise use current time)
        if timestamp is None:
            timestamp = datetime.datetime.now()
        embed.timestamp = timestamp

        # Add player's hand information using emojis and card values
        player_hand_string = " ".join([f"{self.deck[card]['value']}{self.deck[card]['emoji']}" for card in self.player_hand])
        player_hand_value = sum([self.deck[card]["value"] for card in self.player_hand])
        embed.add_field(name="Your Hand", value=f"{player_hand_string}\nTotal Value: {player_hand_value}", inline=False)

        # Add dealer's upcard information using emojis and card values
        dealer_hand_string = " ".join([f"{self.deck[card]['value']}{self.deck[card]['emoji']}" for card in self.dealer_hand])
        embed.add_field(name="Dealer's Hand", value=f"{dealer_hand_string}", inline=False)
        
        if self.gamestate == GameState.WON:
            name = "Blackjack! You win!" if self._player_bj else "Congrats you win!"
            value = f"You win {Inventory.format_money(self.guild.currency, self.wager)}"
            embed.add_field(name=name, value=value, inline=False)
        elif self.gamestate == GameState.LOST:
            name = "The dealer had Blackjack! You lose!" if self._dealer_bj else "The dealer has a better hand, you lose"
            value = f"You lose {Inventory.format_money(self.guild.currency, self.wager)}"
            embed.add_field(name=name, value=value, inline=False)
        elif self.gamestate == GameState.DRAW:
            name = "You and the dealer have the same hand, its a draw!"
            value = "Your wager has been returned to you"
            embed.add_field(name=name, value=value, inline=False)

        return embed