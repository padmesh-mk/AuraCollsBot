import discord
from discord.ext import commands, tasks
import random
import json
import os
from datetime import datetime, timedelta, timezone
import pytz
import asyncio

DAILY_FILE = "daily.json"
POINTS_FILE = "coins.json"
COLLECTIBLES_FILE = "collectibles.json"
MARRIAGE_FILE = "marriages.json"
TRADABLE_FILE = "tradablecoll.json"
PREMIUM_FILE = "premium.json"

COLLECTIBLES = ["Kubo", "Luma", "Bobo", "Nubi", "Roro"]
COLLECTIBLE_EMOJIS = {
    "Kubo": "<a:ac_vanillabearicecream:1399440453778280591>",
    "Luma": "<a:ac_bluebearicecream:1399440402255188120>",
    "Bobo": "<a:ac_chocolatebearicecream:1399440480332152922>",
    "Nubi": "<a:ac_pinkbearicecream:1399440514591490118>",
    "Roro": "<a:ac_redbearicecream:1399440427098308749>"
}

_file_lock = asyncio.Lock()

async def _ensure_file(path: str):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)

async def load_json_async(path: str):
    await _ensure_file(path)
    async with _file_lock:
        with open(path, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}

async def save_json_async(path: str, data):
    async with _file_lock:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

async def is_premium(user_id: int) -> bool:
    data = await load_json_async(PREMIUM_FILE)
    users = data.get("users", {})
    entry = users.get(str(user_id))
    if not entry:
        return False
    expiry_str = entry.get("expiry")
    if not expiry_str:
        return False
    try:
        expiry = datetime.fromisoformat(expiry_str)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < expiry
    except Exception:
        return False

def get_remaining_time():
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    next_reset = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now >= next_reset:
        next_reset += timedelta(days=1)
    remaining = next_reset - now
    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}H {minutes}M {seconds}S"

