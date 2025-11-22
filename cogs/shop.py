import discord
from discord.ext import commands, tasks
from discord import app_commands
import json, random, asyncio
from datetime import datetime, timedelta

SHOP_FILE = 'shop.json'
POINTS_FILE = 'coins.json'
COLLS_FILE = 'collectibles.json'
RESTRICTED_FILE = 'restrictedcoll.json'
TRADABLE_FILE = 'tradablecoll.json'

RESET_HOUR_IST = 9
SHOP_CHANNEL_ID = 1401450861267255347
PING_ROLE_ID = 1401450943110840320
LOG_CHANNEL_ID = 1401450325260500993


class ShopButton(discord.ui.Button):
    def __init__(self, label, user_id, price, is_restricted, bot):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.user_id = user_id
        self.price = price
        self.is_restricted = is_restricted
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your shop menu!", ephemeral=True)
            return

        confirm_view = ConfirmPurchaseView(
            self.label, self.user_id, self.price, self.is_restricted, self.bot
        )

        embed = discord.Embed(
            title="Confirm Purchase",
            description=f"Are you sure you want to buy **{self.label}** for **{self.price}** coins?",
            color=0x99AAB5
        )

        await interaction.response.send_message(embed=embed, view=confirm_view)


class ConfirmPurchaseView(discord.ui.View):
    def __init__(self, item_name, user_id, price, is_restricted, bot):
        super().__init__(timeout=15)
        self.item_name = item_name
        self.user_id = user_id
        self.price = price
        self.is_restricted = is_restricted
        self.bot = bot

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't confirm someone else's purchase.", ephemeral=True)
            return

        user_id_str = str(self.user_id)

        with open(POINTS_FILE, 'r+') as f:
            points_data = json.load(f)
            user_points = points_data.get(user_id_str, 0)

            if user_points < self.price:
                await interaction.response.edit_message(
                    content=f"<:ap_crossmark:1382760353904988230> You don't have enough coins! You need `{self.price}`.",
                    view=None
                )
                return

            points_data[user_id_str] = user_points - self.price
            f.seek(0)
            json.dump(points_data, f, indent=4)
            f.truncate()

        coll_file = RESTRICTED_FILE if self.is_restricted else TRADABLE_FILE
        with open(coll_file, 'r') as f:
            coll_data = json.load(f)
        emoji = coll_data.get(self.item_name, {}).get('emoji', '')

        with open(COLLS_FILE, 'r+') as f:
            try:
                user_data = json.load(f)
            except json.JSONDecodeError:
                user_data = {}

            if user_id_str not in user_data:
                user_data[user_id_str] = {}

            user_data[user_id_str][self.item_name] = user_data[user_id_str].get(self.item_name, 0) + 1

            f.seek(0)
            json.dump(user_data, f, indent=4)
            f.truncate()

        embed = discord.Embed(title="Successful Purchase", color=0x57F287)
        embed.add_field(name="You have", value=f"`{points_data[user_id_str]}` coins left.", inline=False)
        embed.add_field(name="You bought", value=f"• 1 {emoji} {self.item_name}", inline=False)
        embed.add_field(name="You paid", value=f"• {self.price} coins", inline=False)
        await interaction.response.edit_message(content=None, embed=embed, view=None)

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(title="<:ac_shop:1403001224558673950> Purchase Log", color=0x57F287)
            log_embed.add_field(name="Buyer", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
            log_embed.add_field(name="Item Bought", value=f"{emoji} {self.item_name}", inline=False)
            log_embed.add_field(name="Cost", value=f"{self.price} coins", inline=True)
            log_embed.add_field(name="Remaining Coins", value=f"{points_data[user_id_str]} coins", inline=True)
            await log_channel.send(embed=log_embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Purchase cancelled.", view=None)


class ShopView(discord.ui.View):
    def __init__(self, items, user_id, bot):
        super().__init__(timeout=60)
        for item in items:
            btn = ShopButton(
                label=item['name'],
                user_id=user_id,
                price=item['price'],
                is_restricted=item['restricted'],
                bot=bot
            )
            self.add_item(btn)


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reset_shop_daily.start()

    def cog_unload(self):
        self.reset_shop_daily.cancel()

    @tasks.loop(minutes=1)
    async def reset_shop_daily(self):
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        if now.hour == RESET_HOUR_IST and now.minute == 0:
            await self.generate_shop()

    async def generate_shop(self):
        with open(RESTRICTED_FILE) as f:
            restricted = list(json.load(f).keys())
        with open(TRADABLE_FILE) as f:
            tradable = list(json.load(f).keys())

        today_shop = {
            'tradables': random.sample(tradable, 3)
        }
        with open(SHOP_FILE, 'w') as f:
            json.dump(today_shop, f, indent=4)

        channel = self.bot.get_channel(SHOP_CHANNEL_ID)
        if channel:
            items = await self.get_shop_items()
            embed = discord.Embed(title="<:ac_shop:1403001224558673950> Daily Collectible Shop", color=0xFF6B6B)
            for item in items:
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"Price: `{item['price']}` coins",
                    inline=False
                )
            await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)

    async def get_shop_items(self):
        with open(SHOP_FILE) as f:
            shop = json.load(f)
        with open(TRADABLE_FILE) as f:
            tradable = json.load(f)

        items = []
        for name in shop['tradables']:
            items.append({
                'name': name,
                'price': 50,
                'restricted': False,
                'emoji': tradable[name]['emoji']
            })
        return items

    @commands.hybrid_command(name="shop")
    async def shop_command(self, ctx):
        user_id = ctx.author.id
        with open(POINTS_FILE) as f:
            points = json.load(f).get(str(user_id), 0)

        items = await self.get_shop_items()

        embed = discord.Embed(title="<:ac_shop:1403001224558673950> Daily Collectible Shop", color=0xFF6B6B)
        embed.description = f"You have `{points}` coins. Select an item to buy:"

        for item in items:
            embed.add_field(name=f"{item['emoji']} {item['name']}", value=f"Price: `{item['price']}` coins", inline=False)

        await ctx.send(embed=embed, view=ShopView(items, user_id, self.bot))

    @reset_shop_daily.before_loop
    async def before_reset(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Shop(bot))
