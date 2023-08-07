from nextcord.ext import commands
from nextcord.application_command import slash_command
from nextcord import Interaction, SlashOption
from main import InventoryBot
from utils.item import Item
from utils.ui import EditorView


class ItemShop(commands.Cog):
    def __init__(self, bot: InventoryBot):
        self.bot = bot
        
    @slash_command(name='shop', description="Commands for the itemshop", guild_ids=[1001667368801550439])
    async def shop(self, interaction: Interaction):
        pass
    
    @shop.subcommand(name='list', description="List all the items available for purchase")
    async def list(self, interaction: Interaction):
        guild = self.bot._get_guild_inventory(interaction.guild_id)
        itemshop = guild.itemShop
        msg = '\n'.join([f'{i+1}.) {str(itemshop[i])}' for i in range(len(itemshop))])
        await interaction.response.send_message(msg)
    
    @slash_command(name='shopeditor', description="Allows admins to edit the itemshop", guild_ids=[1001667368801550439])
    async def shopeditor(self, interaction: Interaction):
        pass
    
    @shopeditor.subcommand(name="editor", description="Edit the itemshop within Discord")
    async def editor(self, interaction: Interaction):
        guild = self.bot._get_guild_inventory(interaction.guild_id)
        await interaction.send(view=EditorView(guild=guild))
    
    @shopeditor.subcommand(name='add', description='Add an item to the itemshop')
    async def add(self, interaction: Interaction, name: str = SlashOption(name="name", description="The name of the item", required=True),
            value: float = SlashOption(name="value", description="The value of the item", required=True, min_value=0),
            description: str = SlashOption(name="description", description="The item description", required=False)):
        guild = self.bot._get_guild_inventory(guild_id=interaction.guild_id)
        
        new_item = Item(name=name, description=description, value=value)
        
        guild.itemShop.append(new_item)
        
        self.bot.pgsql.update_guild(interaction.guild_id, guild)
        
        

def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(ItemShop(bot))