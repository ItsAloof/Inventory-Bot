from operator import inv
import random
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption, Interaction, Permissions
from main import InventoryBot

class Games(commands.Cog):
    def __init__(self, bot: InventoryBot) -> None:
        self.bot = bot

    @nextcord.slash_command(name="rps", description="Play rock paper scissors", guild_ids=[1001667368801550439])
    async def rps(self, interaction: Interaction, 
    choice: str = SlashOption(name="choice", description="Your choice", required=True, choices=["rock", "paper", "scissors"]),
    bet: int = SlashOption(name="bet", description="How much to bet", required=False, default=0)):
        rpslookup = {0: "rock", 1: "paper", 2: "scissors"}
        botchoice = rpslookup[random.randint(0, 2)]
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(interaction.user)
            if self.won_rps(choice, botchoice):
                inventory.deposit(bet)
                msg = f"You won! You chose {choice} and the bot chose {botchoice}" if bet == 0 else f"You won {guild.currency}{bet}! You chose {choice} and the bot chose {botchoice}"
                await interaction.response.send_message(msg)
            else:
                inventory.withdraw(bet)
                msg = f"You lost! You chose {choice} and the bot chose {botchoice}" if bet == 0 else f"You lost {guild.currency}{bet}! You chose {choice} and the bot chose {botchoice}"
                await interaction.response.send_message(msg)
            self.bot.save_inventories()
    def won_rps(self, choice1: str, choice2: str) -> bool:
        if choice1 == "rock" and choice2 == "scissors":
            return True
        elif choice1 == "paper" and choice2 == "rock":
            return True
        elif choice1 == "scissors" and choice2 == "paper":
            return True
        return False

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
