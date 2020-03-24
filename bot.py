# bot.py
import os
import random
import discord
from dotenv import load_dotenv
import threading
from Tutor import Tutor
from datetime import datetime

# this code starts a separate threads that updates the current tutors every 15 minuntes
currentTutors = []
studentQueue = [] # students who are queued up to be tutored
# maps the tutorDiscordID to the student and start time of the session
currentTutoringDict = dict()

def updateTutors():
    global currentTutors
    tutors = Tutor.getCurrentTutors()
    for tutor in tutors:
        if tutor not in currentTutors:
            if tutor not in currentTutoringDict:
                currentTutors.append(tutor)
    for i, tutor in enumerate(currentTutors):
        if tutor not in tutors:
            currentTutors.pop(i)
    
    threading.Timer(1, updateTutors).start()
threading.Thread(target=updateTutors).start()



# every thirty seconds this function will run and check if a tutor is available and if there is a student that needs help
def updateQueues():
    print(currentTutors)
    print(studentQueue)
    print(currentTutoringDict)

    if len(studentQueue) > 0 and len(currentTutors) > 0:
        print('hahah')
        tutor = currentTutors.pop(0)
        student = studentQueue.pop(0)
        # datetime object containing current date and time
        now = datetime.now()
        
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        currentTutoringDict[tutor] = (student, currentTime)
        # make a chatroom and stuff

    threading.Timer(1, updateQueues).start()
threading.Thread(target=updateQueues).start()


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
        f'Hi {member.name}, welcome to the EKU CSC Tutoring server! Look in the info channel for more information! If you want help using the tutoring bot type !info'
    )

@bot.command(name='tutorme', help='Schedules a student for tutoring')
async def tutor_me(ctx):
    discordID = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'
    if discordID not in studentQueue:
        studentQueue.append(discordID)

    response = f'Hello {ctx.message.author.mention}, you are scheduled for tutoring and a tutor will be with you shortly!'
    await ctx.send(response)

@bot.command(name='freetutor', help='Makes the tutor available and ends the session')
async def free_tutor(ctx):
    # make sure it is a tutor using the command
    discordID = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'
    # put info in db
    del currentTutoringDict[discordID]
    #response = f'Hello {ctx.message.author.mention}, you are scheduled for tutoring and a tutor will be with you shortly!'
    #await ctx.send(response)

bot.run(TOKEN)