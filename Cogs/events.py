from nextcord.ext import commands
from main import InventoryBot


class Events(commands.Cog):
    def __init__(self, bot: InventoryBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        pass


def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(Events(bot))