# -*- coding: utf-8 -*-

import discord
import datetime
import asyncio
from discord.ext import commands, tasks
from collections import Counter
from typing import Union
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
    async def vote(self, ctx, member: Union[discord.Member, discord.User]):
        """誰か一人を処刑します。名前かメンション、idで指定してください。"""
        if isinstance(member, discord.User):
            member = self.bot.get_guild(target_guild_id).get_member(member.id)

        if member.id == self.bot.user.id:
            await ctx.send('私を指定することはできません。')
            return
        changed = False
        before = None
        if ctx.author.id in self.vote_counter.keys():
            changed = True
            before = self.vote_counter[ctx.author.id]

        self.vote_counter[ctx.author.id] = member
        await ctx.send(f'ユーザー: {member} を追放先に指定しました。')
        if changed:
            await self.bot.log(f'あるユーザーが 追放先を{before.mention}さんから{member.mention}さんに変更しました！')
            return

        await self.bot.log(f'追放先に{member.mention} さんがあるユーザーによって選ばれました！')
        c = Counter(self.vote_counter.values())
        max_member, max_value = c.most_common()[0]
        await self.bot.log(f'現在、{max_value}票で{max_member.mention}さんが一位です.')

    @tasks.loop(hours=24)
    async def ban_task(self):
        c = Counter(self.vote_counter.values())
        max_value = c.most_common()[0][1]
        for value, count in c.most_common():
            if count == max_value:
                await self.bot.log(f'{value.mention} ({value}) さんが得票数{count}で追放されました。')
                try:
                    await value.send(f'あなたは{count}票獲得し、追放されました。')
                except Exception:
                    pass
                try:
                    await value.ban(reason=f'{count}票を獲得したため、banされました。')
                except Exception:
                    pass
        self.vote_counter = {}


def setup(bot):
    bot.add_cog(Vote(bot))
