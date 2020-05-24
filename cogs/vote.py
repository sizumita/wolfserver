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
        self.guess_counter = {}
        self.guess_users = {}
        try:
            with open('guess.pickle', 'rb') as f:
                self.guess_counter = pickle.load(f)
        except FileNotFoundError:
            pass
        try:
            with open('guess_users.pickle', 'rb') as f:
                self.guess_users = pickle.load(f)
        except FileNotFoundError:
            pass
        self.more_vote = {}
        try:
            with open('more_vote.pickle', 'rb') as f:
                self.more_vote = pickle.load(f)
        except FileNotFoundError:
            pass
        self.fake_vote = {}
        try:
            with open('fake.pickle', 'rb') as f:
                self.fake_vote = pickle.load(f)
        except FileNotFoundError:
            pass
        self.fake_counter = {}
        try:
            with open('fake_counter.pickle', 'rb') as f:
                self.fake_counter = pickle.load(f)
        except FileNotFoundError:
            pass

    def get_point(self, user_id):
        if user_id in self.guess_counter.keys():
            return self.guess_counter[user_id]
        self.guess_counter[user_id] = 10
        return self.guess_counter[user_id]

    def get_fake_count(self, user_id):
        if user_id in self.fake_counter.keys():
            return self.fake_counter[user_id]
        self.fake_counter[user_id] = 0
        return self.fake_counter[user_id]

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

    def get_vote_vounter(self, include_fake=True):
        all_ = list(self.vote_counter.values()) + list(self.more_vote.values())
        if include_fake:
            _ = []
            for key, value in self.fake_vote.items():
                for x in range(value):
                    _.append(key)
            all_ += _
        c = Counter(all_)
        return c

    async def ranking(self):
        embed = discord.Embed(title="投票数ランキング", description="各ユーザーの投票数ランキングを表示します")
        c = self.get_vote_vounter()
        i = 1
        for user_id, count in c.most_common(10):
            user = self.bot.get_user(user_id)
            embed.add_field(name=f"{i}位", value=f"{user.mention}: {count}票")
            i += 1
        await self.bot.log('', embed=embed)

    @commands.command()
    async def real(self, ctx):
        """本当"""
        if self.get_point(ctx.author.id) < 2:
            await ctx.send(f'ポイントが足りません。({self.get_point(ctx.author.id)} < 2)')
            return
        self.guess_counter[ctx.author.id] -= 2
        embed = discord.Embed(title="投票数ランキング", description="各ユーザーの投票数ランキングを表示します")
        c = self.get_vote_vounter(False)
        i = 1
        for user_id, count in c.most_common(10):
            user = self.bot.get_user(user_id)
            embed.add_field(name=f"{i}位", value=f"{user.mention}: {count}票")
            i += 1
        await ctx.author.send(embed=embed)

    @commands.command()
    async def fake(self, ctx, member: Union[discord.Member, discord.User]):
        """嘘投票"""
        if isinstance(member, discord.User):
            member = self.bot.get_guild(target_guild_id).get_member(member.id)
        if member is None:
            await ctx.send("そんな人いないよ！")
            return
        if self.get_fake_count(ctx.author.id) != 1:
            self.fake_counter[ctx.author.id] += 1
        else:
            if self.get_point(ctx.author.id) < 1:
                await ctx.send(f'ポイントが足りません。({self.get_point(ctx.author.id)} < 1)')
                return
            self.guess_counter[ctx.author.id] -= 1
        if member.id not in self.fake_vote.keys():
            self.fake_vote[member.id] = 0
        self.fake_vote[member.id] += 1
        await ctx.send('完了')
        msg = await self.bot.log("投票")
        await msg.edit(content=f"追放先に{member.mention} さんがあるユーザーによって選ばれました！")
        await self.ranking()

    @commands.command()
    async def more(self, ctx, member: Union[discord.Member, discord.User]):
        """追加の投票"""
        if isinstance(member, discord.User):
            member = self.bot.get_guild(target_guild_id).get_member(member.id)

        if member is None:
            await ctx.send("そんな人いないよ！")
            return
        if self.get_point(ctx.author.id) < 10:
            await ctx.send(f'ポイントが足りません。({self.get_point(ctx.author.id)} < 10)')
            return
        if ctx.author.id in self.more_vote.keys():
            before = self.bot.get_user(self.more_vote[ctx.author.id])
            self.more_vote[ctx.author.id] = member.id
            await ctx.send(f"ユーザー: {member} を追加の追放先に指定しました。")
            msg = await self.bot.log('投票')
            await msg.edit(content=f"あるユーザーが 追放先を{before.mention}さんから{member.mention}さんに変更しました！")
            return
        self.guess_counter[ctx.author.id] -= 10
        self.more_vote[ctx.author.id] = member.id
        await ctx.send(f"ユーザー: {member} を追加の追放先に指定しました。")
        msg = await self.bot.log("投票")
        await msg.edit(content=f"追放先に{member.mention} さんがあるユーザーによって選ばれました！")
        await self.ranking()

    @commands.command()
    async def vote(self, ctx, member: Union[discord.Member, discord.User]):
        """誰か一人を処刑します。名前かメンション、idで指定してください。"""
        if isinstance(member, discord.User):
            member = self.bot.get_guild(target_guild_id).get_member(member.id)

        if member is None:
            await ctx.send("そんな人いないよ！")
            return
        if member.bot:
            await ctx.send("Botを指定することはできません。")
            return
        changed = False
        if ctx.author.id in self.vote_counter.keys():
            changed = True
            before = self.bot.get_user(self.vote_counter[ctx.author.id])

        self.vote_counter[ctx.author.id] = member.id
        await ctx.send(f"ユーザー: {member} を追放先に指定しました。")
        if changed:
            msg = await self.bot.log("投票")
            await msg.edit(content=f"あるユーザーが 追放先を{before.mention}さんから{member.mention}さんに変更しました！")
            await self.ranking()
            return

        msg = await self.bot.log("投票")
        await msg.edit(content=f"追放先に{member.mention} さんがあるユーザーによって選ばれました！")
        await self.ranking()

    @commands.command()
    async def guess(self, ctx, member: Union[discord.Member, discord.User]):
        if isinstance(member, discord.User):
            member = self.bot.get_guild(target_guild_id).get_member(member.id)
        if member is None:
            await ctx.send("そんな人いないよ！")
            return
        if member.bot:
            await ctx.send("Botを指定することはできません。")
            return
        if ctx.author.id in self.guess_users.keys():
            await ctx.send('もうあなたは予想しています！')
            return
        self.guess_users[ctx.author.id] = member.id
        if ctx.author.id not in self.guess_counter.keys():
            self.guess_counter[ctx.author.id] = 10
        msg = await ctx.send('結果')
        await msg.edit(content=f'{member.mention}さんを追放されるユーザーだと予想しました！')
        msg = await self.bot.log('予想')
        await msg.edit(content=f'あるユーザーが{member.mention}さんが追放されるユーザーだと予想しました。')

    @commands.command()
    async def point(self, ctx):
        await ctx.send(f'{self.get_point(ctx.author.id)}ポイント')

    @tasks.loop(hours=24)
    async def ban_task(self):
        now = datetime.datetime.now()
        c = self.get_vote_vounter(False)
        guild = self.bot.get_guild(target_guild_id)
        max_value = c.most_common()[0][1]
        banned_users_id = []
        for value, count in c.most_common():
            banned_users_id.append(value)
            value = guild.get_member(value)
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
        self.more_vote = {}
        for guess_user_id, guessed_user_id in self.guess_users.items():
            if guess_user_id in banned_users_id:
                continue
            if guessed_user_id in banned_users_id:
                member = guild.get_member(guess_user_id)
                await self.bot.log(f'{member.mention} さん、おめでとうございます。見事予想が当たりました。')
                self.guess_counter[guess_user_id] += 1
        self.guess_users = {}
        self.fake_counter = {}
        self.fake_vote = {}


def setup(bot):
    bot.add_cog(Vote(bot))
