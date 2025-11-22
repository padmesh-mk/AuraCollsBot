import discord
from discord.ext import commands
from discord import app_commands
import json

COLLECTIBLES_FILE = "collectibles.json"
SHOWCASE_FILE = "showcase.json"
COLLECTIBLE_INFO = "collectible_info.json"
RESTRICTED_FILE = "restrictedcoll.json"
TRADABLE_FILE = "tradablecoll.json"

CHECK = "<:ac_checkmark:1399650326201499798>"
CROSS = "<:ac_crossmark:1399650396322005002>"

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def get_collectible_details(coll):
    for db_file in [COLLECTIBLE_INFO, RESTRICTED_FILE, TRADABLE_FILE]:
        db = load_json(db_file)
        if coll in db:
            return db[coll]
    return None

class ShowcaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_collectibles(self, user_id):
        return load_json(COLLECTIBLES_FILE).get(str(user_id), {})

    def get_user_showcase(self, user_id):
        return load_json(SHOWCASE_FILE).get(str(user_id), {})

    def save_user_showcase(self, user_id, data):
        all_data = load_json(SHOWCASE_FILE)
        all_data[str(user_id)] = data
        save_json(SHOWCASE_FILE, all_data)

    def get_owned_collectibles_list(self, user_id):
        user_collectibles = self.get_user_collectibles(user_id)
        return [c for c, qty in user_collectibles.items() if qty > 0]

    def get_filled_slots(self, user_id):
        showcase = self.get_user_showcase(user_id)
        return [int(k) for k in showcase.keys() if k.isdigit()]

    async def update_profile_embed(self, user: discord.User):
        """Update profile embed if ProfileCog is open"""
        profile_cog = self.bot.get_cog("ProfileCog")
        if profile_cog and hasattr(profile_cog, "visibility"):
            if str(user.id) in profile_cog.visibility:
                visibility = profile_cog.visibility[str(user.id)]
                embed = await profile_cog.build_profile_embed(user, visibility)
                if hasattr(profile_cog, "last_profile_msg"):
                    msg = profile_cog.last_profile_msg.get(user.id)
                    if msg:
                        await msg.edit(embed=embed)

    @commands.hybrid_group(name="showcase", description="Manage your showcase", invoke_without_command=True)
    async def showcase(self, ctx):
        await ctx.send("Use `/showcase add <slot> <collectible>` or `/showcase remove <slot>`")

    @showcase.command(name="add")
    @app_commands.describe(slot="Slot number 1-3", collectible="Collectible to add")
    async def showcase_add(self, ctx, slot: int, collectible: str):
        if slot not in [1, 2, 3]:
            return await ctx.send(f"{CROSS} Slot must be 1, 2, or 3.")

        user_collectibles = self.get_user_collectibles(ctx.author.id)
        coll_key = collectible.lower()
        if coll_key not in user_collectibles or user_collectibles[coll_key] == 0:
            return await ctx.send(f"{CROSS} You don't own any `{collectible}`.")

        details = get_collectible_details(coll_key)
        emoji = details.get("emoji", "") if details else ""
        coll_name = details.get("name", coll_key) if details else coll_key

        showcase = self.get_user_showcase(ctx.author.id)
        showcase[str(slot)] = {
            "key": coll_key,   
            "name": coll_name,
            "emoji": emoji
        }
        self.save_user_showcase(ctx.author.id, showcase)
        await ctx.send(f"{CHECK} Added {emoji} `{coll_name}` to slot {slot}.")
        await self.update_profile_embed(ctx.author)

    @showcase.command(name="remove")
    @app_commands.describe(slot="Slot number 1-3")
    async def showcase_remove(self, ctx, slot: int):
        if slot not in [1, 2, 3]:
            return await ctx.send(f"{CROSS} Slot must be 1, 2, or 3.")

        showcase = self.get_user_showcase(ctx.author.id)
        if str(slot) in showcase:
            removed = showcase.pop(str(slot))
            self.save_user_showcase(ctx.author.id, showcase)
            await ctx.send(f"{CHECK} Removed {removed.get('emoji','')} `{removed['name']}` from slot {slot}.")
            await self.update_profile_embed(ctx.author)
        else:
            await ctx.send(f"{CROSS} Slot {slot} is already empty.")

    @showcase_add.autocomplete("collectible")
    async def collectible_autocomplete(self, interaction: discord.Interaction, current: str):
        owned = self.get_owned_collectibles_list(interaction.user.id)
        return [app_commands.Choice(name=c, value=c) for c in owned if current.lower() in c.lower()][:25]

    @showcase_remove.autocomplete("slot")
    async def slot_autocomplete(self, interaction: discord.Interaction, current: str):
        filled = self.get_filled_slots(interaction.user.id)
        return [app_commands.Choice(name=str(s), value=s) for s in filled if str(s).startswith(current)][:25]

async def setup(bot):
    await bot.add_cog(ShowcaseCog(bot))
