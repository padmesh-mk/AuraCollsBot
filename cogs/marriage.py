import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

MARRIAGE_FILE = "marriages.json"
COLLECTIBLES_FILE = "collectibles.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def make_key(uid1: int, uid2: int) -> str:
    """Generate stable key (smaller_id:larger_id)."""
    return f"{min(uid1, uid2)}:{max(uid1, uid2)}"

def find_marriage(user_id: int):
    marriages = load_json(MARRIAGE_FILE)
    for key, info in marriages.items():
        if str(user_id) in [info["user_id"], info["partner_id"]]:
            return key, info
    return None, None

class Marry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_ring(self, user_id: str):
        collectibles = load_json(COLLECTIBLES_FILE)
        return collectibles.get(str(user_id), {}).get("ring", 0) > 0

    @commands.hybrid_command(name="marry", description="Propose to another user with a ring")
    async def marry(self, ctx, user: discord.Member = None):
        if not user:
            return await ctx.reply("<:ac_crossmark:1399650396322005002> You need to mention someone to marry!")
  
        proposer = ctx.author
        
        if user.bot:
            return await ctx.reply("<:ac_crossmark:1399650396322005002> You can't marry bots, idiot!")

        if user.id == proposer.id:
            return await ctx.reply("<:ac_crossmark:1399650396322005002> You can’t marry yourself!")

        _, existing = find_marriage(proposer.id)
        if existing:
            return await ctx.reply("<:ac_crossmark:1399650396322005002> One of you is already married!")
        _, existing = find_marriage(user.id)
        if existing:
            return await ctx.reply("<:ac_crossmark:1399650396322005002> One of you is already married!")

        if not self.has_ring(proposer.id):
            return await ctx.reply("<:ac_crossmark:1399650396322005002> You need an <:ac_ring:1406956497648484442> Engagement Ring to propose!")

        embed = discord.Embed(
            title=f"{proposer.display_name} proposed to {user.display_name}! <:ac_ring:1406956497648484442>",
            description=(
                "Once you have accepted, you will receive an extra collectible when you both complete your daily!\n"
                "When you and your partner claim dailies together for 5 days in a row, you both will get baby collectible.\n\n"
                "If things don’t work out, you can always divorce anytime with `adivorce` or /divorce."
            ),
            color = ctx.author.color if ctx.author.color.value != 0 else discord.Color.from_str("#ff6b6b")
        )

        view = MarriageView(proposer, user, ctx)
        await ctx.reply(embed=embed, view=view)

    @commands.hybrid_command(name="marriage", description="Check your marriage status", aliases=["m"])
    async def marriage(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        key, data = find_marriage(user.id)
        if not data:
            return await ctx.reply(f"💔 {user.mention} is not married.")

        marriages = load_json(MARRIAGE_FILE)
        updated = False
        if data.get("user_username") != data.get("user_username", "Unknown"):
            data["user_username"] = data.get("user_username", "Unknown")
            updated = True
        if data.get("partner_username") != data.get("partner_username", "Unknown"):
            data["partner_username"] = data.get("partner_username", "Unknown")
            updated = True

        if updated:
            marriages[key] = data
            save_json(MARRIAGE_FILE, marriages)

        start_date = datetime.fromisoformat(data["start_date"])
        days = (datetime.utcnow() - start_date).days
        formatted_date = start_date.strftime("%a, %b %d, %Y")

        streak = data.get("shared_streak", 0)
        if str(user.id) == data["user_id"]:
            spouse_name = data.get("partner_username", f"User ID {data['partner_id']}")
        else:
            spouse_name = data.get("user_username", f"User ID {data['user_id']}")

        embed = discord.Embed(
            title=f"<a:ac_redheart:1399456300500389899> {user.name}, you are married to {spouse_name}!",
            description=(
                f"Married since **{formatted_date} ({days} days)**\n"
                f"You have claimed **{streak} dailies** together!"
            ),
            color = ctx.author.color if ctx.author.color.value != 0 else discord.Color.from_str("#ff6b6b")
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1406956497648484442.png?size=128")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="divorce", description="Divorce your partner 💔")
    async def divorce(self, ctx):
        user = ctx.author
        key, data = find_marriage(user.id)
        if not data:
            return await ctx.reply("<:ac_crossmark:1399650396322005002> You are not married!")

        marriages = load_json(MARRIAGE_FILE)
        marriages.pop(key, None)
        save_json(MARRIAGE_FILE, marriages)

        if str(user.id) == data["user_id"]:
            partner_id = data["partner_id"]
            partner_name = data.get("partner_username", f"User ID {partner_id}")
        else:
            partner_id = data["user_id"]
            partner_name = data.get("user_username", f"User ID {partner_id}")

        partner_name = partner.name if partner else data.get("partner_username", f"User ID {partner_id}")

        embed = discord.Embed(
            title="💔 Divorce Finalized",
            description=f"{user.mention} and {partner_name} are no longer married.",
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)


class MarriageView(discord.ui.View):
    def __init__(self, proposer, target, ctx):
        super().__init__(timeout=60)
        self.proposer = proposer
        self.target = target
        self.ctx = ctx

    @discord.ui.button(label="Accept 💖", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> This proposal isn’t for you!", ephemeral=True)

        collectibles = load_json(COLLECTIBLES_FILE)
        collectibles.setdefault(str(self.proposer.id), {})
        collectibles[str(self.proposer.id)]["ring"] = collectibles[str(self.proposer.id)].get("ring", 1) - 1
        save_json(COLLECTIBLES_FILE, collectibles)

        marriages = load_json(MARRIAGE_FILE)
        key = make_key(self.proposer.id, self.target.id)
        marriages[key] = {
            "user_id": str(self.proposer.id),
            "partner_id": str(self.target.id),
            "user_username": self.proposer.name,
            "partner_username": self.target.name,
            "start_date": datetime.utcnow().isoformat(),
            "shared_streak": 0,
            "daily_claimed": {"user": False, "partner": False}
        }
        save_json(MARRIAGE_FILE, marriages)

        embed = discord.Embed(
            title="Congratulations!",
            description=f"<a:ac_redheart:1399456300500389899> {self.proposer.mention} and {self.target.mention} are now married!",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Decline 💔", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> This proposal isn’t for you!", ephemeral=True)

        embed = discord.Embed(
            title="💔 Proposal Declined",
            description=f"{self.target.mention} rejected {self.proposer.mention}'s proposal.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    await bot.add_cog(Marry(bot))
