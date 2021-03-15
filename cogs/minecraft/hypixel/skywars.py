"""
MIT License

Copyright (c) 2020 Myer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
from discord.ext import commands, menus


class Skywars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.icon = "https://static.myer.wtf/hypixel/skywars.png"

    @commands.group(aliases=["sw"], invoke_without_command=True)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    async def skywars(self, ctx, query=None):
        player = await ctx.bot.hypixel.player.get(ctx=ctx, query=query)
        stats = (
            self.get_stats_embed(player),
            self.get_stats_embed(player, player.skywars.insane.solo),
            self.get_stats_embed(player, player.skywars.insane.doubles),
            self.get_stats_embed(player, player.skywars.normal.solo),
            self.get_stats_embed(player, player.skywars.normal.doubles)
        )
        wlr = (
            self.get_wlr_embed(player),
            self.get_wlr_embed(player, player.skywars.insane.solo),
            self.get_wlr_embed(player, player.skywars.insane.doubles),
            self.get_wlr_embed(player, player.skywars.normal.solo),
            self.get_wlr_embed(player, player.skywars.normal.doubles)
        )
        kdr = (
            self.get_kdr_embed(player),
            self.get_kdr_embed(player, player.skywars.insane.solo),
            self.get_kdr_embed(player, player.skywars.insane.doubles),
            self.get_kdr_embed(player, player.skywars.normal.solo),
            self.get_kdr_embed(player, player.skywars.normal.doubles)
        )
        stats = SkywarsMenu(stats, wlr, kdr)
        await stats.start(ctx)

    @staticmethod
    def get_description(mode):
        if hasattr(mode, "games_played"):
            return f"Winstreak: {mode.winstreak}\n" \
                   f"Games Played: {mode.games_played:,d}"
        else:
            return f"Winstreak: {mode.winstreak}"

    def get_stats_embed(self, player, mode=None):
        if not mode:
            mode = player.skywars  # overall stats
        return discord.Embed(
            color=player.skywars.prestige.color,
            title=f"[{player.skywars.prestige.star}{self.bot.static.star}] {player.display}",
            description=self.get_description(mode)
        ).add_field(
            name="Kills",
            value=f"{mode.kills.kills:,d}"
        ).add_field(
            name="Deaths",
            value=f"{mode.kills.deaths:,d}"
        ).add_field(
            name="K/D",
            value=mode.kills.ratio.ratio
        ).add_field(
            name="Wins",
            value=f"{mode.wins.wins:,d}"
        ).add_field(
            name="Losses",
            value=f"{mode.wins.losses:,d}"
        ).add_field(
            name="W/L",
            value=mode.wins.ratio.ratio
        ).set_author(
            name=f"Currently Viewing: {mode}",
            icon_url=self.icon
        )

    def get_wlr_embed(self, player, mode=None):
        if not mode:
            mode = player.skywars  # overall
        return discord.Embed(
            color=player.skywars.prestige.color,
            title=f"[{player.skywars.prestige.star}{self.bot.static.star}] {player.display}",
        ).add_field(
            name="Wins",
            value=f"{mode.wins.wins:,d}"
        ).add_field(
            name="Losses",
            value=f"{mode.wins.losses:,d}"
        ).add_field(
            name="W/L",
            value=mode.wins.ratio.ratio
        ).add_field(
            name=f"To {mode.wins.ratio.next} WLR",
            value=f"{mode.wins.ratio.increase():,d} needed"
        ).set_author(
            name=f"Currently Viewing: {mode} WLR",
            icon_url=self.icon
        )

    def get_kdr_embed(self, player, mode=None):
        if not mode:
            mode = player.skywars  # overall
        return discord.Embed(
            color=player.skywars.prestige.color,
            title=f"[{player.skywars.prestige.star}{self.bot.static.star}] {player.display}",
        ).add_field(
            name="Kills",
            value=f"{mode.kills.kills:,d}"
        ).add_field(
            name="Deaths",
            value=f"{mode.kills.deaths:,d}"
        ).add_field(
            name="K/D",
            value=mode.kills.ratio.ratio
        ).add_field(
            name=f"To {mode.kills.ratio.next} KDR",
            value=f"{mode.kills.ratio.increase():,d} needed"
        ).set_author(
            name=f"Currently Viewing: {mode} KDR",
            icon_url=self.icon
        )


class SkywarsMenu(menus.Menu):
    def __init__(self, stats, wlr, kdr):
        super().__init__(timeout=300.0)
        self.stats = stats
        self.wlr = wlr
        self.kdr = kdr
        self.index = 0
        self.display = stats  # default display mode is stats

    def increment_index(self):
        if abs(self.index + 1) > len(self.display) - 1:
            self.index = 0  # loop back
        else:
            self.index += 1

    def decrement_index(self):
        if abs(self.index - 1) > len(self.display) - 1:
            self.index = 0  # loop back
        else:
            self.index -= 1

    async def send_initial_message(self, ctx, channel):
        return await ctx.reply(embed=self.display[self.index])

    @menus.button("\u21A9")
    async def on_first(self, payload):
        return await self.message.edit(embed=self.display[0])

    @menus.button("\u2B05")
    async def on_arrow_backwards(self, payload):
        self.decrement_index()
        return await self.message.edit(embed=self.display[self.index])

    @menus.button("\u23F9")
    async def on_stop(self, payload):
        self.stop()

    @menus.button("\u27A1")
    async def on_arrow_forward(self, payload):
        self.increment_index()
        return await self.message.edit(embed=self.display[self.index])

    @menus.button("\u21AA")
    async def on_arrow_last(self, payload):
        return await self.message.edit(embed=self.display[-1])

    @menus.button("<:stats:795017651277135883>")
    async def on_stats(self, payload):
        self.display = self.stats
        return await self.message.edit(embed=self.display[self.index])

    @menus.button("<:kdr:802191344377528401>")
    async def on_kdr(self, payload):
        self.display = self.kdr
        return await self.message.edit(embed=self.display[self.index])

    @menus.button("<:wlr:795017651726450758>")
    async def on_wlr(self, payload):
        self.display = self.wlr
        return await self.message.edit(embed=self.display[self.index])


def setup(bot):
    bot.add_cog(Skywars(bot))
    print("COGS > Reloaded cogs.minecraft.hypixel.skywars")
