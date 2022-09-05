from nextcord.ext import commands
from InventoryBot import InventoryBot


class Events(commands.Cog):
    def __init__(self, bot: InventoryBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # self.bot.inventories(self.bot.load_inventories())
        for guild in self.bot.guilds:
            if guild.id not in self.bot.inventories:
                self.bot.add_guild(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        pass


def setup(bot: InventoryBot):
    print(f"Loaded {__name__}")
    bot.add_cog(Events(bot))