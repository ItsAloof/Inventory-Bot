from discord import Interaction, SlashCommandOption, SlashOption
from nextcord import Permissions, User
from nextcord.ext import commands
from nextcord.application_command import slash_command
from main import InventoryBot
from utils.item import Item
from utils.ui import EmbedCreator, EditUserInventoryView, ItemSelectorType

class InventoryCmd(commands.Cog):
    def __init__(self, bot: InventoryBot):
        self.bot = bot
    
    
    @slash_command(name="inventory", description="View your inventory", guild_ids=[1001667368801550439])
    async def inventory(self, interaction: Interaction, user: User = SlashOption(name="user", description="The user to view the inventory of", required=False)):
        inventory = self.bot.get_user_inventory(interaction.guild_id, user if user is not None else interaction.user)
        embeds = EmbedCreator.many_item_embeds(inventory.items, inventory.currency)
        if len(inventory.items) == 0:
            await interaction.send(content="There are no items to show", ephemeral=True)
            return
        
        if user is not None:
            await interaction.response.send_message(f"Viewing {user.name}'s inventory", embeds=embeds)
            return
        else:
            await interaction.response.send_message(content=f"**{inventory.name}'s Inventory**", embeds=embeds)


    @slash_command(name="additem", description="Add an item to your inventory", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def additem(self, interaction: Interaction, user: User = SlashOption(name="user", description="The user to give the item", required=True)):
        guild = self.bot.get_guild_inventory(interaction.guild_id)
        user = self.bot.get_user_inventory(guild.guildId, user)
        
        if guild.itemShop.item_count == 0:
            await interaction.send(content="There are no available items in the guilds item shop!", ephemeral=True)
            return
        
        if guild is None or user is None:
            await interaction.send(content="Inventory not found for user: {}".format(user.name))
            return
        
        await interaction.send(view=EditUserInventoryView(user=user, guild=guild, selectorType=ItemSelectorType.ADD_ITEM, sql=self.bot.pgsql))
        

    @slash_command(name="removeitem", description="Remove an item from your inventory", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def removeitem(self, interaction: Interaction, index: int = SlashOption(name="index", 
    description="Which item to remove starting from 1 to your inventory size", required=True), 
    username: User = SlashOption(name="user", description="The user to remove the item from", required=False)):
    
        user = interaction.user if not username else username
        guild = self.bot.get_guild_inventory(interaction.guild.id)
        if guild:
            inventory = guild.get_inventory(user)
            if len(inventory.items) == 0:
                msg = "Your inventory is empty" if user == interaction.user else f"{user.name}'s inventory is empty"
                await interaction.response.send_message(msg, ephemeral=True)
                return
            if inventory:
                item = inventory.remove_item(index)
                if item:
                    self.bot.save_inventories()
                    msg = f"Removed {item.name} from your inventory" if user == interaction.user else f"Removed {item.name} from {user.name}'s inventory"
                    await interaction.response.send_message(msg, ephemeral=True)
                    return
                else:
                    await interaction.response.send_message(f"Invalid number, please enter a number between 1 and {len(inventory.items)}", ephemeral=True)
                    return
        await interaction.response.send_message("Could not find inventory", ephemeral=True)

    @slash_command(name="clearinventory", description="Clear your or another users inventory", guild_ids=[1001667368801550439], default_member_permissions=Permissions(administrator=True))
    async def clearinventory(self, interaction: Interaction, username: User = SlashOption(name="user", description="The user to clear the inventory of", required=False)):
        user = interaction.user if not username else username
        inventory = self.bot.get_user_inventory(interaction.guild_id, user)
        if inventory is None:
            await interaction.send(content="No inventory found!")
            return
        
        inventory.clear()
        self.bot.pgsql.update_user(interaction.guild_id, inventory)
        msg = f"Your inventory has been cleared" if user == interaction.user else f"{user}'s inventory has been cleared"
        await interaction.response.send_message(msg, ephemeral=True)
        
        
    @slash_command(name="maxitems", description="Set the max items for the guild", default_member_permissions=Permissions(administrator=True))
    async def maxitems(self, interaction: Interaction, maxitems: int = SlashOption(name="maxitems", description="The max items to set", required=True)):
        guild = self.bot.get_guild_inventory(interaction.guild.id)
        if guild is None:
            await interaction.send(content="Something went wrong!")
            return
        guild.inventory_limit = maxitems
        self.bot.pgsql.update_guild(guild)
        await interaction.response.send_message(f"Set max items to {maxitems}", ephemeral=True)
        
        
def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(InventoryCmd(bot))