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
PREMIUM_FILE = "premium.json"
TRADABLE_FILE = "tradablecoll.json"
WORK_FILE = "work.json" 

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

NOTHING_TEXTS = [
    "You worked hard but found nothing this time...",
    "You tried... Better luck next time!"
    "Your efforts today didn’t pay off.",
    "Nothing to show for your work, maybe next time!",
    "You swing your hands wildly… and catch air.",
    "The universe laughs at your work attempt.",
    "You dug deep but found only dust.",
    "Your pockets remain empty. Better luck next time!",
    "You found absolutely nothing… except maybe disappointment.",
    "You stared on me… and i stared you back.",
    "The coins are hiding from you.",
    "You searched high and low… nothing.",
    "You were ready, but i say 'nope!'",
    "You chased shadows, caught nothing.",
    "Your hard work earned you… a sigh.",
    "You tried to impress me, but i ignored you.",
    "The collectibles are on vacation today.",
    "You almost found something, but it was a mirage.",
    "Your hands feel heavier from all that nothing.",
    "You hustled, but luck is on break.",
    "You were close… but not quite.",
    "Your effort is noted… but unrewarded.",
    "You dug, you mined… just air.",
    "The mine mocks you with emptiness.",
    "Your shovel hits air, not treasure.",
    "You worked so hard, even the dust applauds.",
    "You found a tiny pebble. Close enough?",
    "The treasure said: 'Maybe next time!'",
    "You gave it your all, still empty-handed.",
    "Coins are playing hide and seek… and winning.",
    "You look around… nothing moves, nothing shines.",
    "Your hard work is inspirational… for nothing.",
    "You tiptoed around, but found nothing.",
    "The collectibles giggled and hid from you.",
    "Your effort was heroic… for zero reward.",
    "You dug like a pro, found like a newbie.",
    "The void rewarded you with… nothing.",
    "Your hands are empty, your heart full of hope.",
    "You worked like a champ, got like a pauper.",
    "You searched everywhere… even in your imagination.",
    "Your effort echoes in the emptiness.",
    "You tried… the coins didn’t notice.",
    "You rolled up your sleeves… and found nothing.",
    "You were ready for anything… except this emptiness.",
    "The treasure map was blank today.",
    "You hustled… but only dust greets you.",
    "Your epic quest ended with… nothing.",
    "You gave it all, the universe gave you nada.",
    "Your pockets jingle… with nothing.",
    "You dug, mined, searched… got ghosted.",
    "You’re rich in spirit, poor in coins today.",
    "Even the shadows avoid your efforts.",
    "You tried to catch **100** <:ac_coins:1400522330668794028> coins… but it slipped away.",
    "Your work is legendary… for not finding anything."
]

