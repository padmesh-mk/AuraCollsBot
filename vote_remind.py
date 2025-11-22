<<<<<<< HEAD
=======
# vote_remind.py
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
import json
import os
import datetime
import asyncio
<<<<<<< HEAD
import discord

REMIND_FILE = "vote_remind.json"


=======
import discord  # Make sure you have this import

REMIND_FILE = "vote_remind.json"

>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
def load_reminders():
    if not os.path.exists(REMIND_FILE):
        with open(REMIND_FILE, "w") as f:
            json.dump({}, f)
    with open(REMIND_FILE, "r") as f:
        return json.load(f)

<<<<<<< HEAD

=======
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
def save_reminders(data):
    with open(REMIND_FILE, "w") as f:
        json.dump(data, f, indent=4)

<<<<<<< HEAD

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
=======
def add_to_reminder(user_id):
    data = load_reminders()
    # Store as Unix timestamp (int)
    next_vote = int((datetime.datetime.utcnow() + datetime.timedelta(hours=12)).timestamp())
    data[user_id] = next_vote
    save_reminders(data)

def is_on_cooldown(user_id):
    data = load_reminders()
    if user_id not in data:
        return False

    reminder = data[user_id]
    # Parse both string and int formats
    try:
        if isinstance(reminder, int):
            next_time = datetime.datetime.utcfromtimestamp(reminder)
        else:
            next_time = datetime.datetime.strptime(reminder, "%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return False

    return datetime.datetime.utcnow() < next_time

async def start_reminder_loop(bot):
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
    await bot.wait_until_ready()
    while not bot.is_closed():
        data = load_reminders()
        now = datetime.datetime.utcnow()
        to_remove = []

<<<<<<< HEAD
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
=======
        for user_id, reminder in data.items():
            try:
                # Handle both string and int formats
                if isinstance(reminder, int):
                    remind_time = datetime.datetime.utcfromtimestamp(reminder)
                else:
                    remind_time = datetime.datetime.strptime(reminder, "%Y-%m-%d %H:%M:%S UTC")

                if now >= remind_time:
                    user = bot.get_user(int(user_id))
                    if user:
                        try:
                            await user.send("<:ap_vote:1395506333834543144> Hey! It's time to vote for AuraColl again!\nVote using `avote` or `/vote`.")
                        except discord.Forbidden:
                            pass  # Can't DM user
                    to_remove.append(user_id)

            except Exception as e:
                print(f"Error handling reminder for {user_id}: {e}")
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47

        for user_id in to_remove:
            del data[user_id]

        save_reminders(data)
<<<<<<< HEAD
        await asyncio.sleep(60) 
=======
        await asyncio.sleep(60)  # Check every minute
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
