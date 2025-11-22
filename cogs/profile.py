import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime

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

PROFILE_FILE = "profile.json"

def get_profile(user_id: int):
    data = load_json(PROFILE_FILE)
    return data.get(str(user_id), {})

def save_profile(user_id: int, user_data: dict):
    data = load_json(PROFILE_FILE)
    data[str(user_id)] = user_data
    save_json(PROFILE_FILE, data)

class ToggleButton(discord.ui.Button):
    def __init__(self, cog, user_id, field, label, state: bool):
        self.cog = cog
        self.user_id = user_id
        self.field = field
        super().__init__(label=label, style=(discord.ButtonStyle.green if state else discord.ButtonStyle.danger))

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{CROSS} You cannot interact with this profile!", ephemeral=True)

        profile_data = get_profile(self.user_id)
        visibility = profile_data.get("visibility", self.cog.default_visibility.copy())
        visibility[self.field] = not visibility.get(self.field, True)

        profile_data["visibility"] = visibility
        save_profile(self.user_id, profile_data)

        self.style = discord.ButtonStyle.green if visibility[self.field] else discord.ButtonStyle.danger

        embed = await self.cog.build_profile_embed(interaction.user, visibility)
        await interaction.response.edit_message(embed=embed, view=ProfileView(self.cog, self.user_id, interaction.user.id))