COINS_TEXTS = [
    "You earned **{amount}** <:ac_coins:1400522330668794028> from your work!",
    "Your hard work paid off: **{amount}** <:ac_coins:1400522330668794028> collected!",
    "Success! **{amount}** <:ac_coins:1400522330668794028> have been added to your balance.",
    "Ka-ching! You just got **{amount}** <:ac_coins:1400522330668794028>!",
    "You mined some coins and found **{amount}** <:ac_coins:1400522330668794028> glittering pieces!",
    "Lucky you! **{amount}** <:ac_coins:1400522330668794028> found.",
    "Your effort brought in **{amount}** <:ac_coins:1400522330668794028>. Nice!",
    "You hit the jackpot and got **{amount}** <:ac_coins:1400522330668794028>!",
    "Coins rain down! You received **{amount}** <:ac_coins:1400522330668794028>.",
    "You worked smart and earned **{amount}** <:ac_coins:1400522330668794028>!",
    "Treasure hunt success: **{amount}** <:ac_coins:1400522330668794028> acquired!",
    "Your pockets jingle with **{amount}** <:ac_coins:1400522330668794028>!",
    "You collected **{amount}** <:ac_coins:1400522330668794028>. Feeling rich yet?",
    "Cha-ching! **{amount}** <:ac_coins:1400522330668794028> are yours.",
    "Gold rush! You got **{amount}** <:ac_coins:1400522330668794028>!",
    "You found **{amount}** <:ac_coins:1400522330668794028> hiding under the rocks!",
    "Coins sparkle in your hands: **{amount}** <:ac_coins:1400522330668794028> added!",
    "You dug deep and got **{amount}** <:ac_coins:1400522330668794028> shiny coins!",
    "Fortune smiles! **{amount}** <:ac_coins:1400522330668794028> have appeared.",
    "You hustled and earned **{amount}** <:ac_coins:1400522330668794028>!",
    "Work well done: **{amount}** <:ac_coins:1400522330668794028> collected.",
    "You earned **{amount}** <:ac_coins:1400522330668794028>. Spend wisely!",
    "A treasure chest opens! **{amount}** <:ac_coins:1400522330668794028> inside.",
    "You discovered **{amount}** <:ac_coins:1400522330668794028> in your adventure!",
    "You found **{amount}** <:ac_coins:1400522330668794028> while on your quest!",
    "Coins jingling! You got **{amount}** <:ac_coins:1400522330668794028>.",
    "You struck gold and earned **{amount}** <:ac_coins:1400522330668794028>!",
    "You worked like a champ and earned **{amount}** <:ac_coins:1400522330668794028>!",
    "Treasure found! **{amount}** <:ac_coins:1400522330668794028> are now yours.",
    "Your diligence paid off: **{amount}** <:ac_coins:1400522330668794028> received!",
    "You earned **{amount}** <:ac_coins:1400522330668794028>! Keep it up!",
    "Jackpot! **{amount}** <:ac_coins:1400522330668794028> have been added to you!",
    "Coins aplenty! You got **{amount}** <:ac_coins:1400522330668794028>.",
    "Your quest yields **{amount}** <:ac_coins:1400522330668794028>!",
    "You earned **{amount}** <:ac_coins:1400522330668794028> through sheer skill!",
    "You worked hard and gained **{amount}** <:ac_coins:1400522330668794028>!",
    "Your effort brings **{amount}** <:ac_coins:1400522330668794028> into your pocket!",
    "Lucky day! **{amount}** <:ac_coins:1400522330668794028> collected!",
    "Coins found: **{amount}** <:ac_coins:1400522330668794028> added to your stash!",
    "You discovered **{amount}** <:ac_coins:1400522330668794028> in the treasure pile!",
    "Hustle pays off: **{amount}** <:ac_coins:1400522330668794028> earned!",
    "Your hands are full of **{amount}** <:ac_coins:1400522330668794028>!",
    "Adventure reward: **{amount}** <:ac_coins:1400522330668794028> collected!",
    "You mined **{amount}** <:ac_coins:1400522330668794028> from the treasure vein!",
    "Coins incoming! **{amount}** <:ac_coins:1400522330668794028> now in your wallet.",
    "You found **{amount}** <:ac_coins:1400522330668794028>! Not bad!",
    "Hard work = **{amount}** <:ac_coins:1400522330668794028>! Good job!",
    "Treasure uncovered! **{amount}** <:ac_coins:1400522330668794028> obtained.",
    "You gained **{amount}** <:ac_coins:1400522330668794028> from your effort!",
    "Your mining paid off: **{amount}** <:ac_coins:1400522330668794028> received!"
]

