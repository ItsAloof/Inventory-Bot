from decimal import Decimal
from typing import Optional, Union
import random
from nextcord.emoji import Emoji
from nextcord.enums import ButtonStyle
from nextcord.interactions import Interaction
from nextcord.partial_emoji import PartialEmoji
from utils.guild import GuildInventory
from utils.inventory import Inventory
from utils.pgsql import Query
from .game import Game, GameState
import nextcord
from enum import Enum

class RPSHand(Enum):
    ROCK = 'Rock'
    PAPER = 'Paper'
    SCISSORS = 'Scissors'

class RPSButton(nextcord.ui.Button):
    def __init__(self, *, 
                 style: ButtonStyle = ButtonStyle.secondary, 
                 label: str | None = None, 
                 disabled: bool = False, 
                 custom_id: str | None = "rps-inventory-bot", 
                 url: str | None = None, 
                 emoji: str | Emoji | PartialEmoji | None = None, 
                 row: int | None = 1,
                 type: RPSHand) -> None:
        label = type
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)

        
    async def callback(self, interaction: Interaction) -> None:
        assert self.view is not None
        
        self.view: RPSView
        game = self.view._game
        
        game._player_hand = self.type

        game.bots_turn()
        game.game_over()

class RPSView(nextcord.ui.View):
    def __init__(self, *, timeout: float | None = 180, auto_defer: bool = True, rps_game: 'RPS') -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self._game = rps_game
        
        self.rock = RPSButton(ButtonStyle.blurple, custom_id=f"{RPSHand.ROCK}-rps-button", type=RPSHand.ROCK)
        self.paper = RPSButton(ButtonStyle.blurple, custom_id=f"{RPSHand.PAPER}-rps-button", type=RPSHand.PAPER)
        self.scissors = RPSButton(ButtonStyle.blurple, custom_id=f"{RPSHand.SCISSORS}-rps-button", type=RPSHand.SCISSORS)

        self.add_item(self.rock)
        self.add_item(self.paper)
        self.add_item(self.scissors)

        

class RPS(Game):
    def __init__(self, player: Inventory, guild: GuildInventory, wager: Decimal, sql: Query, bestof: int) -> None:
        super().__init__(player, guild, wager, sql)
        self._bestof = bestof
        self._bot_hand = None
        self._player_hand = None
        
    def bots_turn(self):
        rps_lookup = [RPSHand.ROCK, RPSHand.PAPER, RPSHand.SCISSORS]
        n = random.randint(0, 2)
        
    
    def game_over(self) -> bool:
        if self._bot_hand is None or self._player_hand is None:
            return False
        
        if type(self._bot_hand) is not RPSHand or type(self._player_hand) is not RPSHand:
            return False
        
        if self._bot_hand == self._player_hand:
            self.gamestate = GameState.DRAW
            return True
        
        self.gamestate = GameState.LOST
        if self._bot_hand == RPSHand.ROCK and self._player_hand == RPSHand.SCISSORS:
            return True
        if self._bot_hand == RPSHand.PAPER and self._player_hand == RPSHand.ROCK:
            return True
        if self._bot_hand == RPSHand.SCISSORS and self._player_hand == RPSHand.PAPER:
            return True
        
        self.gamestate = GameState.WON
        self._winner = True
        return True