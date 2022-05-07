#  -----------------------------------------------------------------------------
#   <calendar.py>
#    - A set of commands to manipulate the calendar.
#    --
#  -----------------------------------------------------------------------------
#   Version 0 (2022/05/07 11:47)
#    -
#  -----------------------------------------------------------------------------
#   (C) 2022 masahiro nishimura. All rights reserved.
#  -----------------------------------------------------------------------------

from discord.ext import commands
import discord


class calendarCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("テスト成功！")


async def setup(bot):
    await bot.add_cog(calendarCog(bot))
