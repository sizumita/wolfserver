from discord.ext import commands
import discord
import config
import pickle
target_guild_id = 712581579351785503
log_channel_id = 712587428426416149


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), **kwargs)
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(cog, exc))

    async def close(self):
        with open('vote.pickle', 'wb') as f:
            pickle.dump(self.get_cog("Vote").vote_counter, f)
        with open('guess.pickle', 'wb') as f:
            pickle.dump(self.get_cog("Vote").guess_counter, f)
        with open('guess_users.pickle', 'wb') as f:
            pickle.dump(self.get_cog("Vote").guess_users, f)

        await super().close()

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))

    async def log(self, message, embed=None):
        if embed:
            channel = self.get_channel(log_channel_id)
            return await channel.send(embed=embed)
        channel = self.get_channel(log_channel_id)
        return await channel.send(message)


bot = Bot()

# write general commands here

if __name__ == '__main__':
    bot.run(config.token)
