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
from discord.ext import commands


# dictionary of id's to member objects
memberDict = dict()
loop = asyncio.new_event_loop()


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pw = os.getenv('DB_PW')
db_name = os.getenv('DB_NAME')
con = access.Connection(db_host, db_user, '', db_name, False)



# this code starts a separate threads that updates the current tutors every 15 minuntes
currentTutors = []
studentQueue = [] # students who are queued up to be tutored
# maps the tutorDiscordID to the student and start time of the session
currentTutoringDict = dict()
def updateTutors():
    global currentTutors # get the global list instead of making one locally
    tutors = Tutor.getCurrentTutors() # get a list of tutors who are scheduled for the current time
    for tutor in tutors:
        # if they arent in the current tutors, add them
        if tutor not in currentTutors:
            # make sure they aren't currently tutoring (implies they arent in the currentTutors list)
            if tutor not in currentTutoringDict:
                currentTutors.append(tutor)
    # if a current tutor isn't in the list we just retrieved, get rid of them from our currentTutor list
    for i, tutor in enumerate(currentTutors):
        if tutor not in tutors:
            currentTutors.pop(i) # remove them
    threading.Timer(20, updateTutors).start() # update every 60 seconds
threading.Thread(target=updateTutors).start()
bot = commands.Bot(command_prefix='!')

pfp_path = "./hat.png"

fp = open(pfp_path, 'rb')
pfp = fp.read()

    
'''
Helper function that allows the bot to direct message a user

@param userID - discord id of the user the message will be sent to
@param message - the message text
@return None
'''
@bot.event
async def sendDM(userID: str, message: str) -> None:
    member = memberDict[userID] # get the member
    await member.create_dm() # create dm
    await member.dm_channel.send(message) # send the message


'''
Checks if there is a tutor who is readily available to help
@return number of tutors
'''
def tutorAvailable() -> int:
    return len(currentTutors) > 0

'''
Checks if there are students currently in queue waiting on help
@return number of students in queue
'''
def studentsAvailable() -> int:
    return len(studentQueue) > 0


'''
Every thirty seconds this function will run and check if a tutor 
is available and if there is a student that needs help
@return updates the tutoring dict and if there is a student
        tutor pair that is available, makes that pair and
        initiates tutoring session
'''
async def updateQueues() -> None:
    print('Tutors:')
    for tutor in currentTutors:
        print(tutor)
    print('\nStudents:')
    for student in studentQueue:
        print(student)
    print('\nTutoring Dict:')
    for tutor in currentTutoringDict:
        print(f'tutor: {tutor} -> student: {str(currentTutoringDict[tutor])}.')


    if studentsAvailable() and tutorAvailable():
        tutor = currentTutors.pop(0) # get the first tutor
        studentObject = studentQueue.pop(0) # get the first student in queue
        studentID = studentObject.getDiscordID() # get their id
        
        message = ""
    
        if memberDict[studentID].nick is not None:
                message = f'ID: {studentID} {memberDict[studentID].nick} is waiting on your assistance!\nCourse: {studentObject.getCourse()}\nDescription: {studentObject.getAssignmentDescription()}'
        else:
            message = f'{memberDict[studentID].mention} ID: {studentID} is waiting on your assistance!\nCourse: {studentObject.getCourse()}\nDescription: {studentObject.getAssignmentDescription()}'
        #message = f'{memberDict[studentID].mention} is waiting on your assistance!\nCourse: {studentObject.getCourse()}\nDescription: {studentObject.getAssignmentDescription()}'
        # tell the tutor they have a student waiting for their help
        bot.loop.create_task(sendDM(tutor, message))
        
        # tell the student who is going to help them
        bot.loop.create_task(sendDM(studentID, f'Hello {memberDict[studentID].mention}, {memberDict[tutor].mention} will contact you to help you!'))
        
        # get the current time and format it to hh:mm:ss
        now = datetime.now()
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        # add an entry to the dict with the studentID, currentTime, and course so
        # it can be added to the database later
        currentTutoringDict[tutor] = (studentID, currentTime, studentObject.getCourse())
    
    # sleep for one second
    await asyncio.sleep(2)

    # make a new task of the update queues
    bot.loop.create_task(updateQueues())


'''
Bot command to help a user with the bot
@param ctx
@return sends a helpful message to the user who uses the command
'''
@bot.command(name='info', help='Gives the user some info about how to use the bot')
async def help(ctx):
    help_text = "If you are a student and need help, do the following:\nThe command you need to use is '!tutorme csc 123 here is a description of my assignment'. The description is optional but you must put your course prefix and number"
    response = help_text
    await ctx.send(response)


