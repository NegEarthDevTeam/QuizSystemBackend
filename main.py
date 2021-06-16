from logging import error, exception
from re import U
from warnings import catch_warnings
import logic
import traceback
import random
import string
import math
import time
import analytics
from flask_mongoengine import *
import hashlib
from flask_socketio import *
from flask import *
import datetime
from flask_login import (
    current_user,
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
)
from flask_session import Session

# Argon2 implementation
from argon2 import PasswordHasher
from argon2 import exceptions as Argon2Exceptions

global db
global SECRET_KEY


def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


def prGreen(skk):
    print("\033[92m {}\033[00m".format(skk))


def prYellow(skk):
    print("\033[93m {}\033[00m".format(skk))


def prLightPurple(skk):
    print("\033[94m {}\033[00m".format(skk))


def prPurple(skk):
    print("\033[95m {}\033[00m".format(skk))


def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))


def prLightGray(skk):
    print("\033[97m {}\033[00m".format(skk))


app = Flask(__name__)


app.config["MONGODB_SETTINGS"] = {
    "db": "quizsystemdb",
    "host": "localhost",
    "port": 27017,
}
db = MongoEngine(app)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "quizSystemSecretKey"
SECRET_KEY = "%^&quizSystem*()SecretKey!£$"

# app.config['SESSION_PERMANENT'] = False

login_manager = LoginManager(app)
Session(app)

app.secret_key = "quizSystemSecretKey"


socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# establish passwordhasher
ph = PasswordHasher()


#####################
# CLASSES FOR MONGO #
#####################


"""class HostUser(db.Document):
    firstName = db.StringField()
    lastName = db.StringField()
    email = db.StringField()
    passwordHash = db.StringField()
    created = db.DateTimeField()
    lastEdit = db.DateTimeField()
    lastSignIn = db.DateTimeField()

    def to_json(self):
        return jsonify(
            {
                "_id": str(self.pk),
                "First Name": self.firstName,
                "Last Name": self.lastName,
                "Email": self.email,
                "Creation Date": self.created,
                "Edit Date": self.lastEdit,
            }
        )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.pk)


class TestUser(db.Document):
    email = db.StringField()
    created = datetime.datetime.now()
    lastEdit = datetime.datetime.now()

    def to_json(self):
        return jsonify(
            {
                "_id": str(self.pk),
                "Email": self.email,
                "Creation Date": self.created,
                "Edit Date": self.lastEdit,
            }
        )"""


class UserType(db.Document):
    firstName = db.StringField()
    lastName = db.StringField()
    email = db.StringField()
    passwordHash = db.StringField()
    created = db.DateTimeField()
    lastEdit = db.DateTimeField()
    lastSignIn = db.DateTimeField()
    hostOrTest = db.StringField()

    def to_json(self):
        return jsonify(
            {
                "_id": str(self.pk),
                "First Name": self.firstName,
                "Last Name": self.lastName,
                "Email": self.email,
                "Creation Date": self.created,
                "Edit Date": self.lastEdit,
                "Last Sign In": self.lastSignIn,
                "hostOrTest": self.hostOrTest,
            }
        )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.pk)

    @property
    def host(self):
        if self.hostOrTest == "host":
            return True
        else:
            return False

    @property
    def test(self):
        if self.hostOrTest == "test":
            return True
        else:
            return False

    @property
    def deleted(self):
        if self.hostOrTest == "deleted":
            return True
        else:
            return False


class Quizzes(db.Document):
    roomId = db.StringField()
    allConnectedUsers = db.ListField()
    dateTime = db.DateTimeField()
    quizCompletedSuccessfully = db.StringField()
    questions = db.ListField()
    timeLimit = db.IntField()
    activeRoomId = db.StringField()
    hostId = db.StringField()
    quenswerId = db.ListField()

    def to_json(self):
        return jsonify(
            {
                "_id": str(self.pk),
                "Room ID": self.roomId,
                "All Time Connected Users": self.allConnectedUsers,
                "Date and Time of Creation": self.dateTime,
                "Quiz Completed Successfully": self.quizCompletedSuccessfully,
                "Questions": self.questions,
                "Time Limit": self.timeLimit,
                "Active Room Object Id": self.activeRoomId,
                "Host ID": self.hostId,
                "Quenswer IDs": self.quenswerId,
            }
        )


class Question(db.Document):
    category = db.StringField()
    questionType = db.StringField()
    answer = db.ListField()
    poll = db.ListField()
    title = db.StringField()
    bodyMD = db.StringField()
    videoURL = db.StringField()
    imageURL = db.StringField()

    def to_json(self):
        return jsonify(
            {
                "_id": str(self.pk),
                "Category": self.category,
                "Question Type": self.questionType,
                "Answer": self.answer,
                "Poll": self.poll,
                "Title": self.title,
                "Body MD": self.bodyMD,
                "Image URL": self.imageURL,
                "VideoURL": self.videoURL,
            }
        )


class Categories(db.Document):
    name = db.StringField()

    def to_json(self):
        return jsonify({"_id": str(self.pk), "name": self.name})

    @property
    def assocQuestions(self):
        op = []
        for question in Question.objects:
            if question.category == self.name:
                op.append(str(question.pk))
        return op


class ActiveRooms(db.Document):
    roomId = db.StringField()
    connectedUserId = db.ListField()
    allConnectedUsers = db.ListField()
    dateTime = db.DateTimeField()
    quizStarted = db.StringField()
    questions = db.ListField()
    allQuestions = db.ListField()
    questionCompleted = db.ListField()
    timeLimit = db.IntField()
    currentQuestion = db.StringField()
    lastQuestion = db.StringField()
    lastQuestionSentTimestamp = db.DateTimeField()
    firstQuestion = db.StringField()
    hostId = db.StringField()

    def to_json(self):
        return jsonify(
            {
                "_id": str(self.pk),
                "Room ID": self.roomId,
                "Connected User IDs": self.connectedUserId,
                "All Time Connected Users": self.allConnectedUsers,
                "Date and Time of Creation": self.dateTime,
                "Questions": self.questions,
                "Time Limit": self.timeLimit,
                "Quiz Started": self.quizStarted,
                "Current Question": self.currentQuestion,
                "lastQuestion": self.lastQuestion,
                "firstQuestion": self.firstQuestion,
                "Host ID": self.hostId,
            }
        )


