import datetime
from typing import Any, List, Callable, Optional, Union
import nextcord
from nextcord import Embed
from nextcord.colour import Colour
from nextcord.components import SelectOption
from nextcord.emoji import Emoji
from nextcord.enums import ButtonStyle, TextInputStyle
from nextcord.interactions import Interaction
from nextcord.partial_emoji import PartialEmoji
from nextcord.types.embed import EmbedType
from nextcord.utils import MISSING
from utils.guild import GuildInventory
from utils.item import Item
from utils.pgsql import Query
from utils.inventory import Inventory
from utils.itemstore import ItemStore
from enum import Enum

class ItemSelectorType(Enum):
    ADD_ITEM = 1
    REMOVE_ITEM = 2

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
        embed.set_image(item.url)
        embed.add_field(name='Value:', value=f'{currency}{item.value:,.2f}')
        embed.add_field(name="Amount:", value=str(item.amount))
        return embed
    
    
class ItemSelector(nextcord.ui.StringSelect):
    def __init__(self, *, custom_id: str = "inventory-bot-itemselector", placeholder: str = "Select an item from the menu", min_values: int = 1, max_values: int = 1, options: List[SelectOption] = None, disabled: bool = False, row: int | None = 2, guild: GuildInventory) -> None:
        if options is None:
            options = []
        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=options, disabled=disabled, row=row)
        self.guild = guild
        self.buttons_added = False
        for item in self.guild.itemShop.items:
            description = item.description if len(item.description) <= 100 else item.description[:97] + '...'
            self.add_option(label=item.name, value=str(item.id), description=description)
        
    def add_editor_buttons(self):
        self.view: EditorView
        self.edit_btn = EditButton()
        self.delete_btn = DeleteButton()
        self.view.add_item(self.edit_btn)
        self.view.add_item(self.delete_btn)
        
    def add_itemshop_buttons(self):
        self.view: ItemShopView
        self.buy_btn = BuyButton()
        self.view.add_item(self.buy_btn)
        
        
    async def callback(self, interaction: Interaction) -> None:
        
        assert self.view is not None
        if isinstance(self.view, EditorView) and not self.buttons_added:
            self.add_editor_buttons()
        elif not self.buttons_added:
            self.add_itemshop_buttons()
        
        self.buttons_added = True
        selected = self.values[0]
        self.view._selected_item = self.guild.itemShop.get_item(selected)
        await interaction.response.edit_message(embed=EmbedCreator.item_embed(currency=self.guild.currency, item=self.view._selected_item), view=self.view)
        
class EditorView(nextcord.ui.View):
    def __init__(self, *, timeout: float | None = 180, auto_defer: bool = True, guild: GuildInventory, sql: Query) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.guild = guild
        if len(guild.itemShop) > 0:
            self.add_item(ItemSelector(guild=guild, custom_id=f"editor-view-{guild.guildId}"))
        
        self.sql = sql
        self._selected_item = None

class ItemShopView(nextcord.ui.View):
    def __init__(self, *, timeout: float | None = 180, auto_defer: bool = True, guild: GuildInventory, sql: Query, user: Inventory) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.add_item(ItemSelector(custom_id=f"itemshop-view-{guild.guildId}", min_values=1, max_values=1, guild=guild))
        self.sql = sql
        self.guild = guild
        self.user = user
        self._selected_item = None

class EditModal(nextcord.ui.Modal):
    def __init__(self, title: str, *, timeout: float | None = None, custom_id: str = "inventory-bot-editmodal", auto_defer: bool = True, item: Item, guild: GuildInventory, update: Callable) -> None:
        super().__init__(title, timeout=timeout, custom_id=custom_id, auto_defer=auto_defer)
        self.name = nextcord.ui.TextInput(label="Name", placeholder=item.name)
        self.description = nextcord.ui.TextInput(label="Description", placeholder=item.description, style=nextcord.TextInputStyle.paragraph)
        self.value = nextcord.ui.TextInput(label="Value", placeholder=f"{item.value:,.2f}")
        self.item = item
        self.guild = guild
        self.update_guild = update
        self.add_item(self.name)
        self.add_item(self.description)
        self.add_item(self.value)
    
    async def callback(self, interaction: Interaction) -> None:
        try:
            if ',' in self.value.value:
                value = self.value.value.replace(',', '')
            else:
                value = self.value.value
            new_value = float(value)
            self.item.value = new_value
        except Exception as e:
            print(e)
            await interaction.send(content="Invalid value entered")
        self.item.name = self.name.value
        self.item.description = self.description.value
        self.update_guild(self.guild)
        await interaction.send(embed=EmbedCreator.item_embed(self.item, self.guild.currency))
        
        
class EditButton(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.primary, label: str | None = "Edit", disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 1) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction) -> None:
        self.view: EditorView
        if self.view._selected_item is None:
            await interaction.send(content="No item found")
            return
        await interaction.response.send_modal(EditModal(title="Item Editor", custom_id=f"edit-itemshop-{self.view.guild.guildId}", item=self.view._selected_item, guild=self.view.guild, update=self.view.sql.update_guild))
        
class DeleteButton(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.red, label: str | None = "Delete", disabled: bool = False, custom_id: str | None = None, url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 1) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
    
    async def callback(self, interaction: Interaction) -> None:
        self.view: EditorView
        if self.view._selected_item is None:
            await interaction.send(content="This item no longer exists!")
            return
        item = self.view._selected_item
        self.view._selected_item = None
        self.view.guild.remove_item(item)
        self.view.sql.update_guild(guild=self.view.guild)
        
        await interaction.send(content="Successfully Deleted Item:", embed=EmbedCreator.item_embed(item, self.view.guild.currency))
        
