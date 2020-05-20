# -*- coding: utf-8 -*-

from discord.ext import commands
import discord

class Shiritori(commands.Cog):
    """The description for Shiritori goes here."""

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Shiritori(bot))
