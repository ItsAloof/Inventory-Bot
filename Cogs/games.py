from operator import inv
import random
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption, Interaction, Permissions
from main import InventoryBot
from games.rps import RPS, RPSView

class Games(commands.Cog):
    def __init__(self, bot: InventoryBot) -> None:
        self.bot = bot

    @nextcord.slash_command(name="rps", description="Play a game of Rock, Paper, Scissors against a bot")
    async def rps(self, 
                  interaction: Interaction, 
                  wager: float = SlashOption(name="bet", description="The amount of money you wish to bet", required=True), 
                  best_of: int = SlashOption(name="rounds", description="How many rounds to play best of", required=False, default=1)):
        
        inventory = self.bot.get_user_inventory(interaction.guild_id, interaction.user)
        
        if inventory.balance < wager:
            await interaction.send("You cannot afford this wager!", ephemeral=True)
            return
        
        guild = self.bot.get_guild_inventory(interaction.guild_id)
        game = RPS(inventory, guild, wager, self.bot.pgsql, best_of)
        await interaction.send(view=RPSView(timeout=300, rps_game=game), embed=game.game_embed())

    
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

def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(Games(bot))
