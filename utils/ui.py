import datetime
from typing import Any, List, Optional, Union
import nextcord
from nextcord import Embed
from nextcord.colour import Colour
from nextcord.components import SelectOption
from nextcord.interactions import Interaction
from nextcord.types.embed import EmbedType
from utils.guild import GuildInventory
from utils.item import Item

class EmbedCreator():
    
    @staticmethod
    def many_item_embeds(items: list[Item], currency: str) -> list[Embed]:
        """Creates multiple item embeds from a list of items

        Args:
            items (list[Item]): The items to turn into embeds
            currency (str): The currency to use when displaying the item value

        Returns:
            list[Embed]: The list of embeds created from the items
        """
        return [EmbedCreator.item_embed(item, currency) for item in items]
    
    @staticmethod
    def item_embed(item: Item, currency: str) -> Embed:
        """Create an embed for an `Item`

        Args:
            item (Item): The item to use for the embed
            currency (str): The currency to use when displaying the item value

        Returns:
            Embed: The emed for the item
        """
        embed = Embed(title=item.name, color=Colour.blue())
        embed.description = item.description
        embed.add_field(name='Value:', value=f'{currency}{item.value:,.2f}')
        return embed
    
    
class ItemSelector(nextcord.ui.StringSelect):
    def __init__(self, *, custom_id: str = "inventory-bot-itemselector", placeholder: str = "Select an item from the menu", min_values: int = 1, max_values: int = 1, options: List[SelectOption] = None, disabled: bool = False, row: int | None = None, guild: GuildInventory) -> None:
        if options is None:
            options = []
        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=options, disabled=disabled, row=row)
        self.guild = guild
        for item in guild.itemShop:
            self.add_option(label=item.name, value=str(item.id), description=item.description)
        
    async def callback(self, interaction: Interaction) -> None:
        
        assert self.view is not None
        selected = self.values[0]
        await interaction.response.edit_message(embed=EmbedCreator.item_embed(currency=self.guild.currency, item=self.guild.get_item(selected)))
        
class EditorView(nextcord.ui.View):
    def __init__(self, *, timeout: float | None = 180, auto_defer: bool = True, guild: GuildInventory) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.guild = guild
        self.add_item(ItemSelector(custom_id=f"editor-view-{guild.guildId}", row=1, guild=guild))
        

class ItemShopView(nextcord.ui.View):
    def __init__(self, *, timeout: float | None = 180, auto_defer: bool = True, guild: GuildInventory) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.add_item(ItemSelector(custom_id=f"itemshop-view-{guild.guildId}", min_values=1, max_values=1, guild=guild))
        
        