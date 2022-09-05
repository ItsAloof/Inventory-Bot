from discord import Interaction, SlashCommandOption, SlashOption
from nextcord.ext import commands
from nextcord.application_command import slash_command
from InventoryBot import InventoryBot
from utils.item import Item
class InventoryCmd(commands.Cog):
    def __init__(self, bot: InventoryBot):
        self.bot = bot
    
    
    @slash_command(name="inventory", description="View your inventory", guild_ids=[1001667368801550439])
    async def inventory(self, interaction: Interaction, user: str = SlashOption(name="user", description="The user to view the inventory of", required=False)):
        if user:
            await interaction.response.send_message(f"Viewing {user}'s inventory")
        else:
            inventory = self.bot.get_guild_inventories(interaction.guild_id).get_inventory(interaction.user)
            await interaction.response.send_message(str(inventory), ephemeral=True)

    @slash_command(name="additem", description="Add an item to your inventory", guild_ids=[1001667368801550439])
    async def additem(self, interaction: Interaction, 
    name: str = SlashOption(name="name", description="The name of the item", required=True), 
    description: str = SlashOption(name="description", description="The description of the item", required=True), 
    value: int = SlashOption(name="value", description="The value of the item", required=True)):

        user = interaction.user
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        item = Item(name=name, description=description, value=value, currency=guild.currency)
        if guild:
            inventory = guild.get_inventory(user)
            if inventory:
                inventory.add_item(item)
                self.bot.save_inventories()
                await interaction.response.send_message(f"Added {item.name} to your inventory", ephemeral=True)
                return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(InventoryCmd(bot))