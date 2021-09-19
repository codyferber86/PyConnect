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

#!    Copyright Cody Ferber, 2020.
###############################################################################
from contextlib import closing
from discord.ext import commands
import asyncio
import discord
import json
import pymysql
import sys
import re
import telnetlib

class Serverbot(commands.Cog):
###############################################################################
    def __init__(self, bot):
        self.bot = bot
        self.version = '1.00'
        with open('PyConnect.json') as config_file:
            self.config = json.load(config_file)
            self.channel_id = self.config['id']['channel']
            self.telnet_host = self.config['server']['host']
            self.telnet_port = self.config['server']['port']
            self.telnet_user = self.config['server']['user']
            self.telnet_pass = self.config['server']['password']
            self.sql_host = self.config['sql']['host']
            self.sql_db = self.config['sql']['db']
            self.sql_user = self.config['sql']['user']
            self.sql_pass = self.config['sql']['password']
        self.connect()
        self.tracking_task = self.bot.loop.create_task(self.track())

###############################################################################
    def connect(self):
        self.telnet = telnetlib.Telnet(self.telnet_host, self.telnet_port)
        print(self.telnet.read_until(b'Username: ').decode('ascii'))
        self.telnet.write(bytes(self.telnet_user, encoding='ascii') + b'\r\n')
        print(self.telnet.read_until(b'Password: ').decode('ascii'))
        self.telnet.write(bytes(self.telnet_pass, encoding='ascii') + b'\r\n')
        print(self.telnet.read_until(b'> ').decode('ascii'))
        self.telnet.write(b'acceptmessages on\r\n')

