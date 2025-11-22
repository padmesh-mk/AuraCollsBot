import discord
from discord.ext import commands
import json
import os

COINS_FILE = "coins.json"
LOG_CHANNEL_ID = 1408056613209636874

def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

class CoinShare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="give", aliases=["send"])
    async def give(self, ctx, *args):
        sender = ctx.author

        if len(args) < 2:
            return await ctx.reply("<:ap_crossmark:1382760353904988230> Usage: `give <user> <amount>` or `give <amount> <user>`", delete_after=5)

        member = None
        amount = None

        for arg in args:
            if arg.isdigit() and amount is None:
                amount = int(arg)
            else:
                try:
                    member = await commands.MemberConverter().convert(ctx, arg)
                except:
                    pass

        if not member:
            return await ctx.reply("<:ap_crossmark:1382760353904988230> You must mention a valid user to send coins to!", delete_after=3)
        if member.bot:
            return await ctx.reply("<:ap_crossmark:1382760353904988230> You can't send coins to bots!", delete_after=3)
        if member.id == sender.id:
            return await ctx.reply(f"{sender.mention} tried sending coins to *yourself...*", delete_after=3)
        if not amount or amount <= 0:
            return await ctx.reply("<:ap_crossmark:1382760353904988230> Please enter a valid amount of coins to send!", delete_after=3)

        coins_data = load_json(COINS_FILE)
        sender_coins = coins_data.get(str(sender.id), 0)

        if sender_coins < amount:
            return await ctx.reply(f"<:ap_crossmark:1382760353904988230> You only have `{sender_coins}` coins!", delete_after=3)

        embed = discord.Embed(
            title=f"**{sender.display_name}, you are about to give coins to {member.display_name}**",
            description=(
                f"{sender.mention} will give {member.mention}:\n"
                f"`{amount} coins`"
            ),
            color=discord.Color.greyple()
        )

        view = ConfirmView(sender, member, amount, coins_data, ctx)
        await ctx.reply(embed=embed, view=view)


class ConfirmView(discord.ui.View):
    def __init__(self, sender, receiver, amount, coins_data, ctx):
        super().__init__(timeout=60)
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.coins_data = coins_data
        self.ctx = ctx

    @discord.ui.button(label="Confirm", emoji="<:ap_checkmark:1382760062728273920>", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.sender.id:
            return await interaction.response.send_message("You cannot confirm this transfer.", ephemeral=True)

        self.coins_data[str(self.sender.id)] -= self.amount
        self.coins_data[str(self.receiver.id)] = self.coins_data.get(str(self.receiver.id), 0) + self.amount
        save_json(COINS_FILE, self.coins_data)

        await interaction.message.edit(
            content=f"<:ap_checkmark:1382760062728273920> {self.sender.mention} sent **{self.amount} coins** to {self.receiver.mention}!",
            embed=None,
            allowed_mentions=discord.AllowedMentions.none(),
            view=None
        )

        log_channel = self.ctx.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="💸 Coin Transfered",
                description=(
                    f"**Sender:** {self.sender.mention}\n"
                    f"**Receiver:** {self.receiver.mention}\n"
                    f"**Amount:** `{self.amount}` coins\n\n"
                    f"[Jump to message]({interaction.message.jump_url})"
                ),
                color=discord.Color.green()
            )
            await log_channel.send(embed=log_embed)

    @discord.ui.button(label="Cancel", emoji="<:ap_crossmark:1382760353904988230>", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.sender.id:
            return await interaction.response.send_message("You cannot cancel this transfer.", ephemeral=True)

        await interaction.message.edit(
            content=f"<:ap_crossmark:1382760353904988230> {self.sender.mention} cancelled the coin transfer.",
            embed=None,
            allowed_mentions=discord.AllowedMentions.none(),
            view=None
        )

async def setup(bot):
    await bot.add_cog(CoinShare(bot))
