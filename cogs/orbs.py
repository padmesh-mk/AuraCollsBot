import discord
from discord.ext import commands
from datetime import datetime
import json
import os
from typing import Dict, Any

ORB_FILE = "orb.json"    
ORBS_FILE = "orbs.json"  


def ensure_file(filename: str, default: Any):
    """Ensure file exists; create with default if missing."""
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)


def load_json(filename: str) -> Dict:
    ensure_file(filename, {})
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            with open(filename, "w", encoding="utf-8") as fw:
                json.dump({}, fw)
            return {}


class OrbSelect(discord.ui.Select):
    def __init__(self, view: "OrbView"):
        options = [
            discord.SelectOption(label="All", value="All", description="Show all orbs (default)"),
            discord.SelectOption(label="Owned", value="Owned", description="Show only orbs you own"),
            discord.SelectOption(label="Not Owned", value="Not Owned", description="Show only orbs you don't own"),
        ]
        super().__init__(placeholder="Filter orbs...", min_values=1, max_values=1, options=options)
        self.view_ref: OrbView = view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view_ref.invoker.id:
            return await interaction.response.send_message("You cannot use this menu.", ephemeral=True)

        self.view_ref.filter_type = self.values[0]
        await interaction.response.edit_message(embed=self.view_ref.build_embed(), view=self.view_ref)


class OrbView(discord.ui.View):
    def __init__(self, bot: commands.Bot, invoker: discord.User, target: discord.User, orb_defs: Dict, user_orbs: Dict):
        super().__init__(timeout=180)
        self.bot = bot
        self.invoker = invoker
        self.target = target
        self.orb_defs = orb_defs     
        self.user_orbs = user_orbs   
        self.filter_type = "All"     

        self.add_item(OrbSelect(self))

    def build_embed(self) -> discord.Embed:
        orb_keys = list(self.orb_defs.keys())[:12]

        rows = []
        for key in orb_keys:
            info = self.orb_defs.get(key, {})
            emoji = info.get("emoji", "")
            name = info.get("name", key)
            count = self.user_orbs.get(key, 0) if isinstance(self.user_orbs, dict) else 0

            if self.filter_type == "Owned" and count <= 0:
                continue
            if self.filter_type == "Not Owned" and count > 0:
                continue

            rows.append(f"{emoji} **{name}**: `{count}`")

        if not rows:
            description = "*No orbs match this filter.*"
        else:
            description = "\n".join(rows)

        embed = discord.Embed(
            title=f"{self.target.display_name}'s Orbs",
            description=description,
            color=discord.Color.from_str("#FF6B6B")
        )

        embed.set_footer(text=f"Filter: {self.filter_type} • Only obtainable during Event!")
        return embed


class OrbsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        ensure_file(ORB_FILE, {})
        ensure_file(ORBS_FILE, {})

    def get_orb_defs(self) -> Dict[str, Dict]:
        return load_json(ORB_FILE)

    def get_user_orbs(self, user_id: int) -> Dict[str, int]:
        data = load_json(ORBS_FILE)
        return data.get(str(user_id), {})

    @commands.hybrid_command(name="orb", aliases=["orbs"], description="View someone's orbs")
    async def orb_cmd(self, ctx: commands.Context, member: discord.Member = None):
        """
        Hybrid command: prefix and slash.
        Usage:
          !orb -> your orbs
          !orb @member -> member's orbs
        """
        target = member or ctx.author

        orb_defs = self.get_orb_defs()
        user_orbs = self.get_user_orbs(target.id)

        view = OrbView(bot=self.bot, invoker=ctx.author, target=target, orb_defs=orb_defs, user_orbs=user_orbs)
        embed = view.build_embed()
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(OrbsCog(bot))
