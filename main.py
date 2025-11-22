import discord
from discord.ext import commands
import os
import asyncio
import datetime
import logging
import json
<<<<<<< HEAD
import requests  
=======
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
from dotenv import load_dotenv
from console_logger import DiscordLogHandler
from vote_remind import start_reminder_loop

<<<<<<< HEAD
load_dotenv()

=======
# Load environment variables
load_dotenv()

# Get values from .env
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_LOG_WEBHOOK")
RESTART_CHANNEL_ID = int(os.getenv("BOT_RESTART_CHANNEL_ID", 0))
GUILD_ID = int(os.getenv("MAIN_GUILD_ID", 0))

<<<<<<< HEAD
TOPGG_TOKEN = os.getenv("TOPGG_TOKEN")  
BOT_ID = os.getenv("BOT_ID")        

=======
# Prefix config
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
PREFIX_FILE = 'prefixes.json'
DEFAULT_PREFIX = 'a'

if not os.path.exists(PREFIX_FILE):
    with open(PREFIX_FILE, 'w') as f:
        json.dump({}, f)

def get_prefix(bot, message):
    if not message.guild:
        return [DEFAULT_PREFIX, DEFAULT_PREFIX + ' ']
    try:
        with open(PREFIX_FILE, 'r') as f:
            data = json.load(f)
        guild_prefix = data.get(str(message.guild.id), DEFAULT_PREFIX)
        if isinstance(guild_prefix, str):
            return [guild_prefix, guild_prefix + ' ']
<<<<<<< HEAD
=======
        # If it's a list
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
        return guild_prefix + [p + ' ' for p in guild_prefix]
    except:
        return [DEFAULT_PREFIX, DEFAULT_PREFIX + ' ']


<<<<<<< HEAD
=======
# Intents and bot setup
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.start_time = datetime.datetime.now(datetime.UTC)
<<<<<<< HEAD
bot.remove_command("help")


async def post_topgg_stats():
    if not TOPGG_TOKEN or not BOT_ID:
        logging.warning("⚠️ Top.gg token or bot ID missing. Skipping stats post.")
        return

    url = f"https://top.gg/api/bots/{BOT_ID}/stats"
    headers = {"Authorization": TOPGG_TOKEN, "Content-Type": "application/json"}
    data = {"server_count": len(bot.guilds)}

    try:
        r = requests.post(url, headers=headers, json=data)
        logging.info(f"📡 Posted Top.gg stats: {r.status_code} - {r.text}")
    except Exception as e:
        logging.error(f"❌ Failed to post Top.gg stats: {e}")

=======

# -------------------- DISCORD BOT EVENTS --------------------
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47

async def send_restart_message():
    await bot.wait_until_ready()
    await asyncio.sleep(2)
    if not RESTART_CHANNEL_ID:
        return
    channel = bot.get_channel(RESTART_CHANNEL_ID)
    if channel:
        try:
            await channel.send("<a:ap_uptime:1382717912120430702> **AuraColls** is back online!")
        except:
            pass

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} slash commands')
    except Exception as e:
        print(f'❌ Slash command sync error: {e}')
<<<<<<< HEAD

    await send_restart_message()
    await post_topgg_stats() 

@bot.event
async def on_guild_join(guild):
    await post_topgg_stats() 

@bot.event
async def on_guild_remove(guild):
    await post_topgg_stats() 


async def load_cogs():
    base_path = "cogs"

    reminder_path = f"{base_path}.reminder"
    try:
        if os.path.exists(os.path.join(base_path, "reminder.py")):
            await bot.load_extension(reminder_path)
            logging.info("✅ Loaded reminder cog first.")
    except Exception as e:
        logging.error(f"❌ Failed to load reminder cog: {e}")

    for file in os.listdir(base_path):
        if file.endswith(".py") and file != "reminder.py":
            module = f"{base_path}.{file[:-3]}"
            try:
                if module in bot.extensions:
                    await bot.unload_extension(module)
=======
    await send_restart_message()

# -------------------- DYNAMIC COG LOADER --------------------

async def load_cogs():
    base_path = "cogs"
    for file in os.listdir(base_path):
        if file.endswith(".py"):
            module = f"{base_path}.{file[:-3]}"
            try:
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
                await bot.load_extension(module)
                logging.info(f"✅ Loaded cog: {module}")
            except Exception as e:
                logging.error(f"❌ Failed to load cog {module}: {e}")

<<<<<<< HEAD

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.CommandNotFound, commands.CheckFailure, commands.CommandOnCooldown)):
        return
    raise error

async def main():
    await asyncio.sleep(5)
=======
                
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Silently ignore unknown commands
    raise error  # Raise others so they're logged or handled elsewhere
    
# -------------------- MAIN ENTRY --------------------

async def main():
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
    handler = DiscordLogHandler(webhook_url=WEBHOOK_URL)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)
    await handler.start()
    logging.info("🦵 Discord bot logging has started.")

    async with bot:
        await load_cogs()
<<<<<<< HEAD
        bot.loop.create_task(start_reminder_loop(bot))
=======
        bot.loop.create_task(start_reminder_loop(bot))  
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
        logging.info("🚀 Bot starting now...")
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
