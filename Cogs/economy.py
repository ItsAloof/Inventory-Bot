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


