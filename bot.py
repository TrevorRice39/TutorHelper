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
from Student import Student
# dictionary of id's to member objects
memberDict = dict()
loop = asyncio.new_event_loop()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
from discord.ext import commands

client = discord.Client()
load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pw = os.getenv('DB_PW')
db_name = os.getenv('DB_NAME')
con = access.Connection(db_host, db_user, '', db_name, False)
client = discord.Client()
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
    print('students ', studentQueue)
    print(currentTutoringDict)

    if len(studentQueue) > 0 and len(currentTutors) > 0:
        tutor = currentTutors.pop(0)
        studentObject = studentQueue.pop(0)
        studentID = studentObject.getDiscordID()
        
        bot.loop.create_task(sendDM(tutor, f'{memberDict[studentID].mention} is waiting on your assistance!\nCourse: {studentObject.getCourse()}\nDescription: {studentObject.getAssignmentDescription()}'))
        bot.loop.create_task(sendDM(studentID, f'Hello {memberDict[studentID].mention}, {memberDict[tutor].mention} will contact you to help you!'))
        
        now = datetime.now()
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        currentTutoringDict[tutor] = (studentID, currentTime, studentObject.getCourse())

    await asyncio.sleep(1)
    bot.loop.create_task(updateQueues())

    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    # build member dictionary
    for member in guild.members:
        if member not in memberDict:
            memberDict[str(member)] = member

@bot.command(name='info', help='Gives the user some info about how to use the bot')
async def help(ctx):
    help_text = "If you are a student and need help, do the following:\nThe command you need to use is '!tutorme csc 123 here is a description of my assignment'. The description is optional but you must put your course prefix and number"
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
    # print(memberDict)
    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Guild Members:\n - {members}')
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the EKU CSC Tutoring server! Look in the info channel for more information! If you want help using the tutoring bot type !info'
    )

def studentInQueue(studentID):
    for student in studentQueue:
        print(student.getDiscordID, " ", studentID)
        if student.getDiscordID() == studentID:
            return True
    for value in list(currentTutoringDict.values()):
        if value[0] == studentID:
            return True
    return False


@bot.command(name='tutorme', help='Schedules a student for tutoring')
async def tutor_me(ctx, *, arguments):
    if len(arguments) <= 6:
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(
            f'Hi {ctx.message.author.mention}, to use this command you must enter your course and optionally a description of your assignment. \nExample: !tutorme csc 195 I need help with homework 5.'
        )
        return
    classArg = arguments[0 : 7].upper()
    description = arguments[8:]
    discordID = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'
    if studentInQueue(discordID) == False:
        print('not in')
        s = Student(discordID, classArg, description)
        studentQueue.append(s)
    else:
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(
            f'Hi {ctx.message.author.mention}, you are already in queue or you are being tutored currently.'
        )
        return
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(
        f'Hi {ctx.message.author.mention}, please wait until a tutor becomes available and they will message you.'
    )

@bot.command(name='addme', help="Adds a student to the db")
async def add_me(ctx, fName, lName):
    insertVals = [ctx.message.author, fName, lName]
    con.insert("Student", 'discordID, firstName, lastName', insertVals)
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(
        f'Hello {ctx.message.author.mention}, you have been added!'
    )
@bot.command(name='freetutor', help='Makes the tutor available and ends the session')
async def free_tutor(ctx):
    # make sure it is a tutor using the command
    discordID = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'
    if discordID in currentTutoringDict:
        # put info in db
        now = datetime.now()
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        student = currentTutoringDict[discordID][0]

        ret = []
        insertVals = [discordID, currentTutoringDict[discordID][1], currentTime, student, currentTutoringDict[discordID][2]]
        con.insert("TutoringLogs", 'discordID, startTime, endTime, studentDiscordID, classTutored', insertVals)
        
        bot.loop.create_task(sendDM(student, f'Hello {memberDict[student].mention}, your tutoring session has ended.'))
        bot.loop.create_task(sendDM(discordID, f'Your tutoring session has ended.'))
        del currentTutoringDict[discordID]

bot.loop.create_task(updateQueues())
bot.run(TOKEN)