def _uid(u):
    return str(u)

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_reset_date = None
        self.reset_marriage_daily.start()

    @tasks.loop(minutes=1)
    async def reset_marriage_daily(self):
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        if now.hour == 9 and now.minute == 0 and self.last_reset_date != now.date():
            marriages = await load_json_async(MARRIAGE_FILE)
            changed = False
            for _, data in marriages.items():
                if "daily_claimed" in data:
                    data["daily_claimed"]["user"] = False
                    data["daily_claimed"]["partner"] = False
                    changed = True
            if changed:
                await save_json_async(MARRIAGE_FILE, marriages)
            self.last_reset_date = now.date()

    async def claim_daily(self, user: discord.User):
        user_id = _uid(user.id)
        daily_data = await load_json_async(DAILY_FILE)
        points_data = await load_json_async(POINTS_FILE)
        coll_data = await load_json_async(COLLECTIBLES_FILE)
        marriages = await load_json_async(MARRIAGE_FILE)
        tradables = await load_json_async(TRADABLE_FILE)

        now_utc = datetime.now(timezone.utc)
        last_claim_iso = daily_data.get(user_id, {}).get("last_claim")
        streak = daily_data.get(user_id, {}).get("streak", 0)

        premium_flag = await is_premium(user.id)

        marriage_key = None
        marriage_data = None
        for key, data in marriages.items():
            if _uid(data.get("user_id")) == user_id or _uid(data.get("partner_id")) == user_id:
                marriage_key = key
                marriage_data = data
                break

        partner_id = None
        partner_status = None
        if marriage_data:
            u1 = _uid(marriage_data.get("user_id"))
            u2 = _uid(marriage_data.get("partner_id"))
            if u1 == user_id:
                partner_id = u2
                partner_status = marriage_data.get("daily_claimed", {}).get("partner", False)
            else:
                partner_id = u1
                partner_status = marriage_data.get("daily_claimed", {}).get("user", False)

        if last_claim_iso:
            try:
                last_time = datetime.fromisoformat(last_claim_iso)
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)
            except Exception:
                last_time = None

            tz = pytz.timezone("Asia/Kolkata")
            now_ist = datetime.now(tz)
            today_reset = now_ist.replace(hour=9, minute=0, second=0, microsecond=0)
            if now_ist < today_reset:
                today_reset -= timedelta(days=1)
            today_reset_utc = today_reset.astimezone(timezone.utc)

            if last_time and last_time >= today_reset_utc:
                remaining = get_remaining_time()
                return False, streak, None, None, remaining, None, None, partner_status, partner_id, premium_flag

        base_points = random.randint(1, 10)
        chosen_collectibles = []
        chosen_collectibles.append(random.choice(COLLECTIBLES))

        if premium_flag:
            base_points += 25

        streak += 1
        daily_data[user_id] = {
            "username": user.name,
            "last_claim": now_utc.isoformat(),
            "streak": streak
        }

        if marriage_data:
            if _uid(marriage_data.get("user_id")) == user_id:
                marriage_data.setdefault("daily_claimed", {})["user"] = True
            else:
                marriage_data.setdefault("daily_claimed", {})["partner"] = True
            await save_json_async(DAILY_FILE, daily_data)

            if marriage_data["daily_claimed"].get("user") and marriage_data["daily_claimed"].get("partner"):
                shared_coll = random.choice(COLLECTIBLES)
                extra_points = random.randint(1, 10)
                tradable_list = list(tradables.keys())
                extra_coll = random.choice(tradable_list) if tradable_list else None

                for uid in [_uid(marriage_data["user_id"]), _uid(marriage_data["partner_id"])]:
                    # points
                    add_pts = base_points
                    if await is_premium(int(uid)):
                        add_pts += 25
                    points_data[uid] = points_data.get(uid, 0) + add_pts

                    if uid not in coll_data:
                        coll_data[uid] = {}
                    coll_data[uid][shared_coll] = coll_data[uid].get(shared_coll, 0) + 1

                    points_data[uid] += extra_points
                    if extra_coll:
                        coll_data[uid][extra_coll] = coll_data[uid].get(extra_coll, 0) + 1

                marriage_data["shared_streak"] = marriage_data.get("shared_streak", 0) + 1
                baby_bonus = False
                if marriage_data["shared_streak"] % 5 == 0:
                    for uid in [_uid(marriage_data["user_id"]), _uid(marriage_data["partner_id"])]:
                        coll_data[uid]["baby"] = coll_data[uid].get("baby", 0) + 1
                    baby_bonus = True

                marriages[marriage_key] = marriage_data
                await save_json_async(MARRIAGE_FILE, marriages)
                await save_json_async(POINTS_FILE, points_data)
                await save_json_async(COLLECTIBLES_FILE, coll_data)

                return True, streak, base_points, shared_coll, None, (extra_points, extra_coll), baby_bonus, partner_status, partner_id, premium_flag

            points_data[user_id] = points_data.get(user_id, 0) + base_points
            if user_id not in coll_data:
                coll_data[user_id] = {}
            for c in chosen_collectibles:
                coll_data[user_id][c] = coll_data[user_id].get(c, 0) + 1

            marriages[marriage_key] = marriage_data
            await save_json_async(MARRIAGE_FILE, marriages)
            await save_json_async(POINTS_FILE, points_data)
            await save_json_async(COLLECTIBLES_FILE, coll_data)

            return True, streak, base_points, chosen_collectibles[0], None, None, None, partner_status, partner_id, premium_flag

        points_data[user_id] = points_data.get(user_id, 0) + base_points
        if user_id not in coll_data:
            coll_data[user_id] = {}
        for c in chosen_collectibles:
            coll_data[user_id][c] = coll_data[user_id].get(c, 0) + 1

        await save_json_async(DAILY_FILE, daily_data)
        await save_json_async(POINTS_FILE, points_data)
        await save_json_async(COLLECTIBLES_FILE, coll_data)

        return True, streak, base_points, chosen_collectibles[0], None, None, None, None, None, premium_flag

    @commands.hybrid_command(name="daily", description="Claim your daily coins and collectible")
    async def daily(self, ctx: commands.Context):
        (success, streak, points, collectible, remaining, marriage_bonus, baby_bonus,
         partner_status, partner_id, premium_bonus) = await self.claim_daily(ctx.author)
        user = ctx.author

        if success:
            msg = ""
            if points is not None:
                coll_emoji = COLLECTIBLE_EMOJIS.get(collectible, "🎁")
                msg += (
                    f"<:ac_coins:1400522330668794028> **{user.display_name}**, Here is your daily **{points} Coins**!\n"
                    f"<:ac_blank:1399434326591934515> You're on a **{streak} daily streak**!\n"
                    f"{coll_emoji} You received a **{collectible}**!\n"
                )
            if premium_bonus:
                msg += f"<a:ac_yay:1409934560699093054> Premium bonus reward of **25 Coins**\n\n"

            if marriage_bonus:
                extra_points, extra_coll = marriage_bonus
                partner_user = self.bot.get_user(int(partner_id)) or await self.bot.fetch_user(int(partner_id))
                msg += f"<a:ac_redheart:1399456300500389899> You and {partner_user.name} received **+{extra_points} coins** and a **{extra_coll}** collectible!\n"

            if baby_bonus:
                partner_user = self.bot.get_user(int(partner_id)) or await self.bot.fetch_user(int(partner_id))
                msg += f"<:ac_baby:1412496759640297572> You and {partner_user.name} made a **baby**!\n"

            if partner_status is not None and partner_id is not None:
                partner_user = self.bot.get_user(int(partner_id)) or await self.bot.fetch_user(int(partner_id))
                if partner_status:
                    msg += f"\nYour partner {partner_user.name} has already claimed their daily today!\n"
                else:
                    msg += f"\nYour partner {partner_user.name} has **NOT** claimed their daily yet.\n"

            embed = discord.Embed(
                description=msg,
                color=discord.Color.from_str("#ff6b6b")
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed.set_footer(text=f"Your next daily is in: {get_remaining_time()}")
            await ctx.reply(embed=embed, mention_author=False)

        else:
            msg = (
                f"<:ap_time:1382729675616555029> **{user.display_name}**, you already claimed your daily!\n\n"
            )
            if partner_status is not None and partner_id is not None:
                partner_user = self.bot.get_user(int(partner_id)) or await self.bot.fetch_user(int(partner_id))
                if partner_status:
                    msg += f"Your partner {partner_user.name} has already claimed their daily today!"
                else:
                    msg += f"Your partner {partner_user.name} has **NOT** claimed their daily yet."

            embed = discord.Embed(
                description=msg,
                color=discord.Color.red()
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed.set_footer(text=f"Come back in: {remaining}")
            await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(Daily(bot))
