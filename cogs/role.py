# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

target_guild_id = 712581579351785503
target_role_id = 712592318208802820


class Role(commands.Cog):
    """The description for Role goes here."""

    def __init__(self, bot):
        self.bot = bot

    def has_role(self, member):
        for x in member.roles:
            if x.id == target_role_id:
                return True

        return False

    @commands.command()
    @commands.guild_only()
    async def add(self, ctx, member: discord.Member):
        if not self.has_role(ctx.author):
            await ctx.send('あなたはチャンネル管理者役職を持っていません！')
            return
        await member.add_roles(ctx.guild.get_role(target_role_id))
        await ctx.send('付与しました。')

    @commands.command()
    async def freeze(self, ctx):
        """全てのチャンネルを凍結させます。荒らしが来たときに有効です。"""
        if not self.has_role(self.bot.get_guild(target_guild_id).get_member(ctx.author.id)):
            await ctx.send('あなたはチャンネル管理者役職を持っていません！')
            return

        for channel in self.bot.get_guild(target_guild_id).text_channels:
            if channel.category and channel.category.id == 712584583996243999:
                continue
            await channel.edit(overwrites={channel.guild.default_role: discord.PermissionOverwrite(send_messages=False)})
        await self.bot.log(f'{ctx.author.mention}さんが凍結しました。')

    @commands.command()
    async def unfreeze(self, ctx):
        """全てのチャンネルの凍結を解除します。"""
        if not self.has_role(self.bot.get_guild(target_guild_id).get_member(ctx.author.id)):
            await ctx.send('あなたはチャンネル管理者役職を持っていません！')
            return

        for channel in self.bot.get_guild(target_guild_id).text_channels:
            if channel.category and channel.category.id == 712584583996243999:
                continue
            await channel.edit(overwrites={channel.guild.default_role: discord.PermissionOverwrite(send_messages=True)})
        await self.bot.log(f'{ctx.author.mention}さんが凍結を解除しました。')


def setup(bot):
    bot.add_cog(Role(bot))
