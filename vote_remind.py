import json
import os
import datetime
import asyncio
import discord

REMIND_FILE = "vote_remind.json"


def load_reminders():
    if not os.path.exists(REMIND_FILE):
        with open(REMIND_FILE, "w") as f:
            json.dump({}, f)
    with open(REMIND_FILE, "r") as f:
        return json.load(f)


def save_reminders(data):
    with open(REMIND_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_to_reminder(user_id):
    """Add user to reminder with 14-hour cooldown."""
    data = load_reminders()
    user_id = str(user_id)
    next_vote_ts = int((datetime.datetime.utcnow() + datetime.timedelta(hours=13)).timestamp())
    data[user_id] = next_vote_ts
    save_reminders(data)


def is_on_cooldown(user_id):
    """Check if a user is still on vote cooldown."""
    data = load_reminders()
    user_id = str(user_id)
    if user_id not in data:
        return False

    next_time = datetime.datetime.utcfromtimestamp(data[user_id])
    return datetime.datetime.utcnow() < next_time


def get_cooldown_timestamp(user_id):
    """Return remaining cooldown timestamp (Unix) or 0 if ready."""
    data = load_reminders()
    user_id = str(user_id)
    return data.get(user_id, 0)


async def start_reminder_loop(bot):
    """Background loop to DM users when their cooldown expires."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        data = load_reminders()
        now = datetime.datetime.utcnow()
        to_remove = []

        for user_id, ts in data.items():
            remind_time = datetime.datetime.utcfromtimestamp(ts)
            if now >= remind_time:
                user = bot.get_user(int(user_id))
                if user:
                    try:
                        await user.send(
                            "<:ap_vote:1395506333834543144> Hey! It's time to vote for AuraColls again!\n"
                            "<https://top.gg/bot/1261363542867578910/vote>"
                        )
                    except discord.Forbidden:
                        pass
                to_remove.append(user_id)

        for user_id in to_remove:
            del data[user_id]

        save_reminders(data)
        await asyncio.sleep(60) 
