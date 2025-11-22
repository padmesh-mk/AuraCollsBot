import discord
from discord.ext import commands
from discord import app_commands
import json, os

COLLECTIBLES_FILE = "collectibles.json"
BUNDLES_FILE = "bundles.json"
TRADABLE_FILE = "tradablecoll.json"
INFO_FILE = "collectible_info.json"

def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def get_user_inventory(user_id: int):
    data = load_json(COLLECTIBLES_FILE)
    return data.get(str(user_id), {})

def update_user_inventory(user_id: int, new_inv: dict):
    data = load_json(COLLECTIBLES_FILE)
    data[str(user_id)] = new_inv
    save_json(COLLECTIBLES_FILE, data)

def check_requirements(user_id: int, bundle_name: str):
    bundles = load_json(BUNDLES_FILE)
    if bundle_name not in bundles:
        return False, "Bundle not found."

    requirements = bundles[bundle_name]["requires"]
    inventory = get_user_inventory(user_id)

    missing = {}
    for item, qty in requirements.items():
        if inventory.get(item, 0) < qty:
            missing[item] = qty - inventory.get(item, 0)

    if missing:
        return False, missing
    return True, requirements

def claim_bundle(user_id: int, bundle_name: str):
    bundles = load_json(BUNDLES_FILE)
    if bundle_name not in bundles:
        return False, "Bundle not found."

    ok, result = check_requirements(user_id, bundle_name)
    if not ok:
        return False, result

    inventory = get_user_inventory(user_id)

    for item, qty in result.items():
        inventory[item] -= qty
        if inventory[item] <= 0:
            del inventory[item]

    reward = bundles[bundle_name]["reward"]
    inventory[reward] = inventory.get(reward, 0) + 1

    update_user_inventory(user_id, inventory)
    return True, reward

class Bundles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="bundle", description="Bundle related commands")
    async def bundle(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply("<:ac_crossmark:1399650396322005002> Please specify a subcommand (`view` or `claim`).")

    @bundle.command(name="view", description="View available bundles")
    async def bundle_view(self, ctx: commands.Context):
        bundles = load_json(BUNDLES_FILE)
        tradable = load_json(TRADABLE_FILE)
        info = load_json(INFO_FILE)

        bundle_names = list(bundles.keys())
        if not bundle_names:
            await ctx.reply("<:ac_crossmark:1399650396322005002> No bundles available right now.")
            return

        index = 0
        message = await ctx.reply(embed=self.make_bundle_embed(bundle_names[index], bundles, tradable, info, ctx.author, index, len(bundle_names)), 
                                  view=self.BundlePaginator(self, bundle_names, bundles, tradable, info, ctx.author, index))

    def make_bundle_embed(self, bundle_name, bundles, tradable, info, user, page, total):
        bundle = bundles[bundle_name]
        requires = bundle["requires"]
        reward = bundle["reward"]

        embed = discord.Embed(
            title=f"Bundle: {bundle_name.capitalize()}",
            description="Collect the items below to claim this bundle reward!",
            color=discord.Color.from_str("#ff6b6b")
        )
        embed.set_footer(text=f"Page {page+1}/{total}")

        inventory = get_user_inventory(user.id)
        req_list = []
        for item, qty in requires.items():
            emoji = (
                info.get(item, {}).get("emoji")
                or tradable.get(item, {}).get("emoji", "❓")
            )
            display_name = (
                info.get(item, {}).get("name")
                or tradable.get(item, {}).get("name")
                or item
            )
            owned = inventory.get(item, 0)
            req_list.append(f"`[{owned}/{qty}]` {emoji} {display_name}")

        reward_emoji = (
            info.get(reward, {}).get("emoji")
            or tradable.get(reward, {}).get("emoji", "🎁")
        )
        reward_name = (
            info.get(reward, {}).get("name")
            or tradable.get(reward, {}).get("name")
            or reward
        )
        embed.add_field(name="Required Collectibles:", value="\n".join(req_list), inline=False)
        embed.add_field(name="Reward:", value=f"{reward_emoji} {reward_name}", inline=False)

        return embed

    class BundlePaginator(discord.ui.View):
        def __init__(self, cog, bundle_names, bundles, tradable, info, user, index=0):
            super().__init__(timeout=60)
            self.cog = cog
            self.bundle_names = bundle_names
            self.bundles = bundles
            self.tradable = tradable
            self.info = info
            self.user = user
            self.index = index

        async def update_message(self, interaction: discord.Interaction):
            embed = self.cog.make_bundle_embed(
                self.bundle_names[self.index], self.bundles, self.tradable, self.info, self.user,
                self.index, len(self.bundle_names)
            )
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(emoji='<:ap_backward:1382775479202746378>', style=discord.ButtonStyle.primary)
        async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.user != interaction.user:
                return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> Not your menu!", ephemeral=True)
            self.index = (self.index - 1) % len(self.bundle_names)
            await self.update_message(interaction)

        @discord.ui.button(emoji="<:ap_forward:1382775383371419790>", style=discord.ButtonStyle.primary)
        async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.user != interaction.user:
                return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> Not your menu!", ephemeral=True)
            self.index = (self.index + 1) % len(self.bundle_names)
            await self.update_message(interaction)

    @bundle.command(name="claim", description="Claim a bundle reward")
    @app_commands.describe(name="Bundle name")
    async def bundle_claim(self, ctx: commands.Context, name: str):
        success, result = claim_bundle(ctx.author.id, name)
        if success:
            await ctx.reply(f"<:ac_checkmark:1399650326201499798> {ctx.author.mention}, you claimed: **{result}**")
        else:
            if isinstance(result, dict):
                missing = ", \n".join([f"- **{k}** ×{v}" for k,v in result.items()])
                await ctx.reply(f"<:ac_crossmark:1399650396322005002> You are missing the following collectibles:\n{missing}")
            else:
                await ctx.reply(f"<:ac_crossmark:1399650396322005002> {result}")

    @bundle_claim.autocomplete("name")
    async def bundle_autocomplete(self, interaction: discord.Interaction, current: str):
        bundles = load_json(BUNDLES_FILE)
        return [
            app_commands.Choice(name=b, value=b)
            for b in bundles.keys() if current.lower() in b.lower()
        ][:25]

async def setup(bot):
    await bot.add_cog(Bundles(bot))