'''
Bot event that is called when the bot initially starts
@return updates our memberDict so we have all current members in our server
        this is useful so we can dm any user by their id
'''
@bot.event
async def on_ready():
    # commented out avatar update
    # await bot.user.edit(avatar=pfp)

    # when we find the guild we're currently in
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    # build member dictionary
        for member in guild.members:
            if member not in memberDict:
                # maps memberID to member
                memberDict[str(member)] = member

'''
Bot event that is called when a new member joins
'''
@bot.event
async def on_member_join(member):
    print('member joined')
    # role = discord.utils.get(after.server.roles, name="student")
    # await bot.add_roles(member, role)

    # create a dm and send them a message
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the EKU CSC Tutoring server! Look in the info channel for more information!'
    )

    # find the current guild
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

        # add them to the member dictionary
        for member in guild.members:
            if member not in memberDict:
                memberDict[str(member)] = member

'''
Checks if a student is currently in queue or not
@params studentID - discord id of student
@return a boolean 
        true if they are in queue or being tutored
        false otherwise
'''
def studentInQueue(studentID: str) -> bool:
    # loop through students in queue
    for student in studentQueue:
        # if we find them return true
        if student.getDiscordID() == studentID:
            return True
    # check if they're in the tutoring dictionary
    for value in list(currentTutoringDict.values()):
        # if we find them return true
        if value[0] == studentID:
            return True
    # if they are not in queue, nor in tutoring, return false
    return False


'''
Bot command that allows a student to be put in queue for tutoring
@param arguments - must at least have 7 characters with the class prefix and number
        ex: csc 190
@return can update the studentQueue
'''
@bot.command(name='tutorme', help='Schedules a student for tutoring')
async def tutor_me(ctx, *, arguments: str) -> None:
    # if they didn't put in the correct arguments
    if len(arguments) <= 6:
        # tell them how to use the command
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(
            f'Hi {ctx.message.author.mention}, to use this command you must enter your course and optionally a description of your assignment. \nExample: !tutorme csc 195 I need help with homework 5.'
        )
        return

    # get the class and description
    classArg = arguments[0 : 7].upper()
    description = arguments[8:]

    # get their discord id
    discordID = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'

    # check if they are in queue
    if studentInQueue(discordID) == False: # they aren't in queue
        # make a new student object and put them in queue
        s = Student(discordID, classArg, description)
        studentQueue.append(s)
    else: # they are being tutored or in queue
        # tell them they are already queued
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(
            f'Hi {ctx.message.author.mention}, you are already in queue or you are being tutored currently.'
        )
        return

    # tell them a tutor will be with them soon
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(
        f'Hi {ctx.message.author.mention}, please wait until a tutor becomes available and they will message you.'
    )

'''
Bot command that adds a student to the database
@param fName - fName specified by student calling command
@param lName - lName specified by student calling command
@return tells the student they've been added to the db
'''
@bot.command(name='addme', help="Adds a student to the db")
async def add_me(ctx, fName, lName):
     # get the info to insert
    insertVals = [ctx.message.author, fName, lName]

    # insert it
    con.insert("Student", 'discordID, firstName, lastName', insertVals) 

    # tell them they are added
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(
        f'Hello {ctx.message.author.mention}, you have been added!'
    )

'''
Bot command that allows the tutor to end their current session
@return updates the tutoring dict
'''
@bot.command(name='freetutor', help='Makes the tutor available and ends the session')
async def free_tutor(ctx) -> None:
    # make sure it is a tutor using the command
    discordID = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'
    if discordID in currentTutoringDict:
        # get current time
        now = datetime.now()
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        # get the students id
        student = currentTutoringDict[discordID][0]

        # get current day
        day = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}[datetime.today().weekday()]

        # gather info to insert into db
        insertVals = [discordID, currentTutoringDict[discordID][1], currentTime, day, student, currentTutoringDict[discordID][2]]
        # inser it
        con.insert("TutoringLogs", 'discordID, startTime, endTime, DAY, studentDiscordID, classTutored', insertVals)
        
        # tell student and tutor the session is over
        bot.loop.create_task(sendDM(student, f'Hello {memberDict[student].mention}, your tutoring session has ended.'))
        bot.loop.create_task(sendDM(discordID, f'Your tutoring session has ended.'))

        # remove the session from the dictionary
        del currentTutoringDict[discordID]

# start updating queues
bot.loop.create_task(updateQueues())

# run the bot
bot.run(TOKEN)

# close the db connection
con.close_connection()