#!/usr/local/bin/python3
###############################################################################
#!    This program is free software: you can redistribute it and/or modify
#!    it under the terms of the GNU General Public License as published by
#!    the Free Software Foundation, either version 3 of the License, or
#!    (at your option) any later version.

#!    This program is distributed in the hope that it will be useful,
#!    but WITHOUT ANY WARRANTY; without even the implied warranty of
#!    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#!    GNU General Public License for more details.

#!    You should have received a copy of the GNU General Public License
#!    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!    Copyright Cody Ferber, 2021.
###############################################################################
from contextlib import closing
from datetime import datetime
from discord.ext import commands
from random import *
import asyncio
import discord
import re

class Countbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_month = datetime.now().month

############################################################################### 
    @commands.command(name='export', brief='Export userlist.',
            description='Export userlist.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def send(self, ctx, month):
        await ctx.send(file=discord.File('userlist_{}.dat'.format(month)))

############################################################################### 
    @commands.command(name='find', brief='Find user.',
            description='Find user.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def find(self, ctx, month, id):
        with open('userlist_{}.dat'.format(month), 'r') as file:
            data = file.read()
        results = re.findall(r'{}'.format(id), data)
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Userlist search.')
        embed.add_field(name='Results:', value=results, inline=False)
        await ctx.send(embed=embed)
        
###############################################################################
    @commands.command(name='list', brief='Display userlist.',
            description='Display userlist.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def list(self, ctx, month):
        with open('userlist_{}.dat'.format(month), 'r') as file:
            data = file.read()
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Active userlist for month {}.'.format(month))
        embed.add_field(name='Users:',value=data, inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Countbot(bot))

