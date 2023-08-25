from operator import inv
import random
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption, Interaction, Permissions
from main import InventoryBot
from games.rps import RPS, RPSView
from games.blackjack import Blackjack, BlackjackView

class Games(commands.Cog):
    def __init__(self, bot: InventoryBot) -> None:
        self.bot = bot

    @nextcord.slash_command(name="rps", description="Play a game of Rock, Paper, Scissors against a bot")
    async def rps(self, 
                  interaction: Interaction, 
                  wager: float = SlashOption(name="bet", description="The amount of money you wish to bet", required=True), 
                  best_of: int = SlashOption(name="rounds", description="How many rounds to play best of", required=False, default=1)):

        inventory = self.bot.get_user_inventory(interaction.guild_id, interaction.user)
        guild = self.bot.get_guild_inventory(interaction.guild_id)
        game = RPS(inventory, guild, wager, self.bot.pgsql, best_of)
        await interaction.send(view=RPSView(timeout=300, rps_game=game))

    
    @nextcord.slash_command(name="coinflip", description="Flip a coin.", guild_ids=[1001667368801550439])
    async def coinflip(self, interaction: Interaction,
    choice: int = SlashOption(name="choice", description="Your choice", required=True, choices={"heads": 0, "tails": 1}),
    bet: int = SlashOption(name="bet", description="How much to bet", required=False, default=0)):
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(interaction.user)
            coin = random.randint(0, 1)
            if coin == choice:
                inventory.deposit(bet)
                msg = f"You won! It was " + ("heads. " if choice == 0 else "tails. ") if bet == 0 else f"You won {guild.currency}{bet}! It was " + "heads" if choice == 0 else "tails"
                await interaction.response.send_message(msg)
            else:
                inventory.withdraw(bet)
                msg = f"You lost! It was " + "heads. " if coin == 0 else "tails. " if bet == 0 else f"You lost {guild.currency}{bet}! It was " + "heads" if choice == 0 else "tails"
                await interaction.response.send_message(msg)
            self.bot.save_inventories()
            
    @nextcord.slash_command(name="blackjack", description="Play a game of blackjack", guild_ids=[1001667368801550439])
    async def blackjack(self, interaction: Interaction, wager: float = SlashOption(name="bet", description="How much you want to bet on the game", required=True)):
        
        inventory = self.bot.get_user_inventory(interaction.guild_id, interaction.user)
        
        if inventory.balance < wager:
            await interaction.send("You cannot afford this bet!", ephemeral=True)
            return
        
        guild = self.bot.get_guild_inventory(interaction.guild_id)
        game = Blackjack(inventory, guild, wager, self.bot.pgsql)
        await interaction.send(view=BlackjackView(blackjack=game), embed=game.game_embed())

def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(Games(bot))
