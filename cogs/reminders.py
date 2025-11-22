import discord
from discord.ext import commands, tasks
from discord import app_commands
import json, os, time

REMINDERS_FILE = "reminders.json"
REMINDERCOOLDOWN_FILE = "remindercooldown.json"

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

async def add_reminder(user_id: int, category: str, name: str, channel_id: int, message_id: int, delay: int):
    cooldowns = load_json(REMINDERCOOLDOWN_FILE)
    user_id = str(user_id)

    if user_id not in cooldowns:
        cooldowns[user_id] = {}

    if category == "collectibles":
        cooldowns[user_id].setdefault("collectibles", {})[name] = {
            "end": int(time.time()) + delay,
            "channel": channel_id,
            "message": message_id
        }
    elif category == "coinflip":
        cooldowns[user_id]["coinflip"] = {
            "end": int(time.time()) + delay,
            "channel": channel_id,
            "message": message_id
        }
    elif category == "work":
        cooldowns[user_id]["work"] = {
            "end": int(time.time()) + delay,
            "channel": channel_id,
            "message": message_id
        }
    elif category == "pick":
        cooldowns[user_id]["pick"] = {
            "end": int(time.time()) + delay,
            "channel": channel_id,
            "message": message_id
        }

    save_json(REMINDERCOOLDOWN_FILE, cooldowns)


class ReminderView(discord.ui.View):
    def __init__(self, user_id: int, current_page: str, bot):
        super().__init__(timeout=None)
        self.user_id = str(user_id)
        self.current_page = current_page
        self.bot = bot

        self.add_item(ReminderDropdown(self.user_id, current_page, bot))

        reminders = load_json(REMINDERS_FILE)
        state = reminders.get(self.user_id, {}).get(current_page, False)
        self.add_item(ReminderToggle(self.user_id, current_page, bot, state))


class ReminderDropdown(discord.ui.Select):
    def __init__(self, user_id: str, current_page: str, bot):
        options = [
            discord.SelectOption(label="Collectible Trades", value="collectibles"),
            discord.SelectOption(label="Coinflip", value="coinflip"),
            discord.SelectOption(label="Work", value="work"),
            discord.SelectOption(label="Pick Event", value="pick"),
        ]
        super().__init__(placeholder="Choose reminder type...", options=options)
        self.user_id = user_id
        self.current_page = current_page
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> Not your menu.", ephemeral=True)

        new_page = self.values[0]
        embed = ReminderCog.get_embed(new_page)
        view = ReminderView(interaction.user.id, new_page, self.bot)
        await interaction.response.edit_message(embed=embed, view=view)


class ReminderToggle(discord.ui.Button):
    def __init__(self, user_id: str, page: str, bot, state: bool):
        label = "Disable" if state else "Enable"
        style = discord.ButtonStyle.green if not state else discord.ButtonStyle.red
        super().__init__(label=label, style=style)
        self.user_id = user_id
        self.page = page
        self.bot = bot
        self.state = state

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> Not your toggle.", ephemeral=True)

        reminders = load_json(REMINDERS_FILE)
        if self.user_id not in reminders:
            reminders[self.user_id] = {}

        self.state = not self.state
        reminders[self.user_id][self.page] = self.state
        save_json(REMINDERS_FILE, reminders)

        self.label = "Disable" if self.state else "Enable"
        self.style = discord.ButtonStyle.red if self.state else discord.ButtonStyle.green

        await interaction.response.edit_message(view=self.view)


class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    @commands.hybrid_command(name="reminders", description="Enable/Disable your reminders", aliases=["reminder"])
    async def reminders(self, ctx: commands.Context):
        embed = self.get_embed("collectibles")
        view = ReminderView(ctx.author.id, "collectibles", self.bot)
        await ctx.reply(embed=embed, view=view)

    @staticmethod
    def get_embed(page: str):
        if page == "collectibles":
            desc = "🔔 Toggle reminders for **Collectible Trades**.\n\nEnable to get notified when your cooldown is over!"
        elif page == "coinflip":
            desc = "🔔 Toggle reminders for **Coinflip** command.\n\nEnable to get notified when your cooldown is over!"
        elif page == "work":
            desc = "🔔 Toggle reminders for **Work** command.\n\nEnable to get notified when your cooldown is over!"
        elif page == "pick":
            desc = "🔔 Toggle reminders for **Pick Event**.\n\nEnable to get notified when your cooldown is over!"
        else:
            desc = "🔔 Toggle your reminders."

        return discord.Embed(title=f"{page.capitalize()} Reminders", description=desc, color=0x2F3136)

    @tasks.loop(seconds=5)  
    async def reminder_loop(self):
        reminders = load_json(REMINDERS_FILE)
        cooldowns = load_json(REMINDERCOOLDOWN_FILE)

        now = time.time()
        changed = False

        for user_id, data in list(cooldowns.items()):
            for category, info in list(data.items()):
                if category == "collectibles":
                    for coll, details in list(info.items()):
                        if now >= details["end"]:
                            if reminders.get(user_id, {}).get("collectibles", False):
                                try:
                                    channel = self.bot.get_channel(details["channel"])
                                    msg = await channel.fetch_message(details["message"])
                                    await msg.reply(f"<@{user_id}>, your `{coll}` cooldown is ready!")
                                except Exception as e:
                                    print(f"Reminder error: {e}")
                            del data["collectibles"][coll]
                            changed = True

                elif category == "coinflip":
                    if now >= info["end"]:
                        if reminders.get(user_id, {}).get("coinflip", False):
                            try:
                                channel = self.bot.get_channel(info["channel"])
                                msg = await channel.fetch_message(info["message"])
                                await msg.reply(f"<@{user_id}> time to `acoinflip` your money away.")
                            except Exception as e:
                                print(f"Reminder error: {e}")
                        del data["coinflip"]
                        changed = True
                        
                elif category == "work":
                    if now >= info["end"]:
                        if reminders.get(user_id, {}).get("work", False):
                            try:
                                channel = self.bot.get_channel(info["channel"])
                                msg = await channel.fetch_message(info["message"])
                                await msg.reply(f"<@{user_id}>, your `awork` cooldown is ready!")
                            except Exception as e:
                                print(f"Reminder error: {e}")
                        del data["work"]
                        changed = True
                        
                elif category == "pick":
                    if now >= info["end"]:
                        if reminders.get(user_id, {}).get("pick", False):
                            try:
                                channel = self.bot.get_channel(info["channel"])
                                msg = await channel.fetch_message(info["message"])
                                await msg.reply(f"<@{user_id}>, your `apick` cooldown is ready!")
                            except Exception as e:
                                print(f"Pick reminder error: {e}")
                        del data["pick"]
                        changed = True

        if changed:
            save_json(REMINDERCOOLDOWN_FILE, cooldowns)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))