class AddGifButton(discord.ui.Button):
    def __init__(self, cog, user_id):
        super().__init__(label="Add GIF", style=discord.ButtonStyle.blurple)
        self.cog = cog
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{CROSS} You cannot interact with this profile!", ephemeral=True)
        premium_data = load_json("premium.json").get("users", {}).get(str(interaction.user.id))
        if not premium_data:
            return await interaction.response.send_message(f"{CROSS} You are not premium!", ephemeral=True)

        await interaction.response.send_message("Send me a Tenor GIF link to add to your profile:")

        def check(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
            url = msg.content.strip()
            if not ("tenor.com" in url or url.endswith(".gif")):
                return await interaction.followup.send(f"{CROSS} That's not a valid Tenor GIF link!")
            showcase = load_json("showcase.json")
            showcase.setdefault(str(self.user_id), {})
            showcase[str(self.user_id)]["gif"] = url
            save_json("showcase.json", showcase)
            await interaction.followup.send(f"{CHECK} GIF added to your profile!")
        except Exception:
            await interaction.followup.send(f"{CROSS} You did not send a GIF in time!")

class EditTitleButton(discord.ui.Button):
    def __init__(self, cog, user_id):
        super().__init__(label="Edit Title", style=discord.ButtonStyle.blurple)
        self.cog = cog
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{CROSS} You cannot edit this profile!", ephemeral=True)
        await interaction.response.send_message("Send your new title (max 500 chars):")

        def check(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
            title = msg.content.strip()[:500]
            titles = load_json("titles.json")
            titles[str(self.user_id)] = title
            save_json("titles.json", titles)
            embed = await self.cog.build_profile_embed(interaction.user, get_profile(self.user_id).get("visibility", self.cog.default_visibility))
            await interaction.followup.send(f"{CHECK} Title updated!")
            await interaction.message.edit(embed=embed, view=ProfileView(self.cog, self.user_id, interaction.user.id))
        except Exception:
            await interaction.followup.send(f"{CROSS} You did not send a title in time!")

class EditFooterButton(discord.ui.Button):
    def __init__(self, cog, user_id):
        super().__init__(label="Edit Footer", style=discord.ButtonStyle.blurple)
        self.cog = cog
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"{CROSS} You cannot edit this profile!", ephemeral=True)
        premium_data = load_json("premium.json").get("users", {}).get(str(interaction.user.id))
        if not premium_data:
            return await interaction.response.send_message(f"{CROSS} Only premium users can set custom footers.")
        await interaction.response.send_message("Send your new footer text (max 200 chars):")

        def check(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
            footer = msg.content.strip()[:200]
            footers = load_json("footers.json")
            footers[str(self.user_id)] = footer
            save_json("footers.json", footers)
            embed = await self.cog.build_profile_embed(interaction.user, get_profile(self.user_id).get("visibility", self.cog.default_visibility))
            await interaction.followup.send(f"{CHECK} Footer updated!")
            await interaction.message.edit(embed=embed, view=ProfileView(self.cog, self.user_id, interaction.user.id))
        except Exception:
            await interaction.followup.send(f"{CROSS} You did not send a footer in time!")

class ProfileView(discord.ui.View):
    def __init__(self, cog, user_id, invoker_id):
        super().__init__(timeout=180)
        self.cog = cog
        self.user_id = user_id
        self.invoker_id = invoker_id

        profile_data = get_profile(user_id)
        visibility = profile_data.get("visibility", cog.default_visibility)

        self.add_item(EditTitleButton(cog, user_id))
        for field, label in [
            ("balance", "Balance"),
            ("premium", "Premium"),
            ("marriage", "Marriage"),
            ("showcase", "Showcase"),
            ("streaks", "Streaks"),
            ("votes", "Votes"),
        ]:
            btn = ToggleButton(cog, user_id, field, label, visibility.get(field, True))
            self.add_item(btn)
        self.add_item(AddGifButton(cog, user_id))
        self.add_item(EditFooterButton(cog, user_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.invoker_id:
            await interaction.response.send_message(f"{CROSS} You cannot interact with this profile!", ephemeral=True)
            return False
        return True

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_visibility = {
            "balance": True,
            "votes": True,
            "streaks": True,
            "premium": True,
            "marriage": True,
            "showcase": True
        }

    async def build_profile_embed(self, user: discord.Member, visibility: dict):
        points = load_json("coins.json").get(str(user.id), 0)
        premium_data = load_json("premium.json").get("users", {}).get(str(user.id))
        marriage_json = load_json("marriages.json")
        marriage_data = None
        for m in marriage_json.values():
            if m.get("user_id") == str(user.id) or m.get("partner_id") == str(user.id):
                marriage_data = m
                break
        daily_data = load_json("daily.json").get(str(user.id), {})
        weekly_data = load_json("weekly.json").get(str(user.id), {})
        votes_data = load_json("votes.json").get(str(user.id), {})
        showcase = load_json("showcase.json").get(str(user.id), {})
        user_coll = load_json("collectibles.json").get(str(user.id), {})
        restricted_coll = load_json("restrictedcoll.json")

        owned_restricted = [
            f"{v.get('emoji','')} **{v.get('name', k)}**"
            for k, v in restricted_coll.items()
            if v.get("owner_id") == user.id
        ]

        titles = load_json("titles.json")
        footers = load_json("footers.json")
        title_text = titles.get(str(user.id))
        footer_text = footers.get(str(user.id))

        profile_data = get_profile(user.id)
        since_str = profile_data.get("since")
        since_line = ""
        if since_str:
            ts = int(datetime.fromisoformat(since_str).timestamp())
            since_line = f"\n**Collecting since:** <t:{ts}:D> (<t:{ts}:R>)\n"

        desc = ""
        if title_text:
            desc += f"{title_text}\n\n"
        desc += f"**User:** {user.mention} `{user.name}`{since_line}\n"
        if visibility.get("balance", True):
            desc += f"<:ac_coins:1400522330668794028> **Balance:** `{points:,}` coins\n"
        if visibility.get("votes", True):
            desc += f"**<:ap_vote:1395506333834543144> Total Votes:** `{votes_data.get('votes',0)}`\n\n"
        if visibility.get("streaks", True):
            desc += f"**<a:ac_fire1:1412499109943709819> Streaks:**\n"
            desc += f"> **Daily:** `{daily_data.get('streak',0)}`\n"
            desc += f"> **Weekly:** `{weekly_data.get('streak',0)}`\n\n"
        if visibility.get("premium", True):
            value = "_Not a Premium user_"
            if premium_data:
                expiry_str = premium_data.get("expiry")
                if expiry_str:
                    expiry_ts = int(datetime.fromisoformat(expiry_str).timestamp())
                    value = f"Active until <t:{expiry_ts}:D> (<t:{expiry_ts}:R>)"
                else:
                    value = "Active"
            desc += f"<:ac_premium:1412065919882235914> **Premium:** {value}\n"
        if visibility.get("marriage", True):
            if marriage_data:
                partner_id = int(marriage_data.get("partner_id") if marriage_data.get("user_id")==str(user.id) else marriage_data.get("user_id"))
                partner_mention = f"<@{partner_id}>"
                start_date_str = marriage_data.get("start_date")
                date_display = f"<t:{int(datetime.fromisoformat(start_date_str).timestamp())}:D>" if start_date_str else "Unknown"
                desc += f"**<a:ac_redheart:1399456300500389899> Marriage:** {partner_mention} (Married on: {date_display})\n\n"
            else:
                desc += "**<:ac_ducksad:1409944288522928199> Marriage:** Single\n\n"
        if owned_restricted:
            desc += "**<a:ac_yay:1409934560699093054> Owned Collectibles:** \n" + "\n".join(f"> {item}" for item in owned_restricted) + "\n\n"

        embed = discord.Embed(
            title=f"{user.display_name}'s Profile",
            description=desc,
            color=user.color if user.color.value != 0 else discord.Color.from_str("#ff6b6b"),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        if footer_text:
            embed.set_footer(text=footer_text, icon_url=user.display_avatar.url)

        if visibility.get("showcase", True):
            showcase_desc = ""
            for slot in range(1,4):
                item = showcase.get(str(slot))
                if item:
                    qty = user_coll.get(item.get("key",""), 0)
                    showcase_desc += f"> {item.get('emoji','')} **{item.get('name','')}**: `{qty}`\n"
                else:
                    showcase_desc += f"> Slot {slot}: Empty\n"
            embed.add_field(name="<a:ac_star:1412347711314722846> **Showcase**", value=showcase_desc, inline=False)

            gif_url = showcase.get("gif")
            if gif_url:
                embed.set_image(url=gif_url)
        return embed

    @commands.hybrid_command(name="profile", description="Show a user's profile.")
    async def profile(self, ctx, member: discord.Member = None, edit: bool = False):
        user = member or ctx.author

        profile_data = get_profile(user.id)
        if "since" not in profile_data:
            profile_data["since"] = datetime.utcnow().isoformat()
        if "visibility" not in profile_data:
            profile_data["visibility"] = self.default_visibility.copy()
        save_profile(user.id, profile_data)

        if edit and user.id != ctx.author.id:
            return await ctx.reply(f"{CROSS} You can only edit your own profile!", ephemeral=True)

        visibility = profile_data.get("visibility", self.default_visibility)
        embed = await self.build_profile_embed(user, visibility)
        view = ProfileView(self, user.id, ctx.author.id) if edit else None
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
