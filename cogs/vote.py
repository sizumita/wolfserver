# -*- coding: utf-8 -*-

import asyncio
import datetime
from collections import Counter
from typing import Union
import pickle
import discord
from discord.ext import commands, tasks

target_guild_id = 712581579351785503


class Vote(commands.Cog):
    """The description for Vote goes here."""

    def __init__(self, bot):
        self.bot = bot
        self.vote_counter = {}
        self.bot.loop.create_task(self.setup())
        self.bot.loop.create_task(self.setup2())
        try:
            with open('vote.pickle', 'rb') as f:
                self.vote_counter = pickle.load(f)
        except FileNotFoundError:
            pass

    async def setup(self):
        now = datetime.datetime.now()
        next_time = datetime.datetime(year=now.year, month=now.month, day=now.day) + datetime.timedelta(days=1)
        await asyncio.sleep(next_time.timestamp() - now.timestamp())
        self.ban_task.start()

    async def setup2(self):
        now = datetime.datetime.now()
        next_time = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=18)
        await asyncio.sleep(next_time.timestamp() - now.timestamp())
        self.notice_task.start()

    @tasks.loop(hours=24)
    async def notice_task(self):
        guild = self.bot.get_guild(target_guild_id)
        for member in guild.members:
            if member.id in self.vote_counter.keys():
                continue
            try:
                await member.send("投票が未完了です。")
            except Exception:
                await self.bot.log(f"{member.mention} 投票が未完了です。（DMへの送信が失敗したので、こちらに送信されました。）")

    async def ranking(self):
        embed = discord.Embed(title="投票数ランキング", description="各ユーザーの投票数ランキングを表示します")
        c = Counter(self.vote_counter.values())
        i = 1
        for user, count in c.most_common(10):
            embed.add_field(name=f"{i}位", value=f"{user.mention}: {count}票")
            i += 1
        await self.bot.log('', embed=embed)

    @commands.command()
    async def vote(self, ctx, member: Union[discord.Member, discord.User]):
        """誰か一人を処刑します。名前かメンション、idで指定してください。"""
        if isinstance(member, discord.User):
            member = self.bot.get_guild(target_guild_id).get_member(member.id)

        if member is None:
            await ctx.send("そんな人いないよ！")

        if member.bot:
            await ctx.send("Botを指定することはできません。")
            return
        changed = False
        if ctx.author.id in self.vote_counter.keys():
            changed = True
            before = self.vote_counter[ctx.author.id]

        self.vote_counter[ctx.author.id] = member
        await ctx.send(f"ユーザー: {member} を追放先に指定しました。")
        if changed:
            msg = await self.bot.log("投票")
            await msg.edit(content=f"あるユーザーが 追放先を{before.mention}さんから{member.mention}さんに変更しました！")
            await self.ranking()
            return

        msg = await self.bot.log("投票")
        await msg.edit(content=f"追放先に{member.mention} さんがあるユーザーによって選ばれました！")
        await self.ranking()

    @tasks.loop(hours=24)
    async def ban_task(self):
        now = datetime.datetime.now()
        c = Counter(self.vote_counter.values())
        max_value = c.most_common()[0][1]
        for value, count in c.most_common():
            if count == max_value:
                await self.bot.log(f'{value.mention} ({value}) さんが得票数{count}で追放されました。')
                try:
                    await value.send(f'あなたは{count}票獲得したため、追放されました。\n追放先のチャットはこちら： https://discord.gg/XdGRaAn')
                except Exception:
                    pass
                try:
                    await value.ban(reason=f'{count}票を獲得したため、banされました。', delete_message_days=0)
                except Exception:
                    pass

        guild = self.bot.get_guild(target_guild_id)

        for member in guild.members:
            if member.bot or member.id in self.vote_counter.keys():
                continue
            if now.timestamp() - member.joined_at.timestamp() <= 24 * 60 * 60:
                continue
            await self.bot.log(f"{member.mention} ({member}) さんは投票しなかったため、追放されました。")
            try:
                await member.send("あなたは投票しなかったため、追放されました。\n追放先のチャットはこちら： https://discord.gg/XdGRaAn")
            except Exception:
                pass
            try:
                await member.ban(reason="投票しなかったため、banされました。", delete_message_days=0)
            except Exception:
                pass
        self.vote_counter = {}


def setup(bot):
    bot.add_cog(Vote(bot))
