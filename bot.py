# bot.py
import os
import random
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
from discord.ext import commands

client = discord.Client()
load_dotenv()

bot = commands.Bot(command_prefix='!')
@bot.command(name='info', help='Gives the user some info about how to use the bot')
async def help(ctx):
    help_text = "If you are a student and need help, type '!tutorme' to be scheduled for tutoring."
    response = help_text
    await ctx.send(response)

@bot.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})\n'
        )

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the EKU CSC Tutoring server! Look in the info channel for more information!'
    )

@bot.command(name='tutorme', help='Schedules a student for tutoring')
async def tutor_me(ctx):
    # schedule
    response = f'Hello {ctx.message.author.mention}, you are scheduled for tutoring and a tutor will be with you shortly!'
    await ctx.send(response)

bot.run(TOKEN)