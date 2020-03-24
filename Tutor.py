import access
from dotenv import load_dotenv
import os
from datetime import datetime
class Tutor:
    

    def __init__ (discordID, emailAddress, firstName, lastName):
        self.discordID = discordID
        self.emailAddress = emailAddress
        self.firstName = firstName
        self.lastName = lastName


    def __str__ (self):
        return f'{self.firstName} {self.lastName}'


    def getCurrentTutors():
        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pw = os.getenv('DB_PW')
        db_name = os.getenv('DB_NAME')
        con = access.Connection(db_host, db_user, '', db_name, False)
        day = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}[datetime.today().weekday()]

        # datetime object containing current date and time
        now = datetime.now()
        
        currentTime = f'{now.hour}:{now.minute}:{now.second}'

        ret = []
        tutors = con.select("discordID", "TutoringTimeSlots", f"startTime <= '{currentTime}' and endTime >= '{currentTime}' and day = '{day}'")
        
        for entry in tutors:
            ret.append(entry[0]) 
        return ret
    def getAllTutors():
        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pw = os.getenv('DB_PW')
        db_name = os.getenv('DB_NAME')
        con = access.Connection(db_host, db_user, '', db_name, False)

        ret = []
        tutors = con.select("discordID", "Tutor", "")
        
        for entry in tutors:
            ret.append(entry[0]) 
        return ret

    
    