import json
import os
import sys
from discord import ApplicationError, Guild, Interaction
from nextcord.ext import commands
import nextcord

from utils.guild import GuildInventory

class InventoryBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_cogs()
        self._inventories = {}

    def load_cogs(self):
        for root, directories, files in os.walk("Cogs"):
            for file in files:
                if file.endswith(".py"):
                    self.load_extension(f"Cogs.{file[:-3]}")
    
    def get_guild_inventories(self, guild: int) -> GuildInventory | None:
        if guild in self.inventories:
            return self.inventories[guild]
        return None

    @property
    def save_inventories(self):
        data = [guild.save() for guild in self.inventories]
        with open("inventories.json", "w") as f:
            json.dump(data, f, indent=4)

    @property
    def inventories(self) -> list[GuildInventory]:
        return self._inventories
    
    @inventories.setter
    def inventories(self, value: list[GuildInventory]) -> None:
        self._inventories = value


    def remove_guild(self, guild: int):
        pass


    async def on_ready(self):
        print("Bot is ready")
    
    def load_inventories(self) -> dict:
        with open("inventories.json", "r") as f:
            data = json.load(f)
        print(data)
        # return {int(guild["guildId"]): GuildInventory.load(guild) for guild in data}

    def add_guild(self, guild: Guild):
        self.inventories[guild.id] = GuildInventory(guildId=guild.id, guildName=guild.name)


def main():
    # Create the bot
    bot = InventoryBot(intents=nextcord.Intents.all(), status=nextcord.Status.online, activity=nextcord.Game("InventoryBot"))

    # Run the bot
    bot.run("NDQ2NTE2MTIzOTI0NDMwODU4.GPoD8P.s5Wbyv0MF92fx4ms67bp7B-Xzx0b12qbNJ0Q8E", reconnect=True)

if __name__ == "__main__":
    main()