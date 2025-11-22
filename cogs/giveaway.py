import discord
from discord.ext import commands
import random, json, asyncio, time, os
from datetime import datetime, timedelta

COLLECTIBLES_FILE = "collectibles.json"
_file_lock = asyncio.Lock()

async def update_collectible(user_id: int, coll_key: str, amount: int = 1):
    """Safely add collectibles to a user with file lock protection."""
    user_id = str(user_id)
    async with _file_lock:
        if not os.path.exists(COLLECTIBLES_FILE):
            with open(COLLECTIBLES_FILE, "w") as f:
                json.dump({}, f)

        with open(COLLECTIBLES_FILE, "r") as f:
            data = json.load(f)

        if user_id not in data:
            data[user_id] = {}
        data[user_id][coll_key] = data[user_id].get(coll_key, 0) + amount

        with open(COLLECTIBLES_FILE, "w") as f:
            json.dump(data, f, indent=4)

    return data[user_id][coll_key]

class JoinButton(discord.ui.View):
    def __init__(self, giveaway, msg_id):
        super().__init__(timeout=None)
        self.giveaway = giveaway
        self.msg_id = msg_id

    @discord.ui.button(label="Join Giveaway!", style=discord.ButtonStyle.green, emoji="🎉", custom_id="join_giveaway")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.giveaway is None:
            await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> Giveaway system is still loading. Please try again shortly.",
                ephemeral=True
            )
            return
        
        async with _file_lock:
            with open(self.giveaway.state_path, "r") as f:
                state = json.load(f)

            participants = state.get("participants", [])
            if interaction.user.id in participants:
                await interaction.response.send_message(
                    "<:ap_crossmark:1382760353904988230> You've already joined this giveaway!",
                    ephemeral=True
                )
                return

            participants.append(interaction.user.id)
            state["participants"] = participants

            with open(self.giveaway.state_path, "w") as f:
                json.dump(state, f, indent=4)

        await interaction.response.send_message(
            "<:ap_checkmark:1382760062728273920> You've successfully entered the giveaway!",
            ephemeral=True
        )

        channel = interaction.guild.get_channel(state["channel_id"])
        try:
            msg = await channel.fetch_message(self.msg_id)
        except discord.NotFound:
            return

        embed = msg.embeds[0]
        embed.set_footer(text=f"{len(participants)} Participants")
        await msg.edit(embed=embed, view=self)

