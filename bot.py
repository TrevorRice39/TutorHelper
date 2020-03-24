# bot.py
import os
import random
import discord
from dotenv import load_dotenv
import threading
from Tutor import Tutor
from datetime import datetime
import asyncio
import access
# dictionary of id's to member objects
memberDict = dict()
loop = asyncio.new_event_loop()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
from discord.ext import commands

client = discord.Client()
load_dotenv()

client = discord.Client()
# this code starts a separate threads that updates the current tutors every 15 minuntes
currentTutors = []
studentQueue = [] # students who are queued up to be tutored
# maps the tutorDiscordID to the student and start time of the session
currentTutoringDict = dict()
print(Tutor.getAllTutors())
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
bot = commands.Bot(command_prefix='!')

@bot.event
async def sendDM(userID, message):
    member = memberDict[userID]
    await member.create_dm()
    await member.dm_channel.send(message)
    #await bot.send_message(member, message)


def tutorAvailable():
    return len(currentTutors) > 0

def studentsAvailable():
    return len(studentQueue) > 0
# every thirty seconds this function will run and check if a tutor is available and if there is a student that needs help
async def updateQueues():
    print(currentTutors)
    print(studentQueue)
    print(currentTutoringDict)

    if len(studentQueue) > 0 and len(currentTutors) > 0:
        tutor = currentTutors.pop(0)
        student = studentQueue.pop(0)

        
        bot.loop.create_task(sendDM(tutor, f'{memberDict[student].mention} is waiting on your assistance!'))
        bot.loop.create_task(sendDM(student, f'Hello {memberDict[student].mention}, {memberDict[tutor].mention} will contact you to help you!'))
        
        now = datetime.now()
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        currentTutoringDict[tutor] = (student, currentTime)

    await asyncio.sleep(1)
    bot.loop.create_task(updateQueues())

    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    # print(
    #     f'{client.user} is connected to the following guild:\n'
    #     f'{guild.name}(id: {guild.id})\n'
    # )

    # build member dictionary
    for member in guild.members:
        if member not in memberDict:
            memberDict[str(member)] = member

@bot.command(name='info', help='Gives the user some info about how to use the bot')
async def help(ctx):
    help_text = "If you are a student and need help, type !tutorme to be scheduled for tutoring."
    response = help_text
    await ctx.send(response)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    # print(
    #     f'{client.user} is connected to the following guild:\n'
    #     f'{guild.name}(id: {guild.id})\n'
    # )

    # build member dictionary
    for member in guild.members:
        if member not in memberDict:
            memberDict[str(member)] = member
    print(memberDict)
    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Guild Members:\n - {members}')
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

    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(
        f'Hi {ctx.message.author.mention}, please wait until a tutor becomes available and they will message you.'
    )

@bot.command(name='freetutor', help='Makes the tutor available and ends the session')
async def free_tutor(ctx):
    # make sure it is a tutor using the command
    discordID = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'
    if discordID in currentTutoringDict:
        # put info in db
        now = datetime.now()
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pw = os.getenv('DB_PW')
        db_name = os.getenv('DB_NAME')
        con = access.Connection(db_host, db_user, '', db_name, False)

        student = currentTutoringDict[discordID][0]

        ret = []
        insertVals = [discordID, currentTutoringDict[discordID][1], currentTime, student, 'CSC 195']
        print(insertVals)
        con.insert("TutoringLogs", 'discordID, startTime, endTime, studentDiscordID, classTutored', insertVals)
        
        bot.loop.create_task(sendDM(student, f'Hello {memberDict[student].mention}, your tutoring session has ended.'))
        bot.loop.create_task(sendDM(discordID, f'Your tutoring session has ended.'))
        del currentTutoringDict[discordID]

bot.loop.create_task(updateQueues())
bot.run(TOKEN)
