import json
import os
import sys
from discord import ApplicationError, Guild, Interaction
from nextcord.ext import commands
import nextcord
from configparser import ConfigParser

from utils.guild import GuildInventory

class InventoryBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_cogs()
        self._guildInventories: dict[int, GuildInventory] = self.load_inventories()

    def load_cogs(self):
        """
        Loads all cogs in the Cogs folder
        """
        for root, directories, files in os.walk("Cogs"):
            for file in files:
                if file.endswith(".py"):
                    self.load_extension(f"Cogs.{file[:-3]}")
    
    def get_guild_inventories(self, guild: int) -> GuildInventory | None:
        """
        Gets the guild inventories

        Parameters
        ----------
        guild : `int`
            The guild id
        
        Returns
        -------
        `GuildInventory` | `None`
            The guild inventory or None if it doesn't exist
        """
        if guild in self._guildInventories:
            return self._guildInventories[guild]
        return None

    def save_inventories(self):
        data = [self._guildInventories[guildInv].save() for guildInv in self._guildInventories]
        with open("./resources/inventories.json", "w") as f:
            json.dump(data, f, indent=4)

    @property
    def guildInventories(self) -> list[GuildInventory]:
        return self._guildInventories
    
    @guildInventories.setter
    def inventories(self, value: list[GuildInventory]) -> None:
        self._guildInventories = value


    def remove_guild(self, guild: int):
        pass


    async def on_ready(self):
        for guild in self.guilds:
            if guild.id not in self._guildInventories:
                self.add_guild(guild)
    
    def load_inventories(self) -> dict:
        with open("./resources/inventories.json", "r") as f:
            data = json.load(f)
        return {int(guild["guildId"]): GuildInventory.load(guild) for guild in data}

    def add_guild(self, guild: Guild):
        self._guildInventories[guild.id] = GuildInventory(guildId=guild.id, guildName=guild.name)

def _load_config(filename="config.ini", section="discord"):
    parser = ConfigParser()
    parser.read(filename)
    if not parser.has_section(section):
        raise Exception(f'Section {section} not found in the {filename} file')
    
    return dict(parser.items(section)).get('public-key')

def main():
    key = _load_config()
    # Create the bot
    bot = InventoryBot(intents=nextcord.Intents.all(), status=nextcord.Status.online, activity=nextcord.Game("InventoryBot"))

    # Run the bot
    bot.run(key, reconnect=True)

if __name__ == "__main__":
    main()