class AuraColls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_channel_id = 1399803032887361617
        self.ping_role_id = 1399797457172434997
        self.log_channel_id = 1399806268251705496
        self.owner_only_coll_path = "tradablecoll.json"
        self.state_path = "current_giveaway.json"
        self.bot.loop.create_task(self.resume_or_start())

    def get_random_owner_coll(self):
        with open(self.owner_only_coll_path, "r") as f:
            data = json.load(f)
        key = random.choice(list(data.keys()))
        return key, data[key]

    async def resume_or_start(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)
        try:
            with open(self.state_path, "r") as f:
                state = json.load(f)
            ends_at = state.get("end_time")
            if ends_at and time.time() < ends_at:
                await self.resume_giveaway(state)
                return
        except FileNotFoundError:
            pass
        await self.run_giveaway()

    async def run_giveaway(self):
        channel = self.bot.get_channel(self.giveaway_channel_id)
        role = channel.guild.get_role(self.ping_role_id)
        log_channel = self.bot.get_channel(self.log_channel_id)

        coll_key, coll_data = self.get_random_owner_coll()
        emoji, name = coll_data["emoji"], coll_data["name"]

        duration_hours = random.randint(12, 72)
        num_winners = random.randint(1, 10)
        ends_at = datetime.utcnow() + timedelta(hours=duration_hours)
        ends_at_unix = int(ends_at.timestamp())

        embed = discord.Embed(
            title="<a:ac_giveaway:1399806818158645348> A New Giveaway!",
            description=(
                f"**{num_winners} Lucky Users** will have a chance to win:\n\n"
                f"{emoji} {name}\n\n"
                f"Giveaway will end <t:{ends_at_unix}:R>\nGood luck!"
            ),
            color=0xFF6B6B
        )
        embed.set_footer(text="0 Participants")

        msg = await channel.send(content=role.mention, embed=embed, view=JoinButton(self, None))
        view = JoinButton(self, msg.id)
        await msg.edit(view=view)

        with open(self.state_path, "w") as f:
            json.dump({
                "channel_id": channel.id,
                "message_id": msg.id,
                "end_time": ends_at_unix,
                "collectible": coll_key,
                "num_winners": num_winners,
                "participants": []
            }, f, indent=4)

        if log_channel:
            jump_link = f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{msg.id}"
            log_embed = discord.Embed(
                title="📢 Giveaway Started",
                description=f"[Jump to Message]({jump_link})",
                color=0xFF6B6B,
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="Collectible", value=f"{emoji} **{name}**", inline=True)
            log_embed.add_field(name="Winners", value=str(num_winners), inline=True)
            log_embed.add_field(name="Duration", value=f"{duration_hours}h", inline=True)
            log_embed.add_field(name="Ends At", value=f"<t:{ends_at_unix}:F>", inline=False)
            await log_channel.send(embed=log_embed)

        await asyncio.sleep((ends_at - datetime.utcnow()).total_seconds())
        await self.end_giveaway(channel, msg, coll_key, coll_data, num_winners, log_channel)
        await self.run_giveaway()

    async def resume_giveaway(self, state):
        channel = self.bot.get_channel(state["channel_id"])
        log_channel = self.bot.get_channel(self.log_channel_id)
        try:
            msg = await channel.fetch_message(state["message_id"])
        except discord.NotFound:
            return await self.run_giveaway()

        await asyncio.sleep(state["end_time"] - time.time())

        with open(self.owner_only_coll_path, "r") as f:
            coll_data = json.load(f)[state["collectible"]]

        await self.end_giveaway(channel, msg, state["collectible"], coll_data, state["num_winners"], log_channel)
        await self.run_giveaway()

    async def end_giveaway(self, channel, msg, coll_key, coll_data, num_winners, log_channel):
        emoji, name = coll_data["emoji"], coll_data["name"]
        jump_link = f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{msg.id}"

        with open(self.state_path, "r") as f:
            state = json.load(f)
        participants = state.get("participants", [])

        embed = msg.embeds[0]

        if not participants:
            embed.title = "<:ap_crossmark:1382760353904988230> Giveaway Ended"
            embed.description = "No participants joined."
            embed.set_footer(text="0 Participants")

            view = JoinButton(self, msg.id)
            for child in view.children:
                child.disabled = True

            await msg.edit(content=None, embed=embed, view=view)

            if log_channel:
                log_embed = discord.Embed(
                    title="<:ap_crossmark:1382760353904988230> Giveaway Ended (No Participants)",
                    description=f"[Jump to Message]({jump_link})",
                    color=0xFF6B6B,
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(name="Item", value=f"{emoji} **{name}**", inline=True)
                await log_channel.send(embed=log_embed)
            return

        members = [channel.guild.get_member(uid) for uid in participants if channel.guild.get_member(uid)]
        winners = random.sample(members, min(num_winners, len(members)))

        for winner in winners:
            await update_collectible(winner.id, coll_key, 1)

        win_mentions = "\n".join(f"{w.mention}" for w in winners)
        embed.title = "<a:ac_giveaway:1399806818158645348> Giveaway Ended!"
        embed.description = (
            f"**{len(winners)} Lucky Users** won:\n\n"
            f"{emoji} {name}\n\n"
            f"Ended <t:{int(time.time())}:R>\n\n"
            f"{win_mentions}"
        )
        embed.set_footer(text=f"{len(participants)} Participants")

        view = JoinButton(self, msg.id)
        for child in view.children:
            child.disabled = True
        await msg.edit(embed=embed, view=view)

        if log_channel:
            winner_log = "\n".join(f"{w} (`{w.id}`)" for w in winners)
            log_embed = discord.Embed(
                title="<:ap_checkmark:1382760062728273920> Giveaway Ended",
                description=f"[Jump to Message]({jump_link})",
                color=0xFF6B6B,
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="Collectible", value=f"{emoji} **{name}**", inline=True)
            log_embed.add_field(name="Winners", value=str(len(winners)), inline=True)
            log_embed.add_field(name="Users", value=winner_log or "None", inline=False)
            await log_channel.send(embed=log_embed)

        try:
            os.remove(self.state_path)
        except Exception as e:
            print(f"Error deleting giveaway state: {e}")

async def setup(bot):
    await bot.add_cog(AuraColls(bot))