class Quenswers(db.Document):
    userId = db.StringField()
    questionId = db.StringField()
    answer = db.ListField()
    submitDateTime = db.DateTimeField()
    questionSentTimestamp = db.DateTimeField()
    quizEnvId = db.StringField()
    quizId = db.StringField()
    markedBy = db.StringField()
    markedDateTime = db.DateTimeField()
    correct = db.StringField()

    def to_json(self):
        return jsonify(
            {
                "_id": str(self.pk),
                "User ID": self.userId,
                "Question ID": self.questionId,
                "Answer": self.answer,
                "Submit Date Time": self.submitDateTime,
                "Quiz Environment ID": self.quizEnvId,
                "Quiz OBJ ID": self.quizId,
                "Marker ID": self.markedBy,
                "Marked Date Time": self.markedDateTime,
                "Correct": self.correct,
            }
        )

    @property
    def marked(self):
        if self.markedBy == "None":
            return False
        else:
            return True


# '' : self. ,

#################
# Custom Errors #
#################


class BadRequestError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "The request was bad"


class UserAlreadyExist(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "A user with that email already exists"


class UserDeleted(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "That user is deleted"


class ResourceNotFound(Exception):
    def __init__(self, **kwargs):
        self.resourceType = kwargs["resourceType"]

    def __str__(self):
        if self.resourceType == "hostUser":
            return "Host user not found"
        if self.resourceType == "testUser":
            return "Test user not found"
        if self.resourceType == "user":
            return "User not found"
        if self.resourceType == "quiz":
            return "Quiz not found"
        if self.resourceType == "question":
            return "Question not found"
        if self.resourceType == "category":
            return "Category not found"


class NotNegResource(Exception):
    def __init__(self, message):
        if message:
            self.message = message
        else:
            pass

    def __str__(self):
        return "You have tried to use a non NEG resource"


class LastQuestion(Exception):
    def __init__(self, message):
        if message:
            self.message = message
        else:
            pass

    def __str__(self):
        return "this was the last question in this room"


############################
# Authentication Endpoints #
############################


@login_manager.user_loader
def loaduser(id):
    userOBJ = UserType.objects(id=id).first()
    return userOBJ


# login_manager.login_view = "login"
login_manager.session_protection = "strong"


@app.route("/api/Login", methods=["POST"])
@app.route("/api/login", methods=["POST"])
def login():
    requestData = request.get_json()
    print("login")
    print(f"{ph.hash('abcdef')} is the password hash")
    print(requestData)
    if not logic.assertExists(["email", "passwordHash"], requestData):
        return ("Insufficent data", 400)

    thisEmail, thisPassword = requestData["email"], requestData["passwordHash"]
    print(f"{ph.hash('abcdef')} is the password hash")
    # Check user exists, but don't notify that user exists if password is wrong!
    thisUser = UserType.objects(email=thisEmail).first()
    if thisUser == None:
        return ("Username and password combination do not exist", 400)

    try:
        ph.verify(thisUser.passwordHash, thisPassword)
        # Verify raises an exception if it fails, so it must be OK if it gets to this point.
        if ph.check_needs_rehash(thisUser.passwordHash):
            thisUser.update(passwordHash=ph.hash(thisPassword))

        print(ph.hash(thisPassword))

        login_user(thisUser)

        thisUser.update(lastSignIn=datetime.datetime.now())
        prGreen(f"HTTP {thisUser.firstName} {thisUser.lastName} has logged in")
        return (
            jsonify(
                {
                    "status": "success",
                    "userID": thisUser.get_id(),
                    "userName": f"{thisUser.firstName} {thisUser.lastName}",
                }
            ),
            200,
        )

    except Argon2Exceptions.VerificationError as e:
        prRed("Password verification error occurred.")
        prRed(e)
        return "Username and password combination do not exist", 400
    except Exception as e:
        prRed("Exception occurred.")
        prRed(e)
        return "Server error", 500

    """

    data = requestData

    if "session" in data:
        session["value"] = data["session"]
    elif "email" in data:
        if data["email"]:
            email = requestData["email"]
            if "passwordHash" in request_data:
                password = request_data["passwordHash"]
                passwordWiSalt = password + SECRET_KEY
                passwordHash = hashlib.md5(passwordWiSalt.encode())
                passwordHash = passwordHash.hexdigest()
            else:
                passwordHash = request_data["email"]
            userObj = UserType.objects(email=email, passwordHash=passwordHash).first()
            if userObj:
                login_user(userObj)
                userObj.update(lastSignIn=datetime.datetime.now())
                prGreen(f"HTTP {userObj.firstName} {userObj.lastName} logged in")

                return (
                    jsonify(
                        {
                            "status": "success",
                            "userID": userObj.get_id(),
                            "userName": f"{userObj.firstName} {userObj.lastName}",
                        }
                    ),
                    200,
                )
            else:
                prRed("HTTP Username or Password error")
                return (jsonify("Username or password error"), 401)
                """


@socketio.on("socketLogin")
def socketLogin(data):
    # request_data = request.get_json()
    # data = request_data

    if "session" in data:
        session["value"] = data["session"]
    elif "email" in data:
        if data["email"]:
            email = data["email"]
            if "passwordHash" in data:
                passwordHash = data["passwordHash"]
            else:
                passwordHash = data["email"]
            userObj = UserType.objects(email=email, passwordHash=passwordHash).first()
            if userObj:
                login_user(userObj)
                userObj.update(lastSignIn=datetime.datetime.now())
                (f"SOCKET {userObj.firstName} {userObj.lastName} logged in")

                send({"status": "success", "userID": userObj.get_id()})
            else:
                send("Username or password error")


# logout route


@app.route("/api/hostLogout", methods=["POST"])
@login_required
def logout():
    logout_user()
    prGreen("User Logged Out")
    return (jsonify("logout success"), 200)


@app.route("/api/displayHostUserInfo", methods=["POST"])
def user_info():
    if current_user.is_authenticated:
        return (current_user.to_json(), 200)


@app.route("/api/isUserLoggedIn", methods=["GET"])
def apiIsUserLoggedIn():
    if current_user.is_authenticated:

        return "True"
    elif not current_user.is_authenticated:
        return "False"


####################
# Socket IO Events #
####################

# @app.route('/socketIO/API/createRoom2', methods=["POST"])
@socketio.on("createRoom")
def createRoom(data):
    #
    # if current_user.is_authenticated:
    quizId = "".join(random.choice(string.ascii_uppercase) for i in range(6))

    questions = data["questionIDs"]
    if len(questions) == 0:

        return ("error", 400)
    timeLimit = data["timeLimit"]
    requestUserId = data["userID"]
    quizStarted = "False"
    questionCompleted = []
    """
    for question in questions:
        questionCompleted.append("")
    """
    activeRooms = ActiveRooms(
        roomId=quizId,
        connectedUserId=[requestUserId],
        allConnectedUsers=[requestUserId],
        dateTime=datetime.datetime.now(),
        questions=questions,
        allQuestions=questions,
        questionCompleted=questionCompleted,
        timeLimit=timeLimit,
        quizStarted=quizStarted,
        currentQuestion="initiateStr",
        lastQuestion="initiateStr",
        firstQuestion="initiateStr",
        hostId=requestUserId,
    )
    activeRooms.save()

    # emit('id', f'ID {quizId}', namespace='/', )
    join_room(quizId)
    prLightPurple(f"{quizId} was initiated")
    return quizId


# join room
@socketio.on("join")
def on_join(data):
    # TODO check that the room isn't in session before allowing users to join a room, as if the quiz env has begun, it doesn't like users joining part way through
    username = data["username"]
    room = data["room"]
    join_room(room)
    userPk = data["userID"]

    roomObj = ActiveRooms.objects(roomId=room).first()

    emit("joinRoom", roomObj.timeLimit)

    roomObj.connectedUserId.append(userPk)
    roomObj.allConnectedUsers.append(userPk)
    roomObj.save()

    thisNewUser = UserType.objects(id=userPk).first()
    newUserName = thisNewUser.firstName + " " + thisNewUser.lastName
    tempArray = [
        UserType.objects(id=id).first().firstName
        + " "
        + UserType.objects(id=id).first().lastName
        for id in roomObj.connectedUserId
    ]

    emit("onRoomUpdated", newUserName, to=room)
    prGreen(f"{newUserName} joined {room}")
    return (tempArray, roomObj.timeLimit)


# exit room


@socketio.on("leave")
def on_leave(data):

    username = data["username"]
    room = data["room"]
    leave_room(room)

    send(username + " has left the quizspace.", to=room)


# submit quiz answer
@socketio.event
def submitAnswer(data):

    curUserId = data["userID"]["userID"]
    roomId = data["room"]["roomCode"]
    quizEnv = ActiveRooms.objects(roomId=roomId).first()

    thisAnswer = Quenswers(
        userId=str(curUserId),
        questionId=quizEnv.currentQuestion,
        answer=data["Answer"] if isinstance(data["Answer"], list) else [data["Answer"]],
        submitDateTime=datetime.datetime.now(),
        quizEnvId=str(quizEnv.pk),
        quizId=quizEnv.roomId,
        correct="unMarked",
        questionSentTimestamp=quizEnv.lastQuestionSentTimestamp,
    )
    thisAnswer.save()

    currentQuestion = quizEnv.currentQuestion
    newCount = (
        Quenswers.objects(quizEnvId=str(quizEnv.pk))
        .filter(questionId=currentQuestion)
        .count()
    )

    if newCount >= (len(quizEnv.connectedUserId) - 1):

        newEnv = ActiveRooms.objects(roomId=roomId).first()
        newEnv.questionCompleted.append(currentQuestion)
        newEnv.save()

        emit("questionTimeout", to=roomId)
        prPurple(f"all users answered {currentQuestion} in {str(quizEnv.pk)}")
        return "yolo"
        # Prematurely end quiz
    prGreen(f"{str(curUserId)} just submitted an answer to {roomId}")


# Send Question to quizspace
# namespace is implied from the originating event


@socketio.event
def startQuiz(data):

    curUserId = data["userID"]
    """
    
    
    
    """
    quizEnv = ActiveRooms.objects(connectedUserId=curUserId).first()
    quizEnv.quizStarted = "True"
    quizEnv.save()

    try:
        op = {}
        roomId = data["room"]

        quizEnv = ActiveRooms.objects(roomId=roomId).first()
        questionLs = quizEnv.questions

        curQuestion = questionLs[0]
        quizEnv.currentQuestion = curQuestion
        quizEnv.questions.remove(curQuestion)
        quizEnv.quizstarted = "True"
        quizEnv.firstQuestion = "True"
        quizEnv.save()

        if quizEnv.lastQuestion == "True":

            raise LastQuestion(f"LastQuestion for room {quizEnv.roomId}")

        if len(quizEnv.questions) == 0:

            op["lastQuestion"] = "True"
            quizEnv.lastQuestion = "True"
        else:

            op["lastQuestion"] = "False"
            quizEnv.lastQuestion = "False"

        quizEnv.save()
        questionObj = Question.objects(id=curQuestion).first()

        if questionObj.questionType == "multiple":
            possAnswers = questionObj.poll + questionObj.answer
            random.shuffle(possAnswers)
            op["possAnswers"] = possAnswers
            op["answerQty"] = len(questionObj.answer)

        op["questionType"] = questionObj.questionType
        op["title"] = questionObj.title
        op["bodyMD"] = questionObj.bodyMD

        strCurrentTime = datetime.datetime.now()
        op["currentTime"] = str(strCurrentTime)
        strFinishQuestion = datetime.datetime.now() + datetime.timedelta(
            seconds=quizEnv.timeLimit
        )
        op["finishQuestion"] = str(strFinishQuestion)

        emit("startedQuiz", (len(questionLs) + 1), to=roomId)

    except Exception as err:
        prRed(f"There where no questions assigned to {roomId}")
        prRed(err)
        send("There were no questions in this quiz")
    else:
        prLightPurple(f"{roomId} room started quizzing")
        return op


@socketio.event
def sendQuestion(data):
    try:

        # send("question was sent")
        op = {}
        roomId = data["room"]
        quizEnv = ActiveRooms.objects(roomId=roomId).first()

        if quizEnv.lastQuestion == "True":

            raise LastQuestion(quizEnv.roomId)

        questionLs = quizEnv.questions

        if quizEnv.firstQuestion == "True":
            curQuestion = quizEnv.currentQuestion
            quizEnv.firstQuestion = "False"
        else:
            curQuestion = questionLs[0]
            quizEnv.currentQuestion = curQuestion
            quizEnv.questions.remove(curQuestion)

        if len(quizEnv.questions) == 0:

            op["lastQuestion"] = "True"
            quizEnv.lastQuestion = "True"
        else:

            op["lastQuestion"] = "False"
            quizEnv.lastQuestion = "False"

        quizEnv.lastQuestionSentTimestamp = datetime.datetime.now()

        quizEnv.save()

        questionObj = Question.objects(id=curQuestion).first()

        if questionObj.questionType == "multiple":
            possAnswers = questionObj.poll + questionObj.answer
            random.shuffle(possAnswers)
            op["possAnswers"] = possAnswers
            op["answerQty"] = len(questionObj.answer)

        op["questionType"] = questionObj.questionType
        op["title"] = questionObj.title
        op["bodyMD"] = questionObj.bodyMD
        op["position"] = len(quizEnv.questionCompleted) + 1
        tempUnixTimeInMS = time.time_ns() / 1000000
        op["finishQuestion"] = math.floor(tempUnixTimeInMS + quizEnv.timeLimit * 1000)

    except LastQuestion as lqe:
        prRed(lqe)
    except Exception as e:
        prRed(e)

    else:
        prGreen(f"emitting question{op} to {roomId}")
        emit("receiveQuestion", op, to=roomId)

        socketio.sleep(quizEnv.timeLimit)

        newEnv = ActiveRooms.objects(roomId=roomId).first()

        if newEnv == None:
            return

        if not (curQuestion in newEnv.questionCompleted):
            newEnv.questionCompleted.append(curQuestion)
            newEnv.save()

            emit("questionTimeout", to=roomId)
            return

        """
        else:
            currQuestionListIndex = quizEnvUpToDate.allQuestions.index(
                quizEnvUpToDate.currentQuestion
            )
            if quizEnvUpToDate.questionCompleted[currQuestionListIndex] == "true":
                pass
            else:
                quizEnvUpToDate.questionCompleted[currQuestionListIndex] = "true"
                quizEnvUpToDate.save()
                
                emit("questionTimeout", to=roomId)
        #   
        """


@socketio.event
def finishQuiz(data):

    room = data["room"]
    # close_room(room)
    curUserId = data["userID"]

    print(f"Room: {room}")
    print(f"User Id {curUserId}")
    quizEnv = ActiveRooms.objects(roomId=room).first()

    quiz = Quizzes(
        roomId=quizEnv.roomId,
        allConnectedUsers=quizEnv.allConnectedUsers,
        dateTime=quizEnv.dateTime,
        quizCompletedSuccessfully="True",
        questions=quizEnv.allQuestions,
        timeLimit=quizEnv.timeLimit,
        activeRoomId=str(quizEnv.pk),
        hostId=quizEnv.hostId,
        quenswerId=[],
    )
    quiz.save()
    quizEnv.delete()
    emit("notifyFinishQuiz", to=room)
    prCyan(f"{room} completed")
    prGreen(f"attempting auto marking and Quenswer assignment for {quizEnv.roomId}")
    x = 0
    print(len(quiz.quenswerId))
    while len(quiz.quenswerId) == 0:
        assignQuenswersToQuiz(quiz)
        x += 1
    print(f"len is now {len(quiz.quenswerId)} it took {x} attempts")
    autoMarking(quiz)
    prGreen(f"Auto marking and Quenswer assignment complete for {quizEnv.roomId}")


############################
# SOCKETIO LOGIC FUNCTIONS #
############################


def addUserToRoom(room, userPK):
    roomObj = ActiveRooms.objects(roomId=room).first()
    roomObj.connectedUserId.append(userPK)
    roomObj.allConnectedUsers.append(userPK)
    roomObj.save()
    onRoomUpdated(room)

    # emit("onRoomUpdated", connectedusers, to=roomId)


def removeUserFromRoom(roomId, userId):
    room = ActiveRooms.objects(roomId=roomId).first()
    try:
        room.connectedUserId.remove(userId)
        room.save()
    except ValueError:
        return (jsonify("User wasnt in the room"), 404)
    except Exception:

        return (jsonify("BAD REQUEST"), 400)
    else:
        pass


def onRoomUpdated(roomId):
    room = ActiveRooms.objects(roomId=roomId).first()
    connectedusers = room.connectedUserId
    op = []
    for user in connectedusers:
        userObj = UserType.objects(id=user).first()
        op.append(userObj.firstName)
    room.save()
    prGreen(f"{op} joined {roomId}")
    emit("onRoomUpdated", op, to=roomId)


#################
# API ENDPOINTS #
#################


# GET Users
@app.route("/api/users", methods=["GET"])
@app.route("/get/users", methods=["GET"])
def getUsers():
    reqID, reqType = request.args.get("id"), request.args.get("type")

    def getUserById(id):

        user = UserType.objects(id=id).exclude("passwordHash").first()
        return user

    def getUserByType(type):

        op = []
        for user in UserType.objects(hostOrTest=type):
            op.append(UserType.objects(id=str(user.pk)).exclude("passwordHash").first())
        return op

    def getAllUsers():

        return UserType.objects.exclude("passwordHash")

    if reqID and reqType:
        return ("Cannot filter by both type and ID.", 400)

    if reqID:
        return jsonify(getUserById(reqID))

    if reqType:
        return jsonify(getUserByType(reqType))
    return jsonify(getAllUsers())


# Combined route to create users
@app.route("/api/users", methods=["POST"])
def addNewUser():
    requestData = request.get_json()

    expectedData = ["email", "firstName", "lastName", "type"]
    if not "type" in requestData:
        return ("Insufficent data", 400)

    if requestData["type"] != "host" and requestData["type"] != "test":
        return "Invalid data for `type`", 400

    if requestData["type"] == "host":
        expectedData.append("password")

    sanitisedEmail = requestData["email"].lower().strip()

    if not logic.assertExists(expectedData, requestData):
        return ("Insufficent data", 400)

    try:
        # Check user doesn't already exist
        attemptGetUser = UserType.objects(email=sanitisedEmail).first()
        if attemptGetUser and attemptGetUser.hostOrTest == "deleted":
            raise UserDeleted()
        if attemptGetUser != None:
            raise UserAlreadyExist()

        passwordHash = ph.hash(requestData["password"])

        # password = requestData["password"]
        # passwordWiSalt = password + SECRET_KEY
        # passwordHash = hashlib.md5(passwordWiSalt.encode())
        # passwordHash = passwordHash.hexdigest()

        # All good, let's go ahead.
        thisUser = UserType(
            firstName=requestData["firstName"].strip(),
            lastName=requestData["lastName"].strip(),
            email=sanitisedEmail,
            passwordHash=passwordHash
            if requestData["type"] == "host"
            else sanitisedEmail,
            created=datetime.datetime.now(),
            lastEdit=datetime.datetime.now(),
            lastSignIn=datetime.datetime.now(),
            hostOrTest=requestData["type"],
        )
        thisUser.save()
        prGreen(
            f"Succesfully created user {thisUser.firstName} {thisUser.lastName} at {thisUser.email}"
        )
        return jsonify(thisUser), 200
    except UserDeleted as e:
        return "This email is currently assigned to a deleted user", 400
    except UserAlreadyExist as e:

        return "This email is already in use", 400
    except Exception as e:

        return "There was an error with this request", 500


# creates host users
@app.route("/create/hostUser", methods=["POST"])
def createHostUser():
    requestData = request.get_json()
    try:

        if UserType.objects(email=requestData["email"]).first().firstName != "None":
            if (
                UserType.objects(email=requestData["email"]).first().hostOrTest
                == "deleted"
            ):
                raise UserDeleted()
            else:
                raise UserAlreadyExist()

        hostUser = UserType(
            firstName=requestData["firstName"],
            lastName=requestData["lastName"],
            email=requestData["email"],
            passwordHash=requestData["passwordHash"],
            created=datetime.datetime.now(),
            lastEdit=datetime.datetime.now(),
            lastSignIn=datetime.datetime.now(),
            hostOrTest="host",
        )
        hostUser.save()
    except UserDeleted as ud:

        return (jsonify("User is registered as deleted"), 400)
    except UserAlreadyExist as uae:

        return (jsonify("User already exists"), 400)
    except Exception as e:

        return (jsonify("BAD REQUEST"), 400)
    else:
        return jsonify(hostUser)


# creates test users


@app.route("/create/testUser", methods=["POST"])
def createTestUser():
    requestData = request.get_json()
    try:
        if UserType.objects(email=requestData["email"]).first().firstName != "None":
            if (
                UserType.objects(email=requestData["email"]).first().hostOrTest
                == "deleted"
            ):
                raise UserDeleted()
            else:
                raise UserAlreadyExist()
        testUser = UserType(
            firstName=requestData["firstName"],
            lastName=requestData["lastName"],
            email=requestData["email"],
            passwordHash=requestData["passwordHash"],
            created=datetime.datetime.now(),
            lastEdit=datetime.datetime.now(),
            lastSignIn=datetime.datetime.now(),
            hostOrTest="host",
        )
        testUser.save()
    except UserDeleted as ud:

        return (jsonify("User is registered as deleted"), 400)
    except UserAlreadyExist as uae:

        return (jsonify("User already exists"), 400)
    except Exception as e:

        return (jsonify("BAD REQUEST"), 400)
    else:
        return jsonify(testUser)


@app.route("/api/user", methods=["PUT"])
@app.route("/edit/user", methods=["PUT"])
def createDeeTestUser():
    requestData = request.get_json()
    try:
        id = requestData["id"]
        testUser = UserType.objects(id=id).first()
        if "firstName" in requestData:
            testUser.firstName = requestData["firstName"]
        if "lastName" in requestData:
            testUser.lastName = requestData["lastName"]
        if "email" in requestData:
            testUser.email = requestData["email"]
        if "passwordHash" in requestData:
            testUser.passwordHash = requestData["passwordHash"]
        if "hostOrTest" in requestData:
            testUser.hostOrTest = requestData["hostOrTest"]
        testUser.lastEdit = datetime.datetime.now()
    except Exception:

        return (jsonify("BAD REQUEST"), 400)
    else:
        testUser.save()
        return testUser.to_json()


@app.route("/api/user", methods=["DELETE"])
@app.route("/delete/user", methods=["DELETE"])
def deleteUsers():
    requestData = request.get_json()
    id = requestData["id"]
    try:
        userObj = UserType.objects(id=id).first()
        userObj.hostOrTest = "deleted"
        userObj.save()
    except Exception:
        prRed(f"Unable to delete user {id}")
        return (jsonify("BAD REQUEST"), 400)
    else:
        prYellow(f"{id} set to deleted")
        return jsonify({f"STATUS": "{id} set to deleted"})


# checks user types


@app.route("/api/user/check", methods=["POST"])
@app.route("/check/userType", methods=["POST"])
def checkUserType():
    request_data = request.get_json()
    if request_data == None:
        return make_response({"error": "Nothing sent."}, 400)

    email = request_data["email"].lower()
    if not ("@" in email):
        return make_response({"error": "Not a valid email"}, 400)

    emailDomain = email.split("@", 1)[1]

    if emailDomain != "negearth.co.uk":
        return make_response({"error": "Email is not of the correct type"}, 400)

    userObj = UserType.objects(email=email).first()

    if userObj.host:
        return make_response({"user": "hostUser"}, 200)
    if userObj.test:
        return make_response({"user": "testUser"}, 200)
    return make_response({"error": "User not found"}, 400)


@app.route("/api/questions/<id>", methods=["GET"])
def getSingleQuestion(id):
    return


@app.route("/api/questions", methods=["GET"])
def apiQuestionsGet():
    getID, categ = request.args.get("id"), request.args.get("category")

    # Get single question if an ID is passed
    if getID:
        res = Question.objects(id=getID).first()
        if not res:
            return make_response({"error pos 1": res}, 404)
        else:
            return make_response(res.to_json(), 200)

    # Return ALL questions if nothing is specified
    if categ == None:
        return (jsonify(Question.objects), 200)

    # Return a list of all questions in their respective categories
    if categ == "_all_":
        op = {}
        for category in Categories.objects:

            op[category.name] = []
            for questionID in category.assocQuestions:
                op[category.name].append(Question.objects(id=questionID).first())
        return op

    # Return a list of all questions in a single category
    question = Question.objects(category=categ)
    if not question:
        return make_response(
            "This category either doesn't exist or has no questions assigned to it", 404
        )

    return (jsonify(question), 200)


# creates questions
@app.route("/api/questions", methods=["POST"])
def createQuestion():
    requestData = request.get_json()
    answer = requestData["answer"]

    try:
        question = Question(
            category=requestData["category"],
            questionType=requestData["questionType"],
            answer=answer,
            poll=requestData["poll"] if "poll" in requestData else None,
            title=requestData["title"],
            bodyMD=requestData["bodyMD"],
            videoURL=requestData["videoURL"],
            imageURL=requestData["imageURL"],
        )
        question.save()
    except Exception as e:
        prRed(e)
        return (jsonify("BAD REQUEST"), 400)
    else:
        return question.to_json()


# Edits Question
@app.route("/api/questions", methods=["PUT"])
def editsQuestion():
    requestData = request.get_json()
    id = requestData["id"]
    question = Question.objects(id=id).first()
    try:
        if "category" in requestData:
            question.category = requestData["category"]
        if "questionType" in requestData:
            question.questionType = requestData["questionType"]
        if "answer" in requestData:
            question.answer = requestData["answer"]
        if "poll" in requestData:
            question.poll = requestData["poll"]
        if "title" in requestData:
            question.title = requestData["title"]
        if "bodyMD" in requestData:
            question.bodyMD = requestData["bodyMD"]
        if "videoURL" in requestData:
            question.videoURL = requestData["videoURL"]
        if "imageURL" in requestData:
            question.imageURL = requestData["imageURL"]
        question.save()
    except Exception:

        return (jsonify("BAD REQUEST"), 400)
    else:
        return question.to_json()


@app.route("/api/questions", methods=["DELETE"])
def deletesQuestions():
    try:
        requestData = request.get_json()
        id = requestData["id"]
        question = Question.objects(id=id).first()
        if not question:
            raise ResourceNotFound(resourceType="question")
        question.delete()
    except ResourceNotFound:
        prRed(f"Question with ID {id} does not exist")
        return (jsonify(f"Question with ID {id} does not exist"), 404)
    except Exception:
        prRed("Bad request")
        return (jsonify("BAD REQUEST"), 400)
    else:
        prYellow(f"Question {id} deleted")
        return jsonify("success")


@app.route("/api/categories", methods=["GET"])
def getCategories():
    return (jsonify(Categories.objects), 200)


@app.route("/api/categories", methods=["POST"])
def postCategories():
    requestData = request.get_json()
    try:
        catg = Categories(name=requestData["name"])
        catg.save()
    except Exception:

        return (jsonify("BAD REQUEST"), 400)
    else:
        return jsonify(catg)


@app.route("/api/categories", methods=["PUT"])
def putCategories():
    requestData = request.get_json()
    id = requestData["id"]

    category = Categories.objects(id=id).first()
    try:
        category.name = requestData["name"]
        category.save()
    except Exception:
        return ("error", 400)
    else:
        return jsonify(category)


@app.route("/api/categories", methods=["DELETE"])
def deletesCategories():
    requestData = request.get_json()
    try:
        id = requestData["id"]
        migrateTo = requestData["migrateTo"]
        category = Categories.objects(id=id).first()
        if not category:
            raise ResourceNotFound(resourceType="category")
        if not category.assocQuestions:
            category.delete()
        else:
            for questions in category.assocQuestions():
                quessy = Question.objects(id=questions).first()
                quessy.category = migrateTo
                quessy.save()
                category.delete()
    except Exception as e:
        prRed(e)
        prRed("Bad Request")
        traceback.print_exc()
        return (jsonify("BAD REQUEST"), 400)
    else:
        prYellow(f"{id} category deleted")
        return jsonify("success")


@app.route("/api/rooms", methods=["DELETE"])
@app.route("/activeRooms/Delete/All", methods=["DELETE"])
def deleteAllActiveRooms():
    for room in ActiveRooms.objects:
        room.delete()
    prYellow("All rooms deleted")
    return "success"


@app.route("/api/quizzes", methods=["DELETE"])
@app.route("/quizzes/Delete/All", methods=["DELETE"])
def deleteAllQuizzes():
    for quiz in Quizzes.objects:
        quiz.delete()
    prYellow("All quizzes deleted")
    return "success"


@app.route("/api/quenswers", methods=["DELETE"])
@app.route("/quenswers/Delete/All", methods=["DELETE"])
def deleteAllQuenswers():
    for quenswer in Quenswers.objects:
        quenswer.delete()
    prYellow("All quenswers deleted")
    return "success"


@app.route("/api/quizzes", methods=["GET"])
def retrieveQuizzes():
    quizID = request.args.get("id")
    if quizID == None:
        return jsonify(Quizzes.objects), 200
    return jsonify(Quizzes.objects(id=quizID).first()), 200


@app.route("/quizzes/all", methods=["GET"])
def getAllQuizzes():
    return (jsonify(Quizzes.objects), 200)


@app.route("/api/marking", methods=["GET"])
@app.route("/marking", methods=["GET"])
def markingGet():

    op = []
    quizID = request.args.get("id")

    quiz = Quizzes.objects(id=quizID).first()

    for quenswerId in quiz.quenswerId:
        quensObj = Quenswers.objects(id=quenswerId).first()
        questObj = Question.objects(id=quensObj.questionId).first()
        userObj = UserType.objects(id=quensObj.userId).first()
        userOp = {
            "firstName": userObj.firstName,
            "lastName": userObj.lastName,
            "email": userObj.email,
            "hostOrTest": userObj.hostOrTest,
            "id": str(userObj.pk),
        }
        op.append({"quenswer": quensObj, "question": questObj, "user": userOp})

    return jsonify(op)


# Batch mark quenswers by ID
@app.route("/api/mark/", methods=["POST"])
def batchMark():
    requestData = request.get_json()
    # Check necessary data
    if not logic.assertExists(["userID", "toMark"], requestData):
        return ("Insufficent data", 400)

    if len(requestData["toMark"]) < 1:
        return ("toMark cannot be empty", 400)
    returnValue = []
    thisMarker = UserType.objects(id=requestData["userID"]).first()

    thisMarkerName = str("{} {}".format(thisMarker.firstName, thisMarker.lastName))

    try:
        for qid, outcome in requestData["toMark"].items():
            thisQuenswer = Quenswers.objects(id=qid).first()
            if thisQuenswer == None:
                return ("One or more quenswer IDs are invalid", 400)
            thisQuenswer.correct = "true" if outcome else "false"
            thisQuenswer.markedBy = thisMarkerName
            thisQuenswer.markedDateTime = datetime.datetime.now()
            thisQuenswer.save()
            returnValue.append(thisQuenswer)

    except Exception as e:
        prRed(e)
    else:
        prGreen(f"Multiple Quenswers marked successfully")
        return jsonify(returnValue), 200


# 'Mark' an individual quenswer by ID
@app.route("/api/quenswer/<qid>/mark", methods=["POST"])
def markQuenswer(qid):
    requestData = request.get_json()
    # check necessary data
    if not logic.assertExists(["correct", "userID"], requestData):
        return ("Insufficent data", 400)

    # Send shite
    try:
        thisQuenswer = Quenswers.objects(id=qid).first()
        if thisQuenswer == None:
            return "No quenswer exists with that ID", 400
        thisQuenswer.correct = requestData["correct"]
        thisQuenswer.markedBy = requestData["userID"]
        # thisQuenswer.markedDateTime = datetime.datetime.now(),
        thisQuenswer.save()

    except Exception as e:
        prRed(e)
        return "Server encountered an error", 500
    else:
        prGreen(f"Quenswer {str(thisQuenswer.pk)} was successfully marked")
        return jsonify(thisQuenswer), 200


# Get an individual quenswer by ID
@app.route("/api/quenswer/<qid>", methods=["GET"])
def getQuenswer(qid):
    try:
        thisQuenswer = Quenswers.objects(id=qid).first()
        if thisQuenswer == None:
            return "No results for that ID", 400
        return jsonify(thisQuenswer), 200
    except Exception as e:
        prRed(e)
        return "Server encountered an error", 500


@app.route("/marking", methods=["PUT"])
def putMarking():
    requestData = request.get_json()
    quenswerId = requestData["quenswerId"]
    userId = requestData["userId"]
    correct = requestData["correct"]
    quenswer = Quenswers.objects(id=quenswerId).first()
    quenswer.markedBy = userId
    quenswer.markedDateTime = datetime.datetime.now()
    quenswer.correct = "true" if correct else "false"
    quenswer.save()
    return (jsonify(quenswer), 200)


@app.route("/api/users/<id>/analytics/questions", methods=["GET"])
def analyticsGetUserQuestionShite(id):
    try:
        thisUser = UserType.objects(id=id).first()
        if thisUser == None:
            return "No user assosciated with that ID", 400
        all, correct, incorrect = [], [], []
        for q in Quenswers.objects(userId=id):
            thisID = str(q.pk)
            all.append(thisID)
            if q.correct == "true":
                correct.append(thisID)
            elif q.correct == "false":
                incorrect.append(thisID)
        return {
            "fullname": f"{thisUser.firstName} {thisUser.lastName}",
            "correctID": correct,
            "correctAmount": len(correct),
            "incorrectID": incorrect,
            "incorrectAmount": len(incorrect),
            "allID": all,
        }, 200
    except Exception as e:
        prRed(e)


@app.route("/analytics/user/questions", methods=["GET"])
def analyticsUserCorrectQuestionsGet():
    requestData = request.get_json()
    if not logic.assertExists(["userId"], requestData):
        return ("Insufficent data", 400)
    userId = requestData["userId"]
    opcorect = []
    opincorect = []
    op = {}
    allqs = []
    for quenswer in Quenswers.objects(userId=userId):
        allqs.append(str(quenswer.pk))
        if quenswer.correct == "true":
            opcorect.append(str(quenswer.pk))
        elif quenswer.correct == "false":
            opincorect.append(str(quenswer.pk))
    op["userId"] = userId
    op["correctId"] = opcorect
    op["correctLen"] = len(opcorect)
    op["incorrectId"] = opincorect
    op["incorrectLen"] = len(opincorect)
    op["allId"] = allqs
    op["allLen"] = len(allqs)
    return (jsonify(op), 200)


@app.route("/api/nocorspls", methods=["GET"])
def shitandpissreallyhard():
    theID = request.args.get("id")
    if theID == None:
        return "Bad shite", 400
    return analyticsGetSomething(theID)


@app.route("/api/categories/<cid>/analytics/", methods=["GET"])
def analyticsGetSomething(cid):

    thisCategory = Categories.objects(id=cid).first()
    if thisCategory == None:
        return "Category does not exist", 400

    all, correct, incorrect = 0, 0, 0
    easiest, hardest = None, None
    easiestResponses, hardestResponses = 0, 0
    easiestAmount, hardestAmount = 0, 0

    for question in Question.objects(category=thisCategory.name):

        thisQID = str(question.pk)
        thisQuestionCorrectAmount = 0
        thisQuestionIncorrectAmount = 0
        thisQuestionResponses = 0
        all += 1
        for quenswer in Quenswers.objects(questionId=str(question.pk)):
            thisQuestionResponses += 1
            if quenswer.correct == "true":
                correct += 1
                thisQuestionCorrectAmount += 1
            elif quenswer.correct == "false":
                incorrect += 1
                thisQuestionIncorrectAmount += 1

        if thisQuestionCorrectAmount >= easiestAmount:
            easiest = thisQID
            easiestAmount = thisQuestionCorrectAmount
            easiestResponses = thisQuestionResponses

        if thisQuestionIncorrectAmount >= hardestAmount:
            hardest = thisQID
            hardestAmount = thisQuestionIncorrectAmount
            hardestResponses = thisQuestionResponses

    easiestName = Question.objects(id=easiest).first().title
    hardestName = Question.objects(id=hardest).first().title

    return {
        "allAmount": all,
        "correctAmount": correct,
        "incorrectAmount": incorrect,
        "easiestID": easiest,
        "easiestName": easiestName,
        "easiestAmount": easiestAmount,
        "easiestResponses": easiestResponses,
        "hardestID": hardest,
        "hardestName": hardestName,
        "hardestAmount": hardestAmount,
        "hardestResponses": hardestResponses,
        "categoryName": thisCategory.name,
    }


@app.route("/analytics/categories/questions", methods=["GET"])
def analyticsCategoriesQuestionsGet():
    requestData = request.get_json()

    if not logic.assertExists(["categId"], requestData):
        return ("Insufficent data", 400)

    categId = requestData["categId"]
    categObj = Categories.objects(id=categId).first()
    correct = {}
    incorrect = {}

    for question in Question.objects(category=categObj.name):
        correct[str(question.pk)] = 0
        incorrect[str(question.pk)] = 0
        for quenswer in Quenswers.objects(questionId=str(question.pk)):
            if quenswer.correct == "true":
                correct[str(question.pk)] += 1
            elif quenswer.correct == "false":
                incorrect[str(question.pk)] += 1

    return (jsonify({"correct": correct, "incorrect": incorrect}), 200)


@app.route("/analytics/categories/user", methods=["GET"])
def analyticsCategoriesUserGet():
    requestData = request.get_json()

    if not logic.assertExists(["userId", ["categId"]], requestData):
        return ("Insufficent data", 400)

    categId = requestData["categId"]
    userId = requestData["userId"]
    categObj = Categories.objects(id=categId).first()
    correct = {}
    incorrect = {}
    for question in Question.objects(category=categObj.name):
        correct[str(question.pk)] = 0
        incorrect[str(question.pk)] = 0
        for quenswer in Quenswers.objects(questionId=str(question.pk), userId=userId):
            if quenswer.correct == "true":
                correct[str(question.pk)] += 1
            elif quenswer.correct == "false":
                incorrect[str(question.pk)] += 1
    return (jsonify({"correct": correct, "incorrect": incorrect}), 200)


############################################
# SERVER TESTING EVENTS AND HTTP ENDPOINTS #
############################################


@socketio.event
def startServer7Test():

    socketio.sleep(30)

    emit("ServerTestFinished", "the server finished testing")


@app.route("/server/testing1", methods=["GET"])
def serverTesting1():
    print("testing")
    return "the server can still handle requests"


@app.route("/exception/badRequestError")
def testBadRequestError():
    raise BadRequestError()


@app.route("/set/", methods=["GET"])
def set():
    idVar = "this is my UIDIDIDIDI"
    session["theID"] = idVar
    #
    return "ok"


@app.route("/get/", methods=["GET"])
def get():
    yolo = request.args.get("doesnei")

    return jsonify(yolo)


@app.route("/SAM/api/login", methods=["GET", "POST"])
def samCustomLogin():
    if request.method == "GET":
        return jsonify(
            {
                "session": session.get("value", ""),
                "user": current_user.firstName
                if current_user.is_authenticated
                else "anonymous",
            }
        )
    data = request.get_json()
    if "session" in data:

        session["value"] = data["session"]
    elif "email" in data:
        if data["email"]:
            email = data["email"]
            passwordHash = data["passwordHash"]
            userObj = UserType.objects(email=email, passwordHash=passwordHash).first()
            login_user(userObj)

            return "login"
        else:
            logout_user()

            return "logout"

    return "", 204


# test route
@app.route("/sm")
def sm():
    return ("yep", 200)


#######################
# API LOGIC FUNCTIONS #
#######################


def assignQuenswersToQuiz(quiz):
    for quenswer in Quenswers.objects:
        if quenswer.quizId == quiz.roomId:
            quiz.quenswerId.append(str(quenswer.pk))
    quiz.save()
    return None


def markTrueFalse(quenswerObj, questionObj):
    quenswerObj.markedBy = "System"
    quenswerObj.markedDateTime = datetime.datetime.now()
    quenswerObj.correct = (
        "true" if quenswerObj.answer[0] == questionObj.answer[0] else "false"
    )
    quenswerObj.save()


def markMultiple(quenswerObj, questionObj):
    if len(questionObj.answer) >= 2:
        for userAnswer in quenswerObj.answer:
            quenswerObj.markedBy = "System"
            quenswerObj.markedDateTime = datetime.datetime.now()
            quenswerObj.correct = (
                "true" if userAnswer in questionObj.answer else "false"
            )
            quenswerObj.save()
    else:
        quenswerObj.markedBy = "System"
        quenswerObj.markedDateTime = datetime.datetime.now()
        quenswerObj.correct = (
            "true" if quenswerObj.answer[0] == questionObj.answer[0] else "false"
        )
        quenswerObj.save()


def markNumber(quenswerObj, questionObj):
    quenswerObj.markedBy = "System"
    quenswerObj.markedDateTime = datetime.datetime.now()
    quenswerObj.correct = (
        "true"
        if float(quenswerObj.answer[0]) == float(questionObj.answer[0])
        else "false"
    )
    quenswerObj.save()


def autoMarking(quiz):

    for quenswerId in quiz.quenswerId:
        quenswerObj = Quenswers.objects(id=quenswerId).first()
        questionObj = Question.objects(id=quenswerObj.questionId).first()
        if questionObj.questionType == "trueFalse" or "multiple" or "number":
            if questionObj.questionType == "trueFalse":

                markTrueFalse(quenswerObj, questionObj)
            elif questionObj.questionType == "multiple":

                markMultiple(quenswerObj, questionObj)
            elif questionObj.questionType == "number":

                markNumber(quenswerObj, questionObj)
        else:
            pass


###############
# RUNS SERVER #
###############

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=True)


#################
# LIST OF TODOs #
#################

# TODO if a question is marked as first and last it will cause the server to not emit any questions
# TODO add a question sent time to the activeRoom object and then a questionSent time and a QuestionReceived time to the Quenswer Object
# TODO Undeleting users
