from logging import error, exception
from warnings import catch_warnings
import logic
import random
import string
import math
import time
from flask_mongoengine import *
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

global db

app = Flask(__name__)


app.config["MONGODB_SETTINGS"] = {
    "db": "quizsystemdb",
    "host": "localhost",
    "port": 27017,
}
db = MongoEngine(app)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "quizSystemSecretKey"
# app.config['SESSION_PERMANENT'] = False

login_manager = LoginManager(app)
Session(app)

app.secret_key = "quizSystemSecretKey"


socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)


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
    quizEnvId = db.StringField()
    quizId = db.StringField()
    markedBy = db.StringField()
    markedDateTimeStr = db.StringField()
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
                "Marked Date Time String": self.markedDateTimeStr,
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
def login():
    request_data = request.get_json()
    data = request_data
    print("login")
    print(session.keys())
    print(session.values())
    print(session.sid)
    if "session" in data:
        session["value"] = data["session"]
    elif "email" in data:
        if data["email"]:
            email = request_data["email"]
            if "passwordHash" in request_data:
                passwordHash = request_data["passwordHash"]
            else:
                passwordHash = request_data["email"]
            userObj = UserType.objects(email=email, passwordHash=passwordHash).first()
            if userObj:
                login_user(userObj)
                userObj.update(lastSignIn=datetime.datetime.now())

                return (jsonify({"status": "success", "userID": userObj.get_id()}), 200)
            else:
                return (jsonify("Username or password error"), 401)


@socketio.on("socketLogin")
def socketLogin(data):
    # request_data = request.get_json()
    # data = request_data
    print("socketLogin")
    print(session.keys())
    print(session.values())
    print(session.sid)
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

                send({"status": "success", "userID": userObj.get_id()})
            else:
                send("Username or password error")


# logout route


