# -*- coding: utf-8 -*-

import asyncio
import datetime

from discord.ext import commands, tasks


class Shiritori(commands.Cog):
    """The description for Shiritori goes here."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup())
        self.shiritori_tango = []

    async def setup(self):
        now = datetime.datetime.now()
        next_time = datetime.datetime(year=now.year, month=now.month, day=now.day) + datetime.timedelta(days=1)
        await asyncio.sleep(next_time.timestamp() - now.timestamp())

    @tasks.loop(hours=24)
    async def clean_task(self):
        self.shiritori_tango = []


def setup(bot):
    bot.add_cog(Shiritori(bot))
