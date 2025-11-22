import logging
import discord
from discord.ext import commands

LOG_CHANNEL_ID = 1415402768058810458 

logger = logging.getLogger(__name__)

class ShardLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._sent_ready_test = False

    async def send_log(self, message: str):
        """
        Safe send: try cached channel, otherwise wait until ready and fetch channel.
        On failure, log to console so you can debug.
        """
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel is None:
            if not self.bot.is_ready():
                try:
                    await self.bot.wait_until_ready()
                except Exception as e:
                    logger.warning(f"ShardLogger: wait_until_ready() failed: {e}")
            try:
                channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
            except discord.NotFound:
                logger.warning(f"ShardLogger: channel id {LOG_CHANNEL_ID} not found (NotFound).")
                return
            except discord.Forbidden:
                logger.warning(f"ShardLogger: cannot access channel {LOG_CHANNEL_ID} (Forbidden).")
                return
            except Exception as e:
                logger.exception(f"ShardLogger: failed to fetch channel {LOG_CHANNEL_ID}: {e}")
                return

        try:
            if isinstance(channel, (discord.TextChannel, discord.Thread, discord.VoiceChannel)):
                me = channel.guild.me or self.bot.user
                perms = channel.permissions_for(me)
                if not perms.send_messages:
                    logger.warning(f"ShardLogger: bot lacks send_messages permission in channel {LOG_CHANNEL_ID}.")
                    return
            await channel.send(message)
        except discord.Forbidden:
            logger.warning(f"ShardLogger: Forbidden to send in channel {LOG_CHANNEL_ID}.")
        except Exception as e:
            logger.exception(f"ShardLogger: error while sending log to channel {LOG_CHANNEL_ID}: {e}")

    def normalize_shard_id(self, shard_id):
        return 0 if shard_id is None else shard_id

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        sid = self.normalize_shard_id(shard_id)
        await self.send_log(f"<:ac_checkmark:1399650326201499798> Shard `{sid}` has connected to the gateway.")

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        sid = self.normalize_shard_id(shard_id)
        await self.send_log(f"<:ac_checkmark:1399650326201499798> Shard `{sid}` is ready.")

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        sid = self.normalize_shard_id(shard_id)
        await self.send_log(f"♻️ Shard `{sid}` has resumed session successfully.")

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        sid = self.normalize_shard_id(shard_id)
        await self.send_log(f"<:ac_crossmark:1399650396322005002> Shard `{sid}` session has been disconnected.")

    @commands.command(name="shardlogtest")
    @commands.is_owner()
    async def shardlogtest(self, ctx):
        """Owner-only test to ensure the ShardLogger can send to the channel."""
        await ctx.send("Sending test log to the configured log channel...")
        await self.send_log(f"Test: shard logger working. Triggered by {ctx.author} (id: {ctx.author.id}).")
        await ctx.send("Done — check the log channel (or check console warnings).")

async def setup(bot):
    await bot.add_cog(ShardLogger(bot))
