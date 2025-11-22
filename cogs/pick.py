import discord
from discord.ext import commands
from cogs.reminders import add_reminder
import random
import json
import os
import time
from datetime import datetime

COINS_FILE = "coins.json"
COLLECTIBLES_FILE = "collectibles.json"
ORBS_FILE = "orbs.json"
PREMIUM_FILE = "premium.json"
EVENTCD_FILE = "eventcd.json"
EVENTMSG_FILE = "eventmsg.json"
COLLECTIBLE_INFO_FILE = "collectible_info.json"
ORB_INFO_FILE = "orb.json"

def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_json(file, data):
    tmp_file = f"{file}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp_file, file)

PICK_COLLECTIBLES = ["toilet", "philosophy", "television"]
PICK_ORB = "spark"

EVENT_START = "2025-11-01 03:30:00"
EVENT_END = "2025-11-10 03:30:00"

class PickEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reload_data()

    def reload_data(self):
        self.coins_data = load_json(COINS_FILE)
        self.collectibles_data = load_json(COLLECTIBLES_FILE)
        self.orbs_data = load_json(ORBS_FILE)
        self.premium_data = load_json(PREMIUM_FILE)
        self.cooldowns_data = load_json(EVENTCD_FILE)
        self.event_msgs = load_json(EVENTMSG_FILE)
        self.collectible_info = load_json(COLLECTIBLE_INFO_FILE)
        self.orb_info = load_json(ORB_INFO_FILE)

    def get_cooldown(self, user_id):
        """Return cooldown in seconds. Premium 30 min, default 1 hour."""
        users = self.premium_data.get("users", {})
        user = users.get(str(user_id))
        if user:
            try:
                expiry = datetime.fromisoformat(user["expiry"])
                if expiry > datetime.utcnow():
                    return 30 * 60
            except Exception:
                pass
        return 60 * 60

    def is_event_active(self):
        now = datetime.utcnow()
        start = datetime.strptime(EVENT_START, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(EVENT_END, "%Y-%m-%d %H:%M:%S")
        return start <= now <= end

    async def reward_user(self, ctx, user_id):
        roll = random.randint(1, 100)

        self.reload_data()

        if roll <= 64:
            msg = random.choice(self.event_msgs.get("nothing", ["You got nothing!"]))
            embed = discord.Embed(description=msg, color=discord.Color.from_str("#ff6b6b"))
            await ctx.send(embed=embed)

        elif roll <= 94:
            amount = random.randint(5, 25)
            emoji = "<:ac_coins:1400522330668794028>"
            current = self.coins_data.get(str(user_id), 0)
            self.coins_data[str(user_id)] = current + amount
            save_json(COINS_FILE, self.coins_data)
            msg_list = self.event_msgs.get("coins", ["You found {amount} coins!"])
            msg = random.choice(msg_list).format(amount=amount)
            embed = discord.Embed(description=f"{emoji} {msg}", color=discord.Color.from_str("#ff6b6b"))
            await ctx.send(embed=embed)

        elif roll <= 99:
            item_key = random.choice(PICK_COLLECTIBLES)
            item_data = self.collectible_info.get(item_key, {})
            emoji = item_data.get("emoji", "")
            name = item_data.get("name", item_key)
            display_name = f"{emoji} {name}"
            user_coll = self.collectibles_data.get(str(user_id), {})
            user_coll[item_key] = user_coll.get(item_key, 0) + 1
            self.collectibles_data[str(user_id)] = user_coll
            save_json(COLLECTIBLES_FILE, self.collectibles_data)
            msg = random.choice(self.event_msgs.get("collectibles", ["You found {item}!"]))
            msg = msg.format(item=display_name)
            embed = discord.Embed(description=msg, color=discord.Color.from_str("#ff6b6b"))
            await ctx.send(embed=embed)

        else:
            orb_data = self.orb_info.get(PICK_ORB, {})
            emoji = orb_data.get("emoji", "")
            name = orb_data.get("name", PICK_ORB)
            display_name = f"{emoji} {name}"
            user_orbs = self.orbs_data.get(str(user_id), {})
            user_orbs[PICK_ORB] = user_orbs.get(PICK_ORB, 0) + 1
            self.orbs_data[str(user_id)] = user_orbs
            save_json(ORBS_FILE, self.orbs_data)
            msg = random.choice(self.event_msgs.get("orbs", ["You found {item}!"]))
            msg = msg.format(item=display_name)
            embed = discord.Embed(description=msg, color=discord.Color.from_str("#ff6b6b"))
            await ctx.send(embed=embed)

        self.cooldowns_data[str(user_id)] = int(time.time())
        save_json(EVENTCD_FILE, self.cooldowns_data)

    @commands.hybrid_command(name="pick", description="Pick to get coins, collectibles, or a special orb!")
    async def pick(self, ctx):
        user_id = ctx.author.id
        now_ts = int(time.time())
        cd = self.get_cooldown(user_id)
        last = self.cooldowns_data.get(str(user_id), 0)

        if not self.is_event_active():
            embed = discord.Embed(
                title="<:ap_crossmark:1382760353904988230> Event Currently Unavailable",
                description="The event is currently over. Keep an eye out for the next one!",
                color=discord.Color.from_str("#ff0000")
            )
            await ctx.send(embed=embed)
            return

        if now_ts - last < cd:
            retry_time = now_ts + (cd - (now_ts - last))
            embed = discord.Embed(
                title="<:ap_time:1382729675616555029> Slow Down!",
                description=(
                    f"You'll be able to use this command again <t:{retry_time}:R>\n\n"
                    f"The **default** cooldown is `1 hour`\n"
                    f"The **premium** cooldown is `30 minutes`"
                ),
                color=discord.Color.default()
            )
            await ctx.send(embed=embed)
            return

        await self.reward_user(ctx, user_id)

        self.bot.loop.create_task(
            add_reminder(
                user_id=user_id,
                category="pick",
                name="Cooldown finished",
                channel_id=ctx.channel.id,
                message_id=ctx.message.id,
                delay=cd
            )
        )

async def setup(bot):
    try:
        await bot.add_cog(PickEvent(bot))
        print("✅ PickEvent cog loaded successfully!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Failed to load PickEvent cog: {e}")
