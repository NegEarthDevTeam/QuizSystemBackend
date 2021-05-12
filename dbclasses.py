import datetime
import main

db = main.db

class HostUser(main.db.Document):
    firstName = db.StringField()
    lastName = db.StringField()
    email = db.StringField()
    passwordHash = db.StringField()
    created = datetime.datetime.now()
    lastEdit = datetime.datetime.now()


    def to_json(self):
        return {
            '_id' : str(self.pk),
            'First Name' : self.firstName,
            'Last Name' : self.lastName,
            'Email' : self.email,
            'Creation Date' : self.created,
            'Edit Date' : self.lastEdit
        }

class TestUser(main.db.Document):
    email = db.StringField()
    created = datetime.datetime.now()
    lastEdit = datetime.datetime.now()

    def to_json(self):
        return {
            '_id': str(self.pk),
            'Email': self.email,
            'Creation Date': self.created,
            'Edit Date': self.lastEdit
        }

class Quizzes(main.db.Document):
    questions = db.ListField()
    hostId = db.StringField()
    testUsersId = db.ListField()
    timeDate = db.DateTimeField()

    def to_json(self):
        return{
            '_id' : str(self.pk),
            'Questions' : self.questions,
            'Host ID' : self.hostId,
            'Test Users ID' : self.testUsersId,
            'Time + Date' : self.timeDate
        }
