from discord import Interaction, SlashCommandOption, SlashOption
from nextcord import Permissions
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

    @slash_command(name="additem", description="Add an item to your inventory", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
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

    @slash_command(name="removeitem", description="Remove an item from your inventory", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def removeitem(self, interaction: Interaction, index: int = SlashOption(name="index", description="Which item to remove starting from 1 to your inventory size", required=True)):
        user = interaction.user
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(user)
            if len(inventory.items) == 0:
                await interaction.response.send_message("Your inventory is empty", ephemeral=True)
                return
            if inventory:
                item = inventory.remove_item(index)
                if item:
                    self.bot.save_inventories()
                    await interaction.response.send_message(f"Removed {item.name} from your inventory", ephemeral=True)
                    return
                else:
                    await interaction.response.send_message(f"Invalid number, please enter a number between 1 and {len(inventory.items)}", ephemeral=True)
                    return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

    @slash_command(name="clearinventory", description="Clear your inventory", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def clearinventory(self, interaction: Interaction):
        user = interaction.user
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(user)
            if inventory:
                inventory.clear()
                self.bot.save_inventories()
                await interaction.response.send_message("Cleared your inventory", ephemeral=True)
                return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

    @slash_command(name="set", description="Used to set values for the guild", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def set(self, interaction: Interaction):
        pass

    @set.subcommand(name="currency", description="Set the currency for the guild")
    async def set_currency(self, interaction: Interaction, currency: str = SlashOption(name="currency", description="The currency to set", required=True)):
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            guild.currency = currency
            self.bot.save_inventories()
            await interaction.response.send_message(f"Set currency to {currency}", ephemeral=True)
            return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)
    
    @set.subcommand(name="maxitems", description="Set the max items for the guild")
    async def set_maxitems(self, interaction: Interaction, maxitems: int = SlashOption(name="maxitems", description="The max items to set", required=True)):
        guild = self.bot.get_guild_inventories(interaction.guild.id)
        if guild:
            guild.inventory_limit = maxitems
            self.bot.save_inventories()
            await interaction.response.send_message(f"Set max items to {maxitems}", ephemeral=True)
            return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(InventoryCmd(bot))