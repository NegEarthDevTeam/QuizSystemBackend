import main

db = main.db

class HostUser(main.db.Document):
    name = db.StringField()
    email = db.StringField()
    passwordHash = db.StringField()

    