COLLECTIBLE_TEXTS = [
    "Incredible! You found a collectible: **{item}**!",
    "Your work paid off with a rare collectible: **{item}**!",
    "Lucky day! **{item}** has been added to your collection.",
    "Wow! You discovered **{item}** while working!",
    "Fortune smiles upon you: **{item}** is yours!",
    "Amazing! **{item}** has joined your collection!",
    "You strike gold! **{item}** obtained!",
    "Your effort brings rewards: **{item}** collected!",
    "Unbelievable! **{item}** found in the wild!",
    "Congratulations! **{item}** has been added to your inventory!",
    "Jackpot! You stumbled upon **{item}**!",
    "Adventure success! **{item}** now belongs to you!",
    "Epic find! **{item}** collected successfully!",
    "You worked hard and discovered **{item}**!",
    "Treasure unlocked: **{item}** added!",
    "Lucky strike! **{item}** has been found!",
    "The cosmos favors you: **{item}** discovered!",
    "Your hands shake as you pick up **{item}**!",
    "Surprise reward! **{item}** is now yours!",
    "You found **{item}** hiding in plain sight!",
    "What a catch! **{item}** added to your collection!",
    "You earn a rare collectible: **{item}**!",
    "Your work pays off handsomely: **{item}**!",
    "Collectible alert! **{item}** obtained!",
    "You spotted something shiny: **{item}**!",
    "A rare gem appears! **{item}** now yours!",
    "Treasure hunting success: **{item}** collected!",
    "You uncover a hidden collectible: **{item}**!",
    "Fantastic! **{item}** has joined your stash!",
    "You worked smart and got rewarded: **{item}**!",
    "Magical discovery! **{item}** found!",
    "A lucky find: **{item}** added to your collection!",
    "Your work yields a special reward: **{item}**!",
    "You stumbled upon a treasure: **{item}**!",
    "Epic reward! **{item}** is now yours!",
    "You earned a collectible: **{item}**!",
    "Fortune favors your effort: **{item}** found!",
    "A rare item appears: **{item}** collected!",
    "You worked hard and got lucky: **{item}**!",
    "Surprise collectible! **{item}** has joined you!",
    "You found something special: **{item}**!",
    "Amazing luck! **{item}** is now yours!",
    "You discover a rare collectible: **{item}**!",
    "You earned **{item}** for your efforts!",
    "Your diligence pays off: **{item}** collected!",
    "Treasure found! **{item}** is added to your stash!",
    "You uncovered a collectible: **{item}**!",
    "Your work was rewarded with **{item}**!",
    "Lucky discovery! **{item}** found!",
    "You successfully added **{item}** to your collection!",
    "Your adventure brings **{item}** to your inventory!"
]


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coins_data = load_json(COINS_FILE)
        self.collectibles_data = load_json(COLLECTIBLES_FILE)
        self.premium_data = load_json(PREMIUM_FILE)
        self.tradable_data = load_json(TRADABLE_FILE)
        self.cooldowns_data = load_json(WORK_FILE)  

    def get_cooldown(self, user_id):
        """Return cooldown in seconds. 10 min for premium, 30 min regular."""
        users = self.premium_data.get("users", {})
        user = users.get(str(user_id))
        if user:
            try:
                expiry = datetime.fromisoformat(user["expiry"])
                if expiry > datetime.utcnow():
                    return 10 * 60  
            except Exception:
                pass
        return 30 * 60  

    async def reward_user(self, ctx, user_id):
        roll = random.randint(1, 100)
        if roll <= 25:
            msg = random.choice(NOTHING_TEXTS)
            embed = discord.Embed(
                description=msg,
                color=discord.Color.from_str("#ff6b6b")
            )

            if hasattr(ctx, "interaction") and ctx.interaction is not None:
                if ctx.interaction.response.is_done():
                    await ctx.followup.send(embed=embed)
                else:
                    await ctx.response.send_message(embed=embed)
            else:
                await ctx.send(embed=embed)


        elif roll <= 95:
            amount = random.randint(1, 10)
            coins = load_json(COINS_FILE)  
            coins[str(user_id)] = coins.get(str(user_id), 0) + amount
            save_json(COINS_FILE, coins)   
            self.coins_data = coins       
            msg = random.choice(COINS_TEXTS).format(amount=amount)
            embed = discord.Embed(
                description=msg,
                color=discord.Color.from_str("#ff6b6b")
            )

            if hasattr(ctx, "interaction") and ctx.interaction is not None:
                if ctx.interaction.response.is_done():
                    await ctx.followup.send(embed=embed)
                else:
                    await ctx.response.send_message(embed=embed)
            else:
                await ctx.send(embed=embed)

        else:

            if not self.tradable_data:
                await ctx.send("No tradable collectibles available!")
                return
            item_key = random.choice(list(self.tradable_data.keys()))
            item_data = self.tradable_data[item_key]
            emoji = item_data.get("emoji", "")
            name = item_data.get("name", item_key)
            display_name = f"{emoji} {name}"

            user_coll = self.collectibles_data.get(str(user_id), {})
            user_coll[item_key] = user_coll.get(item_key, 0) + 1
            self.collectibles_data[str(user_id)] = user_coll
            save_json(COLLECTIBLES_FILE, self.collectibles_data)

            msg = random.choice(COLLECTIBLE_TEXTS).format(item=display_name)
            embed = discord.Embed(
                description=msg,
                color=discord.Color.from_str("#ff6b6b")
            )

            if hasattr(ctx, "interaction") and ctx.interaction is not None:
                if ctx.interaction.response.is_done():
                    await ctx.followup.send(embed=embed)
                else:
                    await ctx.response.send_message(embed=embed)
            else:
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="work", description="Work to earn coins or collectibles!")
    async def work(self, ctx):
        user_id = ctx.author.id
        now = int(time.time())
        cd = self.get_cooldown(user_id)
        last = self.cooldowns_data.get(str(user_id), 0)

        if now - last < cd:
            retry_time = now + (cd - (now - last))
            embed = discord.Embed(
                title="<:ap_time:1382729675616555029> Slow Down!",
                description=(
                    f"You'll be able to use this command again <t:{retry_time}:R>\n\n"
                    f"The **default** cooldown is `30 minutes`\n"
                    f"The **premium** cooldown is `10 minutes`"
                ),
                color=discord.Color.default()
            )
            await ctx.send(embed=embed)
            return

        self.cooldowns_data[str(user_id)] = now
        save_json(WORK_FILE, self.cooldowns_data)

        await self.reward_user(ctx, user_id)

        self.bot.loop.create_task(
            add_reminder(
                user_id=user_id,
                category="work",
                name="Cooldown finished",
                channel_id=ctx.channel.id,
                message_id=ctx.message.id,
                delay=cd
            )
        )

async def setup(bot):
    await bot.add_cog(Work(bot))