class BuyButton(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.green, label: str | None = "Buy", disabled: bool = False, custom_id: str | None = None, 
                 url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 1) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        
    async def callback(self, interaction: Interaction) -> None:
        
        if not isinstance(self.view, ItemShopView) and self.view._selected_item is not None:
            await interaction.send(content="The item is invalid")
            return
        
        if self.view._selected_item is None:
            await interaction.send(content="This item is no longer available for purchase")
        
        if not isinstance(self.view._selected_item, Item):
            await interaction.send(content="This item is no longer available for purchase")
            return
            
        item: Item = self.view._selected_item
        user: Inventory = self.view.user
        itemstore: ItemStore = self.view.guild.itemShop
        
        if itemstore.buy_item(item, user):
            self.view.sql.update_user(itemstore.guild_id, user)
            await interaction.send(content="Successfully added item:", embed=EmbedCreator.item_embed(item, self.view.guild.currency))
        else:
            await interaction.send(content="You cannot afford this item!")

class EditUserInventoryView(nextcord.ui.View):
    def __init__(self, *, timeout: float | None = 180, auto_defer: bool = True, user: Inventory, guild: GuildInventory, selectorType: ItemSelectorType) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.selectorType = selectorType
        self._selected_item = None
        self.guild = guild
        self.user = user

        if selectorType == ItemSelectorType.ADD_ITEM:
            self.add_item(UserItemSelector(user=user, items=guild.itemShop.items))
        elif selectorType == ItemSelectorType.REMOVE_ITEM:
            self.add_item(UserItemSelector(user=user, items=user.items))
        

class UserItemSelector(nextcord.ui.StringSelect):
    def __init__(self, *, custom_id: str = "user-item-selector", placeholder: str | None = "Select an item", min_values: int = 1, max_values: int = 1, 
                 options: List[SelectOption] = None, 
                 disabled: bool = False, row: int | None = 2, user: Inventory, items: List[Item], remove: bool) -> None:
                 
        options = [SelectOption(label=item.name, value=str(item.id), description=(item.description if len(item.description) <= 100 else item.description[:97] + '...')) for item in items]
        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=options, disabled=disabled, row=row)
        self.remove_mode = remove
        
    async def callback(self, interaction: Interaction) -> None:
        assert self.view is not None
        self.view: EditUserInventoryView
        
        self.view._selected_item = self.view.guild.itemShop.get_item(self.values[0])
        
        if self.view.selectorType == ItemSelectorType.ADD_ITEM:
            self.view.add_item(AddUserItemBtn(item=self.view._selected_item))
        elif self.view.selectorType == ItemSelectorType.REMOVE_ITEM:
            self.view.add_item(DeleteUserItemBtn())
        
        self.view.add_item()

class AmountSelect(nextcord.ui.TextInput):
    def __init__(self, label: str, *, style: TextInputStyle = TextInputStyle.numerator, custom_id: str = "amount-input-item", row: int | None = None, min_length: int | None = 1, max_length: int | None = 3, required: bool | None = True, default_value: str | None = None, placeholder: str | None = "Enter amount") -> None:
        super().__init__(label, style=style, custom_id=custom_id, row=row, min_length=min_length, max_length=max_length, required=required, default_value=default_value, placeholder=placeholder)
        
class EditItemModal(nextcord.ui.Modal):
    def __init__(self, title: str, *, timeout: float | None = 180, custom_id: str = "edit-user-item-modal", auto_defer: bool = True, item: Item) -> None:
        super().__init__(title, timeout=timeout, custom_id=custom_id, auto_defer=auto_defer)
        self.amount_input = AmountSelect()
        self.add_item(self.amount_input)
        self.item = item
        
        
    async def callback(self, interaction: Interaction) -> None:
        assert self.view is not None
        self.view: EditUserInventoryView
        try:
            self.item.amount = int(self.amount_input.value)
            await interaction.send(content="Successfully updated amount to {}".format(self.item.amount), ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.send(content="Invalid value entered!", ephemeral=True)
        
class EditUserItemBtn(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label: str | None = "Edit Amount", disabled: bool = False, custom_id: str | None = "edit-user-item", 
                 url: str | None = None, emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 1, item: Item) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.item = item
        
        
    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.send_modal(EditItemModal(title=f"Edit {self.item.name}"))
        
    
class DeleteUserItemBtn(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.red, label: str | None = "Remove All", disabled: bool = False, custom_id: str | None = "remove-all-button", url: str | None = None, 
                 emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 1, item: Item, user: Inventory) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.item = item
        self.user = user
        
    async def callback(self, interaction: Interaction) -> None:
        assert self.view is not None
        
class AddUserItemBtn(nextcord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.green, label: str = "Add Item", disabled: bool = False, custom_id: str | None = "add-user-item-btn", url: str | None = None, 
                 emoji: str | Emoji | PartialEmoji | None = None, row: int | None = 1, item: Item, user: Inventory) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        self.item = item
        
    async def callback(self, interaction: Interaction) -> None:
        assert self.view is not None
        
        self.view: EditUserInventoryView
        self.view.user.add_item(self.item)
        
        