###############################################################################
    @commands.command(name='gmsay', brief='Send gmsay message to world.',
            description='Send gmsay message to world.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def gmsay(self, ctx, *args):
        x = 0
        for num in args:
            x += 1
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Sending gmsay message to world.')
        if x == 1:
            self.telnet.write(b'gmsay ' + args[0].encode('ascii') + b'\r\n')
            embed.add_field(name='Telnet:',value=self.telnet.read_until(b'> ')
                    .decode('ascii'), inline=False)
        else:
            embed.add_field(name='Telnet:',value='Invalid number of inputs!')
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='list',
            brief='Display Riot Test Server commands.',
                    description='Display riot test server commands.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def list(self, ctx):
        self.telnet.write(b'help\r\n')
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Displaying riot test server commands.')
        embed.add_field(name='Telnet:',value=self.telnet.read_until(b'> ')
                .decode('ascii'), inline=False)
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='lock', brief='Lock riot test server.',
            description='Lock riot test server.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def lock(self, ctx):
        self.telnet.write(b'lock\n')
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Locking Riot Test Server.')
        embed.add_field(name='Telnet:',value=self.telnet.read_until(b'> ')
                .decode('ascii'), inline=False)
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='reload', brief='Reload config variables.',
            description='Reload config variables.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def reload(self, ctx):
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Reloading config variables.')
        await ctx.send(embed=embed)
        with open('PyConnect.json') as config_file:
            self.config = json.load(config_file)
            self.telnet_host = self.config['server']['host']
            self.telnet_port = self.config['server']['port']

###############################################################################
    @commands.command(name='register', brief='Register character with server.',
            description='Register character with server.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def register(self, ctx, name):
        db = pymysql.connect(host=self.sql_host,
                             user=self.sql_user,
                             password=self.sql_pass,
                             database=self.sql_db)
        cursor = db.cursor()
        sql = "UPDATE `account` SET `status` = '1' WHERE `account`.`charname` = '{}';".format(name)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        db.close()
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Registering character with server!')
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='reloadzonequests', brief='Reload zone quests.',
            description='Reload zone quests.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def reloadzonequests(self, ctx, *args):
        x = 0
        for num in args:
            x += 1
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Reloading zone quests.')
        if x == 1:
            self.telnet.write(b'reloadzonequests ' + args[0]
                    .encode('ascii') + b'\r\n')
            embed.add_field(name='Telnet:',value=self.telnet.read_until(b'> ')
                    .decode('ascii'), inline=False)
        else:
            embed.add_field(name='Telnet:',value='Invalid number of inputs!')
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='set', brief='Set config variable.',
            description='Set config variable.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def set(self, ctx, arg1, arg2):
        embed = discord.Embed(colour=discord.Colour(0x7ed321), title='Setting:')
        if arg1 == 'ip':
            self.ip = arg2
            embed.add_field(name='Host:', value=self.telnet_host, inline=False)
            await ctx.send(embed=embed)
        if arg1 == 'port':
            self.port = arg2
            embed.add_field(name='Port:', value=self.telnet_port, inline=False)
            await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='shutdown', brief='Shutdown riot test Server bot.',
            description='Shutdown riot test server bot.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def shutdown(self, ctx):
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Shutting down Riot Test Server bot!')
        await ctx.send(embed=embed)
        await self.bot.close()

###############################################################################
    @commands.command(name='status', brief='Display bot status.',
            description='Display bot status.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def status(self, ctx):
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Riot Test Server Bot:\nVersion {}.'.format(self.version))
        embed.add_field(name='Host:', value=self.telnet_host, inline=False)
        embed.add_field(name='Port:', value=self.telnet_port, inline=False)
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='tell', brief='Send player a tell.',
            description='Send player a tell.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def tell(self, ctx, *args):
        x = 0
        for num in args:
            x += 1
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Sending {} a tell.'.format(args[0]))
        if x == 2:
            self.telnet.write(b'tell ' + args[0].encode('ascii') + b' '
                    + args[1].encode('ascii') + b'\r\n')
            embed.add_field(name='Telnet:',value=self.telnet.read_until(b'> ')
                    .decode('ascii') + args[1], inline=False)
        else:
            embed.add_field(name='Telnet:',value='Invalid number of inputs!')
        await ctx.send(embed=embed)

###############################################################################
    async def track(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            channel = self.bot.get_channel(int(self.channel_id))
            try:
                removelist = '!?,.@#$%&+-= '
                message = re.sub(r'[^\w'+removelist+']', '', self.telnet.read_very_eager().decode('ascii'))
                message = message.replace('says', ':', 1)
                message = message.replace('ooc,', ' ', 1)
                message = message.replace('telnet', '', 1)
                message = message.replace(' ', '', 3)
                await channel.send('{}'.format(message))
                print(message)
            except (EOFError, ConnectionResetError):
                print(sys.exc_info())
                self.telnet.close()
                self.connect()
            except:
                pass
            finally:
                await asyncio.sleep(5)

###############################################################################
    @commands.command(name='unlock', brief='Unlock test server.',
            description='Unlock test server.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def unlock(self, ctx):
        self.telnet.write(b'unlock\r\n')
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Unlocking test server.')
        embed.add_field(name='Telnet:',value=self.telnet.read_until(b'> ')
                .decode('ascii'), inline=False)
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='who',
            brief='Display players online.',
                    description='Display players online.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def who(self, ctx):
        self.telnet.write(b'who\r\n')
        buffer = self.telnet.read_until(b'> ')
        buffer_size = 1023
        chunks = [buffer[i:i+buffer_size]
                for i in range(0, len(buffer), buffer_size)]
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Displaying players online.')
        for value in chunks:
            embed.add_field(name='Telnet:',
                    value=value.decode('ascii'), inline=False)
        await ctx.send(embed=embed)

###############################################################################
    @commands.command(name='zonestatus',
            brief='Display Riot Test Server zone status.',
                    description='Display Riot Test Server zone status.')
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def zonestatus(self, ctx):
        self.telnet.write(b'zonestatus\r\n')
        embed = discord.Embed(colour=discord.Colour(0x7ed321),
                title='Displaying Riot Test Server zone status.')
        embed.add_field(name='Telnet:',value=self.telnet.read_until(b'> ')
                .decode('ascii'), inline=False)
        await ctx.send(embed=embed)

###############################################################################
def setup(bot):
    bot.add_cog(Serverbot(bot))