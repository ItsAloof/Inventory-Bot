from nextcord.ext import commands
from nextcord.application_command import slash_command
from nextcord import Interaction
from main import InventoryBot


class ItemShop(commands.Cog):
    def __init__(self, bot: InventoryBot):
        self.bot = bot
        
    @slash_command(name="itemshop", description="Commands for the itemshop", guild_ids=[1001667368801550439])
    def itemshop(self, interaction: Interaction):
        pass
    
    @itemshop.subcommand(name='list', description="List all the items available for purchase")
    def itemshop_list(self, interaction: Interaction):
        pass
    
    @slash_command(name='shopeditor', description="Allows admins to edit the itemshop", guild_ids=[1001667368801550439])
    def shopeditor(self, interaction: Interaction):
        pass
        
        

def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(ItemShop(bot))