import discord
from discord.ext import commands
from discord import app_commands
import json
import os

COINS_FILE = "coins.json"
LOG_CHANNEL_ID = 1410686729580581056 
OWNER_ID = 941902212303556618        

def load_coins():
    if not os.path.exists(COINS_FILE):
        with open(COINS_FILE, "w") as f:
            json.dump({}, f)
    with open(COINS_FILE, "r") as f:
        return json.load(f)


def save_coins(new_data):
    """
    Prevents overwriting by always loading the latest coins.json,
    merging the new data, and saving back.
    """
    data = load_coins() 
    for uid, balance in new_data.items():
        data[uid] = balance 
    with open(COINS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class CoinAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="coinadmin",
        description="Give or take coins from a user (Owner only)."
    )
    @app_commands.describe(
        action="Choose give or take",
        member="The target user",
        amount="How many coins to give or take"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Give", value="give"),
            app_commands.Choice(name="Take", value="take")
        ]
    )
    async def coinadmin(self, interaction: discord.Interaction, action: app_commands.Choice[str], member: discord.Member, amount: int):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("<:ac_crossmark:1399650396322005002> Only the bot owner can use this command.", ephemeral=True)
            return

        data = load_coins()
        user_id = str(member.id)

        if user_id not in data:
            data[user_id] = 0

        if action.value == "give":
            data[user_id] += amount
            result = f"<:ac_checkmark:1399650326201499798> Added {amount} coins to {member.mention}"
        elif action.value == "take":
            data[user_id] = max(0, data[user_id] - amount)
            result = f"<:ac_checkmark:1399650326201499798> Removed {amount} coins from {member.mention}"
        else:
            await interaction.response.send_message("<:ac_crossmark:1399650396322005002> Invalid action.", ephemeral=True)
            return

        save_coins(data)

        await interaction.response.send_message(result)

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="💰 Coin Admin Action",
                color=discord.Color.gold()
            )
            embed.add_field(name="Action", value=action.name, inline=True)
            embed.add_field(name="User", value=f"{member} (`{member.id}`)", inline=True)
            embed.add_field(name="Amount", value=str(amount), inline=True)
            embed.add_field(name="Invoker", value=f"{interaction.user} (`{interaction.user.id}`)", inline=False)

            message_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.id}"
            embed.add_field(name="Message Link", value=f"[Jump to Message]({message_link})", inline=False)

            await log_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CoinAdmin(bot))