@app.route("/api/hostLogout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return (jsonify("logout success"), 200)


@app.route("/api/displayHostUserInfo", methods=["POST"])
def user_info():
    if current_user.is_authenticated:
        return (current_user.to_json(), 200)


@app.route("/api/isUserLoggedIn", methods=["GET"])
def apiIsUserLoggedIn():
    if current_user.is_authenticated:
        print(f"User ID is {current_user.get_id()}")
        return "True"
    elif not current_user.is_authenticated:
        return "False"


####################
# Socket IO Events #
####################

# @app.route('/socketIO/API/createRoom2', methods=["POST"])
@socketio.on("createRoom")
def createRoom(data):
    # print(session.get('currentUser', 'user not found'))
    # if current_user.is_authenticated:
    quizId = "".join(random.choice(string.ascii_uppercase) for i in range(6))
    print("createRoom")
    print(data)
    print(session.keys())
    print(session.values())
    print(session.sid)
    questions = data["questionIDs"]
    if len(questions) == 0:
        print("questions len was 0")
        return ("error", 400)
    timeLimit = data["timeLimit"]
    requestUserId = data["userID"]
    quizStarted = "False"
    questionCompleted = []
    for question in questions:
        questionCompleted.append("")
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
    print(f"room created with quiz ID: {quizId}")
    # emit('id', f'ID {quizId}', namespace='/', )
    join_room(quizId)
    return quizId


# join room
@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    userPk = data["userID"]

    roomObj = ActiveRooms.objects(roomId=room).first()
    print("the join event was run")
    print(data.keys())
    print(data.values())
    emit("joinRoom", roomObj.timeLimit)

    roomObj.connectedUserId.append(userPk)
    roomObj.allConnectedUsers.append(userPk)
    roomObj.save()
    print("emitting onRoomUpdated")

    thisNewUser = UserType.objects(id=userPk).first()
    newUserName = thisNewUser.firstName + " " + thisNewUser.lastName
    tempArray = [
        UserType.objects(id=id).first().firstName
        + " "
        + UserType.objects(id=id).first().lastName
        for id in roomObj.connectedUserId
    ]
    print(tempArray)
    emit("onRoomUpdated", newUserName, to=room)
    return (tempArray, roomObj.timeLimit)


# exit room


@socketio.on("leave")
def on_leave(data):
    print("leave")
    username = data["username"]
    room = data["room"]
    leave_room(room)

    print("the ")
    send(username + " has left the quizspace.", to=room)


# submit quiz answer


@socketio.event
def submitAnswer(data):
    print("data")
    print(data)
    curUserId = data["userID"]["userID"]
    print("submitAnswer")
    roomId = data["room"]["roomCode"]
    print(f"roomID: {roomId}")
    print(data)
    print(curUserId)
    quizEnv = ActiveRooms.objects(roomId=roomId).first()

    thisAnswer = Quenswers(
        userId=str(curUserId),
        questionId=quizEnv.currentQuestion,
        answer=data["Answer"] if isinstance(data["Answer"], list) else [data["Answer"]],
        submitDateTime=datetime.datetime.now(),
        quizEnvId=str(quizEnv.pk),
        quizId=quizEnv.roomId,
        markedBy="None",
        markedDateTimeStr="None",
        correct="unMarked",
    )
    thisAnswer.save()
    # checks to see if this answer was the last one for the quizEnv
    print(f".count is{Quenswers.objects(quizEnvId=str(quizEnv.pk)).count()}")
    print(f"len -1 is {len(quizEnv.connectedUserId) - 1}")

    if (
        Quenswers.objects(quizEnvId=str(quizEnv.pk)).count()
        % (len(quizEnv.connectedUserId) - 1)
        == 0
    ):
        quizEnvUpToDate = ActiveRooms.objects(roomId=roomId).first()
        currQuestionListIndex = quizEnvUpToDate.allQuestions.index(
            quizEnvUpToDate.currentQuestion
        )
        if quizEnvUpToDate.questionCompleted[currQuestionListIndex] == "true":
            pass
        else:
            quizEnvUpToDate.questionCompleted[currQuestionListIndex] = "true"
            quizEnvUpToDate.save()
            print("server woke, emiting timeout")
            emit("questionTimeout", to=roomId)
    else:
        print("still more users to answer")

    return "yis"


# Send Question to quizspace
# namespace is implied from the originating event


@socketio.event
def startQuiz(data):
    curUserId = data["userID"]
    print("startQuiz")
    print(data.keys())
    print(data.values())
    quizEnv = ActiveRooms.objects(connectedUserId=curUserId).first()
    quizEnv.quizStarted = "True"
    quizEnv.save()

    try:
        op = {}
        roomId = data["room"]
        print(f"var room Id {roomId}")
        quizEnv = ActiveRooms.objects(roomId=roomId).first()
        questionLs = quizEnv.questions
        print(f"quizEnv roomId {quizEnv.roomId}")
        print(quizEnv.questions)
        print(f"request.sid is {request.sid}")
        curQuestion = questionLs[0]
        quizEnv.currentQuestion = curQuestion
        quizEnv.questions.remove(curQuestion)
        quizEnv.firstQuestion = "True"
        quizEnv.save()

        if quizEnv.lastQuestion == "True":
            print("was last question")
            raise LastQuestion(f"LastQuestion for room {quizEnv.roomId}")

        print(f"questions list length is {len(quizEnv.questions)}")
        print(quizEnv.questions)
        if len(quizEnv.questions) == 0:
            print("lastQuestion = True")
            op["lastQuestion"] = "True"
            quizEnv.lastQuestion = "True"
        else:
            print("lastQuestion = False")
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
        print("type of finishQuestion")
        print(type(op["finishQuestion"]))
        print("finishQuestion")
        print(op["finishQuestion"])

        emit("startedQuiz", (len(questionLs)), to=roomId)

        print("the quizEnv firstQuestion should have been set by now")
        print(quizEnv.currentQuestion)
    except Exception as err:
        print("there was an error")
        print(err)
        send("There were no questions in this quiz")
    else:
        print(op)


@socketio.event
def sendQuestion(data):
    try:
        print("sendQuestionEvent")
        send("question was sent")
        op = {}
        roomId = data["room"]
        print(roomId)
        quizEnv = ActiveRooms.objects(roomId=roomId).first()
        print(quizEnv.roomId)
        if quizEnv.lastQuestion == "True":
            print("was last question")
            raise LastQuestion(quizEnv.roomId)

        print(f"questions list length is {len(quizEnv.questions)}")
        print(quizEnv.questions)

        questionLs = quizEnv.questions
        print(quizEnv.questions)
        print(questionLs)

        if quizEnv.firstQuestion == "True":
            curQuestion = quizEnv.currentQuestion
            quizEnv.firstQuestion = "False"
        else:
            curQuestion = questionLs[0]
            quizEnv.currentQuestion = curQuestion
            quizEnv.questions.remove(curQuestion)

        thisRoom = data["room"]

        if len(quizEnv.questions) == 0:
            print("lastQuestion = True")
            op["lastQuestion"] = "True"
            quizEnv.lastQuestion = "True"
        else:
            print("lastQuestion = False")
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
        # strCurrentTime = datetime.datetime.now()
        # op["currentTime"] = str(strCurrentTime)
        # strFinishQuestion = datetime.datetime.now(
        # ) + datetime.timedelta(seconds=quizEnv.timeLimit)
        # op["finishQuestion"] = str(strFinishQuestion)
        tempUnixTimeInMS = time.time_ns() / 1000000
        op["finishQuestion"] = math.floor(tempUnixTimeInMS + quizEnv.timeLimit * 1000)
        print(f'Value of "time limit": {quizEnv.timeLimit}')
        print("type of finishQuestion")
        print(type(op["finishQuestion"]))
        print("finishQuestion")
        print(op["finishQuestion"])
    except LastQuestion as lqe:
        print(f"caught that fact it was the last question for room {lqe}")
    except Exception:
        print("there was an error")
    else:
        print(type(op))
        print(op)
        emit("receiveQuestion", op, to=thisRoom)
        print(f"server sleeping for {quizEnv.timeLimit} seconds")
        socketio.sleep(quizEnv.timeLimit)
        quizEnvUpToDate = ActiveRooms.objects(roomId=roomId).first()
        currQuestionListIndex = quizEnvUpToDate.allQuestions.index(
            quizEnvUpToDate.currentQuestion
        )
        if quizEnvUpToDate.questionCompleted[currQuestionListIndex] == "true":
            pass
        else:
            quizEnvUpToDate.questionCompleted[currQuestionListIndex] = "true"
            quizEnvUpToDate.save()
            print("server woke, emiting timeout")
            emit("questionTimeout", to=thisRoom)
        #   print(op)


@socketio.event
def finishQuiz(data):
    print("finish quiz")
    room = data["room"]
    # close_room(room)
    curUserId = data["userID"]
    quizEnv = ActiveRooms.objects(connectedUserId=curUserId).first()

    for quenswer in Quenswers.objects():
        pass

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
    assignQuenswersToQuiz(quiz)
    # TODO make the server attempt at self marking


############################
# SOCKETIO LOGIC FUNCTIONS #
############################


def addUserToRoom(room, userPK):
    roomObj = ActiveRooms.objects(roomId=room).first()
    roomObj.connectedUserId.append(userPK)
    roomObj.allConnectedUsers.append(userPK)
    roomObj.save()
    onRoomUpdated(room)
    print("emitting onRoomUpdated")
    # emit("onRoomUpdated", connectedusers, to=roomId)


def removeUserFromRoom(roomId, userId):
    room = ActiveRooms.objects(roomId=roomId).first()
    try:
        room.connectedUserId.remove(userId)
        room.save()
    except ValueError:
        return (jsonify("User wasnt in the room"), 404)
    except Exception:
        print("There was an error in this request")
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
    print("emitting onRoomUpdated")
    emit("onRoomUpdated", op, to=roomId)


#################
# API ENDPOINTS #
#################


# GET Users


@app.route("/get/users", methods=["GET"])
def getUsers():
    reqID, reqType = request.args.get("id"), request.args.get("type")

    def getUserById(id):
        print("getUserById")
        user = UserType.objects(id=id).exclude("passwordHash").first()
        return user

    def getUserByType(type):
        print("getUserByType")
        op2 = []
        for user in UserType.objects(hostOrTest=type):
            op2.append(
                UserType.objects(id=str(user.pk)).exclude("passwordHash").first()
            )
        return op2

    def getAllUsers():
        print("getAllUsers")
        print(UserType.objects)
        op3 = {}
        for user in UserType.objects:
            op3[user.get_id()] = (
                UserType.objects(id=str(user.pk)).exclude("passwordHash").first()
            )
        print(op3)
        return op3

    if reqID and reqType:
        return ("Cannot filter by both type and ID.", 400)

    if reqID:
        return jsonify(getUserById(reqID))

    if reqType:
        return jsonify(getUserByType(reqType))

    return jsonify(getAllUsers())


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
        print(ud)
        return (jsonify("User is registered as deleted"), 400)
    except UserAlreadyExist as uae:
        print(uae)
        return (jsonify("User already exists"), 400)
    except Exception as e:
        print("There was an error in this request")
        print(e)
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
        print(ud)
        return (jsonify("User is registered as deleted"), 400)
    except UserAlreadyExist as uae:
        print(uae)
        return (jsonify("User already exists"), 400)
    except Exception as e:
        print("There was an error in this request")
        print(e)
        return (jsonify("BAD REQUEST"), 400)
    else:
        return jsonify(testUser)


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
        print("there was an error in the '/edit/testUser' 'PUT' request")
        return (jsonify("BAD REQUEST"), 400)
    else:
        testUser.save()
        return testUser.to_json()


@app.route("/delete/user", methods=["DELETE"])
def deleteUsers():
    requestData = request.get_json()
    id = requestData["id"]
    try:
        userObj = UserType.objects(id=id).first()
        userObj.hostOrTest = "deleted"
        userObj.save()
    except Exception:
        print("There was an error in this request")
        return (jsonify("BAD REQUEST"), 400)
    else:
        return jsonify({f"STATUS": "{id} set to deleted"})


# checks user types


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
            print(category.assocQuestions)
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
    try:
        question = Question(
            category=requestData["category"],
            questionType=requestData["questionType"],
            answer=requestData["answer"],
            poll=requestData["poll"] if "poll" in requestData else None,
            title=requestData["title"],
            bodyMD=requestData["bodyMD"],
            videoURL=requestData["videoURL"],
            imageURL=requestData["imageURL"],
        )
        question.save()
    except Exception:
        print("There was an error in this request")
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
        print("There was an error in this request")
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
        print("Question Not Found")
        return (jsonify(f"Question with ID {id} does not exist"), 404)
    except Exception:
        print("There was an error in this request")
        return (jsonify("BAD REQUEST"), 400)
    else:
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
        print("There was an error in this request")
        return (jsonify("BAD REQUEST"), 400)
    else:
        return jsonify(catg)


@app.route("/api/categories", methods=["PUT"])
def putCategories():
    requestData = request.get_json()
    id = requestData["id"]
    print(id)
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
        if not category.assocQuestions():
            category.delete()
        else:
            for questions in category.assocQuestions():
                quessy = Question.objects(id=questions).first()
                quessy.category = migrateTo
                quessy.save()
                category.delete()
    except Exception:
        print("There was an error in this request")
        return (jsonify("BAD REQUEST"), 400)
    else:
        return jsonify("success")


@app.route("/activeRooms/Delete/All", methods=["DELETE"])
def deleteAllActiveRooms():
    for room in ActiveRooms.objects:
        room.delete()
    return "success"


@app.route("/quizzes/Delete/All", methods=["DELETE"])
def deleteAllQuizzes():
    for quiz in Quizzes.objects:
        quiz.delete()
    return "success"


@app.route("/quenswers/Delete/All", methods=["DELETE"])
def deleteAllQuenswers():
    for quenswer in Quenswers.objects:
        quenswer.delete()
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


@app.route("/marking", methods=["GET"])
def markingGet():
    op = []
    quizID = request.args.get("id")
    print(quizID)
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
    print("this is the output of marking GET")
    print(op)
    return jsonify(op)


@app.route("/marking", methods=["PUT"])
def putMarking():
    requestData = request.get_json()
    quenswerId = requestData["quenswerId"]
    userId = requestData["userId"]
    correct = requestData["correct"]
    quenswer = Quenswers.objects(id=quenswerId).first()
    quenswer.markedBy = userId
    quenswer.markedDateTimeStr = str(datetime.datetime.now())
    quenswer.correct = correct
    quenswer.save()
    return (jsonify(quenswer), 200)


############################################
# SERVER TESTING EVENTS AND HTTP ENDPOINTS #
############################################


@socketio.event
def startServer7Test():
    print("server test started")
    # print(data)
    print("socket sleeping for 30 seconds")
    socketio.sleep(30)
    print("socket waking")
    emit("ServerTestFinished", "the server finished testing")


@app.route("/server/testing1", methods=["GET"])
def serverTesting1():
    print(
        """
    #########################
    # THE SERVER IS TESTING #
    #########################
    """
    )
    return "the server can still handle requests"


@app.route("/exception/badRequestError")
def testBadRequestError():
    raise BadRequestError()


@app.route("/set/", methods=["GET"])
def set():
    idVar = "this is my UIDIDIDIDI"
    session["theID"] = idVar
    # print(f"idVar is {idVar}")
    return "ok"


@app.route("/get/", methods=["GET"])
def get():
    yolo = request.args.get("doesnei")
    print(yolo)
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
        print("session in data")
        session["value"] = data["session"]
    elif "email" in data:
        if data["email"]:
            email = data["email"]
            passwordHash = data["passwordHash"]
            userObj = UserType.objects(email=email, passwordHash=passwordHash).first()
            login_user(userObj)
            print("login")
            print(session.keys())
            print(session.values())
            return "login"
        else:
            logout_user()
            print("logout")
            return "logout"
    print("things didnt go to plan")
    return "", 204


# test route
@app.route("/sm")
def sm():
    return ("yep", 200)


#######################
# API LOGIC FUNCTIONS #
#######################


def assignQuenswersToQuiz(quiz):
    print("trying to asssign quenswers")
    for quenswer in Quenswers.objects:
        if quenswer.quizId == quiz.roomId:

            quiz.quenswerId.append(str(quenswer.pk))

    quiz.save()
    return None


###############
# RUNS SERVER #
###############

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=True)
