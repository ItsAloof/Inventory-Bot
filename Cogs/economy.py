from nextcord.ext import commands
from main import InventoryBot
from nextcord.application_command import slash_command
from nextcord import Interaction, SlashOption, Permissions, User
class Economy(commands.Cog):

    def __init__(self, bot: InventoryBot) -> None:
        self.bot = bot

    @slash_command(name="balance", description="View your balance", guild_ids=[1001667368801550439])
    async def balance(self, interaction: Interaction):
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(interaction.user)
            if inventory:
                await interaction.response.send_message(f"Your balance is {inventory.format_balance(guild.currency)}", ephemeral=True)
                return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

    @slash_command(name="balancetop", description="View the top 10 balances", guild_ids=[1001667368801550439])
    async def balancetop(self, interaction: Interaction):
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            msg = '\n'.join([f"{i+1}. {inventory.name}: {inventory.format_balance(guild.currency)}" for i, inventory in enumerate(guild.get_baltop())])
            await interaction.response.send_message(msg, ephemeral=False)
    
    @slash_command(name="addmoney", description="Add money to your balance", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def addmoney(self, interaction: Interaction, amount: int = SlashOption(name="amount", description="The amount of money to add", required=True), username: User = SlashOption(name="user", description="The user to add the money to", required=False)):
        user = interaction.user if not username else username
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(user)
            if inventory:
                if inventory.deposit(amount):
                    self.bot.save_inventories()
                    msg = f"Added {amount} to your balance" if user == interaction.user else f"Added {amount} to {user.name}'s balance"
                    await interaction.response.send_message(msg, ephemeral=True)
                    return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

    @slash_command(name="removemoney", description="Remove money from your balance", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def removemoney(self, interaction: Interaction, amount: int = SlashOption(name="amount", description="The amount of money to remove", required=True), username: User = SlashOption(name="user", description="The user to remove the money from", required=False)):
        user = interaction.user if not username else username
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(user)
            if inventory:
                if inventory.withdraw(amount):
                    self.bot.save_inventories()
                    msg = f"Removed {amount} from your balance" if user == interaction.user else f"Removed {amount} from {user.name}'s balance"
                    await interaction.response.send_message(msg, ephemeral=True)
                    return
                else:
                    await interaction.response.send_message("You don't have enough money", ephemeral=True)
                    return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

    @slash_command(name="setbalance", description="Set the balance of a player", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def setbalance(self, interaction: Interaction, user: User = SlashOption(name="user", description="The user to set the balance of", required=True, verify=True), amount: int = SlashOption(name="amount", description="The amount to set the balance to", required=True)):
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(user)
            if inventory:
                inventory.balance = amount
                self.bot.save_inventories()
                await interaction.response.send_message(f"Set {user.name}'s balance to {inventory.format_balance(guild.currency)}", ephemeral=True)
                return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)


def setup(bot: InventoryBot) -> None:
    print("Loaded {}".format(__name__))
    bot.add_cog(Economy(bot))


