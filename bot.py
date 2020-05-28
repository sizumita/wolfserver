from discord.ext import commands
import discord
import config
import pickle
target_guild_id = 712581579351785503
log_channel_id = 712587428426416149
notice_channel_id = 713729437371465820
msg = """
"""


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
        with open('more_vote.pickle', 'wb') as f:
            pickle.dump(self.get_cog("Vote").more_vote, f)
        with open('fake.pickle', 'wb') as f:
            pickle.dump(self.get_cog("Vote").fake_vote, f)
        with open('fake_counter.pickle', 'wb') as f:
            pickle.dump(self.get_cog("Vote").fake_counter, f)

        await super().close()

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))
        await self.notice('@everyone 付与されていないバグを消去しました。また、5ポイント補填しました。また、10ポイント消費するとななななんとBANをを回避できます ！')

    async def log(self, message, embed=None):
        if embed:
            channel = self.get_channel(log_channel_id)
            return await channel.send(embed=embed)
        channel = self.get_channel(log_channel_id)
        return await channel.send(message)

    async def notice(self, message, embed=None):
        channel = self.get_channel(notice_channel_id)
        if embed:
            return await channel.send(embed=embed)
        return await channel.send(message)

    async def on_member_remove(self, member):
        await self.log(f'{member.mention} さんはサーバーから退出したため追放されました。')
        await member.ban(reason='サーバーから退出したため', delete_message_days=0)


bot = Bot()

# write general commands here

if __name__ == '__main__':
    bot.run(config.token)
