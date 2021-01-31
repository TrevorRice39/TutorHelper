import access
from dotenv import load_dotenv
import os
from datetime import datetime
class Tutor:
    
    def __str__ (self):
        return f'{self.firstName} {self.lastName}: {self.discordID}'


    def getCurrentTutors():
        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pw = os.getenv('DB_PW')
        db_name = os.getenv('DB_NAME')
        con = access.Connection(db_host, db_user, db_pw, db_name, False)
        day = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}[datetime.today().weekday()]
        # datetime object containing current date and time
        now = datetime.now()
        
        currentTime = f'{now.hour}:{now.minute}:{now.second}'
    
        ret = []
        tutors = con.select("discordID", "tutoringtimeslots", f"startTime <= '{currentTime}' and endTime >= '{currentTime}' and day = '{day}'")
        
        con.close_connection()
        for entry in tutors:
            ret.append(entry[0]) 
        return ret

    def getAllTutors():
        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_pw = os.getenv('DB_PW')
        db_name = os.getenv('DB_NAME')
        con = access.Connection(db_host, db_user, db_pw, db_name, False)

        ret = []
        tutors = con.select("discordID", "tutor", "")
        
        con.close_connection()
        for entry in tutors:
            ret.append(entry[0]) 
        return ret

    
    