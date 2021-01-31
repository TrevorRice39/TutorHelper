
class Student:

    def __init__(self, discordID, course, assignmentDescription):
        self.discordID = discordID
        self.course = course
        self.assignmentDescription = assignmentDescription
    
    def getDiscordID(self):
        return self.discordID
    def getCourse(self):
        return self.course
    def getAssignmentDescription(self):
        return self.assignmentDescription

    def __str__(self):
        return self.discordID