import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import random
import io


class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_pfp(self, user: discord.User):
        """Fetch user avatar and return as PIL image."""
        async with aiohttp.ClientSession() as session:
            async with session.get(user.avatar.url) as resp:
                avatar_bytes = await resp.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
        return avatar

    def circular_crop(self, image, size=(200, 200)):
        """Crop image into a circle."""
        image = image.resize(size)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        result = Image.new("RGBA", size)
        result.paste(image, (0, 0), mask=mask)
        return result

    def generate_message(self, percent: int):
        """Choose random message based on percentage."""
        messages = {
            "low": [
                "Oof... better luck next time!",
                "Even Google Maps couldn’t find the chemistry here",
                "This ship sank before it even touched water",
                "Bro, even oil and water mix better than you two",
                "The heart meter said, try friendship next time",
                "Cupid looked at you two and said *nah fam*",
                "You two together? Netflix would call it a horror series",
                "Honestly… Discord lag has more spark than this pair.",
                "Even your WiFi has a stronger connection than this."
            ],
            "mid": [
                "There’s some sparks here!",
                "Could be something, could be nothing",
                "You're halfway to a love story!",
                "It’s giving *situationship* vibes.",
                "There’s chemistry… but it’s the kind you failed in high school.",
                "Not enemies… not lovers… just awkward energy.",
                "This is the ‘Are we dating?’ ship where even Discord mods get confused.",
            ],
            "high": [
                "Ohhh… sparks are flying, someone get the fire extinguisher.",
                "Not full soulmate vibes, but definitely Netflix & chill material.",
                "Y’all give *‘will they, won’t they’* romance anime energy.",
                "Lowkey… I’d third-wheel this.",
                "You two are like that couple who swear they’re just friends, but everyone knows.",
                "This feels like a soft-launch relationship post on Insta.",
                "One wrong move away from a enemies-to-lovers plotline.",
                "It’s not true love yet… but it’s definitely giving late-night Discord calls."
            ],
            "vhigh": [
                "Forget shipping, this is a full-on marriage certificate waiting to happen.",
                "You two are basically the reason rom-coms exist.",
                "If love were a leaderboard, you’d be rank #1 with no competition.",
                "This isn’t a ship… it’s a Titanic, and no iceberg’s breaking it.",
                "Cupid saw this and retired — his job’s done.",
                "This is soulmate DLC, not just base game love.",
                "Even Disney would call this unrealistic.",
                "You two are proof fanfiction sometimes comes true.",
                "The stars aligned, the planets clapped, and boom: soulmate energy.",
                "This isn’t just endgame… this is the game."
            ]
        }

        if percent < 25:
            return random.choice(messages["low"])
        elif percent < 50:
            return random.choice(messages["mid"])
        elif percent < 75:
            return random.choice(messages["high"])
        else:
            return random.choice(messages["vhigh"])

    def draw_full_heart(self, percent: int, size=(200, 200)):
        """Draws a solid red heart with percentage text."""
        w, h = size
        img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        def heart_polygon(scale=1.0):
            t = [i * 0.01 for i in range(628)]
            x = [16 * (pow(__import__("math").sin(val), 3)) for val in t]
            y = [13 * __import__("math").cos(val) - 5 * __import__("math").cos(2 * val) -
                 2 * __import__("math").cos(3 * val) - __import__("math").cos(4 * val) for val in t]
            min_x, max_x = min(x), max(x)
            min_y, max_y = min(y), max(y)
            x = [(xx - min_x) / (max_x - min_x) * (w - 20) + 10 for xx in x]
            y = [(yy - min_y) / (max_y - min_y) * (h - 20) + 10 for yy in y]
            y = [h - yy for yy in y]
            return list(zip(x, y))

        draw.polygon(heart_polygon(), fill=(255, 0, 80, 255))

        font = ImageFont.truetype("DejaVuSans.ttf", 48)
        text = f"{percent}%"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        tw = text_bbox[2] - text_bbox[0]
        th = text_bbox[3] - text_bbox[1]
        tx = (w - tw) // 2
        ty = (h - th) // 2 - 15 
        draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

        return img

    async def create_ship_image(self, user1: discord.User, user2: discord.User, percent: int):
        """Generate ship image with two users and solid heart in center."""
        pfp1 = await self.get_pfp(user1)
        pfp2 = await self.get_pfp(user2)

        pfp1 = self.circular_crop(pfp1)
        pfp2 = self.circular_crop(pfp2)

        canvas = Image.new("RGBA", (700, 300), (255, 255, 255, 0))
        draw = ImageDraw.Draw(canvas)

        top_color = (255, 107, 107, 255)
        bottom_color = (255, 107, 107, 0)
        for y in range(300):
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * (y / 300))
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * (y / 300))
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * (y / 300))
            a = int(top_color[3] + (bottom_color[3] - top_color[3]) * (y / 300))
            draw.line([(0, y), (700, y)], fill=(r, g, b, a))

        canvas.paste(pfp1, (50, 50), pfp1)
        canvas.paste(pfp2, (450, 50), pfp2)

        heart_img = self.draw_full_heart(percent, size=(200, 200))
        canvas.paste(heart_img, (250, 50), heart_img)

        buffer = io.BytesIO()
        canvas.save(buffer, "PNG")
        buffer.seek(0)
        return buffer

    @commands.hybrid_command(name="ship")
    async def ship(self, ctx, user1: discord.User, user2: discord.User = None):
        """Ship two users together with a cute image."""
        if not user1:
            return await ctx.reply("<:ac_crossmark:1399650396322005002> You need to mention at least one user to ship!")
        if user2 is None:
            user2 = ctx.author

        percent = random.randint(0, 100)
        message = self.generate_message(percent)
        image = await self.create_ship_image(user1, user2, percent)

        file = discord.File(image, "ship.png")
        embed = discord.Embed(
            title=f"<a:ac_redheart:1399456300500389899> Shipping {user1.display_name} & {user2.display_name}",
            description=f"**{message}**",
            color=discord.Color.pink()
        )
        embed.set_image(url="attachment://ship.png")

        await ctx.send(content=f"{user1.mention} {user2.mention}",file=file, embed=embed)


async def setup(bot):
    await bot.add_cog(Ship(bot))
