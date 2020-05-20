# -*- coding: utf-8 -*-

import discord
import datetime
import asyncio
from discord.ext import commands, tasks
from collections import Counter
log_channel_id = 712587428426416149
target_guild_id = 712581579351785503


class Vote(commands.Cog):
    """The description for Vote goes here."""

    def __init__(self, bot):
        self.bot = bot
        self.vote_counter = {}
        self.bot.loop.create_task(self.setup())

    async def setup(self):
        now = datetime.datetime.now()
        next_time = datetime.datetime(year=now.year, month=now.month, day=now.day) + datetime.timedelta(days=1)
        await asyncio.sleep(next_time.timestamp() - now.timestamp())
        self.ban_task.start()

    @commands.command()
    async def vote(self, ctx, member: discord.Member):
        """誰か一人を処刑します。名前かメンション、idで指定してください。"""
        if member.id == ctx.guild.me.id:
            await ctx.send('私を指定することはできません。')
            return

        self.vote_counter[ctx.author.id] = member
        await ctx.send(f'ユーザー: {member} を追放先に指定しました。')

    @tasks.loop(hours=24)
    async def ban_task(self):
        log_channel = self.bot.get_channel(log_channel_id)
        guild = self.bot.get_guild(target_guild_id)
        c = Counter(self.vote_counter.values())
        max_value = c.most_common()[0][1]
        for value, count in c.most_common():
            if count == max_value:
                await log_channel.send(f'{value.mention} ({value}) さんが得票数{count}で追放されました。')
                try:
                    await value.send(f'あなたは{count}票獲得し、追放されました。')
                except Exception:
                    pass
                try:
                    await value.ban(reason=f'{count}票を獲得したため、banされました。', delete_message_days=0)
                except Exception:
                    pass
        for member in guild.members:
            if member.bot:
                continue
            if member.id not in self.vote_counter.keys():
                await log_channel.send(f'{member.mention} ({member}) さんは投票しなかったため、追放されました。')
                try:
                    await member.send(f'あなたは投票しなかったため、追放されました。')
                except Exception:
                    pass
                try:
                    await member.ban(reason=f'投票しなかったため、banされました。', delete_message_days=0)
                except Exception:
                    pass
        self.vote_counter = {}


def setup(bot):
    bot.add_cog(Vote(bot))
