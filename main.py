from logging import error, exception
from os import name
from warnings import catch_warnings
import logic
import random
import string
from flask_mongoengine import *
from flask_socketio import *
from flask import *
import datetime
from flask_login import (
    current_user,
    LoginManager,
    login_user,
    logout_user,
    login_required,
)
global db

app = Flask(__name__)


app.config["MONGODB_SETTINGS"] = {
    "db": "quizsystemdb",
    "host": "localhost",
    "port": 27017
}
db = MongoEngine(app)

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "login"

app.secret_key = "quizSystemSecretKey"

socketio = SocketIO(app, cors_allowed_origins='*')

# create room is actually just a string generator that then initiates the quiz in the DB
# check that the room code isn't currently in sure with any of the other active quizes


#####################
# CLASSES FOR MONGO #
#####################
class HostUser(db.Document):
    firstName = db.StringField()
    lastName = db.StringField()
    email = db.StringField()
    passwordHash = db.StringField()
    created = db.DateTimeField()
    lastEdit = db.DateTimeField()
    lastSignIn = db.DateTimeField()

    def to_json(self):
        return jsonify({
            '_id': str(self.pk),
            'First Name': self.firstName,
            'Last Name': self.lastName,
            'Email': self.email,
            'Creation Date': self.created,
            'Edit Date': self.lastEdit
        })

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
        return jsonify({
            '_id': str(self.pk),
            'Email': self.email,
            'Creation Date': self.created,
            'Edit Date': self.lastEdit
        })


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
        return jsonify({
            '_id': str(self.pk),
            'First Name': self.firstName,
            'Last Name': self.lastName,
            'Email': self.email,
            'Creation Date': self.created,
            'Edit Date': self.lastEdit,
            'Last Sign In': self.lastSignIn,
            'hostOrTest': self.hostOrTest
        })

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
        if self.hostOrTest == 'test':
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

    def to_json(self):
        return jsonify({
            '_id': str(self.pk),
            'Room ID': self.roomId,
            'All Time Connected Users': self.allConnectedUsers,
            'Date and Time of Creation': self.dateTime,
            'Quiz Completed Successfully': self.quizCompletedSuccessfully,
            'Questions': self.questions,
            'Time Limit': self.timeLimit,
            'Active Room Object Id': self.activeRoomId
        })


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
        return jsonify({
            '_id': str(self.pk),
            'Category': self.category,
            'Question Type': self.questionType,
            'Answer': self.answer,
            'Poll': self.poll,
            'Title': self.title,
            'Body MD': self.bodyMD,
            'Image URL': self.imageURL,
            'VideoURL': self.videoURL,
        })


class Categories(db.Document):
    name = db.StringField()

    def to_json(self):
        return jsonify({
            '_id': str(self.pk),
            'name': self.name
        })

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
    timeLimit = db.IntField()
    currentQuestion = db.StringField()

    def to_json(self):
        return jsonify({
            '_id': str(self.pk),
            'Room ID': self.roomId,
            'Connected User IDs': self.connectedUserId,
            'All Time Connected Users': self.allConnectedUsers,
            'Date and Time of Creation': self.dateTime,
            'Questions': self.questions,
            'Time Limit': self.timeLimit,
            'Quiz Started': self.quizStarted,
            'Current Question': self.currentQuestion
        })


class Quenswers(db.Document):
    userId = db.StringField()
    questionId = db.StringField()
    answer = db.StringField()
    dateTime = db.DateTimeField()
    quizEnvId = db.StringField()

    def to_json(self):
        return jsonify({
            '_id': str(self.pk),
            'User ID': self.userId,
            'Question ID': self.questionId,
            'Answer': self.answer,
            'Date Time': self.dateTime,
            'Quiz Environment ID': self.quizEnvId
        })


# '' : self. ,

#################
# Custom Errors #
#################

class BadRequestError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return ('The request was bad')


class ResourceNotFound(Exception):
    def __init__(self, **kwargs):
        self.resourceType = kwargs['resourceType']

    def __str__(self):
        if self.resourceType == 'hostUser':
            return ('Host user not found')
        if self.resourceType == 'testUser':
            return('Test user not found')
        if self.resourceType == 'user':
            return('User not found')
        if self.resourceType == 'quiz':
            return('Quiz not found')
        if self.resourceType == 'question':
            return('Question not found')
        if self.resourceType == 'category':
            return('Category not found')


class NotNegResource(Exception):
    def __init__(self, message):
        if message:
            self.message = message
        else:
            pass

    def __str__(self):
        return('You have tried to use a non NEG resource')

############################
# Authentication Endpoints #
############################


@login_manager.user_loader
def loaduser(id):
    return UserType.objects(id=id).first()


login_manager.login_view = "login"
login_manager.session_protection = "strong"


@app.route("/api/Login", methods=["POST"])
def login():
    request_data = request.get_json()
    email = request_data["email"]
    if 'passwordHash' in request_data:
        passwordHash = request_data["passwordHash"]
    else:
        passwordHash = request_data["email"]
    userObj = UserType.objects(email=email, passwordHash=passwordHash).first()
    if userObj:
        login_user(userObj, remember=True, fresh=False)
        userObj.update(lastSignIn=datetime.datetime.now())
        return(jsonify('success'), 200)
    else:
        return(jsonify("Username or password error"), 401)

# logout route


@app.route("/api/hostLogout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return(jsonify('logout success'), 200)


@app.route("/api/displayHostUserInfo", methods=["POST"])
def user_info():
    if current_user.is_authenticated:
        return(current_user.to_json(), 200)


@app.route("/api/isUserLoggedIn", methods=["GET"])
def apiIsUserLoggedIn():
    if current_user.is_authenticated:
        print(f"User ID is {current_user.get_id()}")
        return('True')
    elif not current_user.is_authenticated:
        return('False')

####################
# Socket IO Events #
####################


@app.route('/socketIO/API/createRoom', methods=["POST"])
@socketio.event
# @login_required
def createRoom():
    quizId = ''.join(random.choice(string.ascii_lowercase)
                     for i in range(6))

    questions = []
    timeLimit = 5
    quizStarted = 'False'
    print(f"User ID is {current_user.get_id()}")
    activeRooms = ActiveRooms(
        roomId=quizId,
        connectedUserId=[current_user.get_id()],
        allConnectedUsers=[current_user.get_id()],
        dateTime=datetime.datetime.now(),
        questions=questions,
        timeLimit=timeLimit,
        quizStarted=quizStarted,
        currentQuestion="null"
    )
    activeRooms.save()
    print(f'room created with quiz ID: {quizId}')
    # CHANGEBACK emit(f'ID {quizId}')

    return(f'ID {quizId}')


# join room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    userPk = current_user.get_id()
    addUserToRoom(room, userPk)

    quizEnv = ActiveRooms.objects(roomid=room).first()
    print('the join event was run')
    emit('joinRoom', quizEnv.timeLimit)
    return True

# exit room


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    print('the ')
    send(username + ' has left the quizspace.', to=room)

# submit quiz answer


@socketio.event
def submitAnswer(data):
    curUserId = current_user.get_id()
    quizEnv = ActiveRooms.objects(connectedUserId=curUserId).first()

    Quenswers(
        userId=curUserId,
        questionId=quizEnv.currentQuestion,
        answer=data['answer'],
        dateTime=datetime.datetime.now(),
        quizEnvId=str(quizEnv.pk)
    )
    Quenswers.save()

# Send Question to quizspace
# namespace is implied from the originating event


@socketio.event
def startQuiz(data):
    curUserId = current_user.get_id()
    quizEnv = ActiveRooms.objects(connectedUserId=curUserId).first()
    quizEnv.quizStarted = "True"
    quizEnv.save()
    emit("complete")


@socketio.event
def prepareNextQuestion(data):
    emit("prepareNextQuestion", "data")


@socketio.event
def sendQuestion(data):
    op = {}
    curUserId = current_user.get_id()
    quizEnv = ActiveRooms.objects(connectedUserId=curUserId).first()
    questionLs = quizEnv.questions
    curQuestion = questionLs[0]
    quizEnv.currentQuestion = curQuestion
    quizEnv.save()
    questionLs.remove(curQuestion)
    if len(questionLs) == 0:
        op['lastQuestion'] = "True"
    else:
        op['lastQuestion'] = "False"
    questionObj = Question.objects(id=curQuestion).first()
    possAnswers = questionObj.poll
    possAnswers.append(questionObj.answer)
    op["possAnswers"] = possAnswers.sort()
    op["questionType"] = questionObj.questionType
    op["title"] = questionObj.title
    op["bodyMD"] = questionObj.bodyMD
    emit("Question", op)


@socketio.event
def finishQuiz(data):
    room = data['room']
    close_room(room)
    curUserId = current_user.get_id()
    quizEnv = ActiveRooms.objects(connectedUserId=curUserId).first()
    quiz = Quizzes(
        roomId=quizEnv.roomID,
        allConnectedUsers=quizEnv.allConnectedUsers,
        dateTime=quizEnv.dateTime,
        quizCompletedSuccessfully="True",
        questions=quizEnv.questions,
        timeLimit=quizEnv.timeLimit,
        activeRoomId=str(quizEnv.pk)
    )
    quiz.save()


############################
# SOCKETIO LOGIC FUNCTIONS #
############################

def addUserToRoom(roomId, userId):
    room = ActiveRooms.objects(roomId=roomId).first()
    room.connectedUserId.append(userId)
    room.allConnectedUsers.append(userId)
    room.save()
    onRoomUpdated(roomId)


def removeUserFromRoom(roomId, userId):
    room = ActiveRooms.objects(roomId=roomId).first()
    try:
        room.connectedUserId.remove(userId)
        room.save()
    except ValueError:
        return(jsonify('User wasnt in the room'), 404)
    except Exception:
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        pass


def onRoomUpdated(roomId):
    room = ActiveRooms.objects(roomId=roomId).first()
    connectedusers = room.connectedUserId
    room.save()
    print("emitting onRoomUpdated")
    emit("onRoomUpdated", connectedusers, to=roomId)


#################
# API ENDPOINTS #
#################

# test route
@app.route('/sm')
def sm():
    return('API is working', 200)

# creates host users


@app.route('/create/hostUser', methods=['POST'])
def createHostUser():
    requestData = request.get_json()
    try:
        hostUser = UserType(
            firstName=requestData["firstName"],
            lastName=requestData["lastName"],
            email=requestData["email"],
            passwordHash=requestData["passwordHash"],
            created=datetime.datetime.now(),
            lastEdit=datetime.datetime.now(),
            lastSignIn=datetime.datetime.now(),
            hostOrTest='host'
        )
        hostUser.save()
    except Exception as e:
        print('There was an error in this request')
        print(e)
        return (jsonify('BAD REQUEST'), 400)
    else:
        return (jsonify(hostUser))

# creates test users


@app.route('/create/testUser', methods=['POST'])
def createTestUser():
    requestData = request.get_json()
    try:
        testUser = UserType(
            firstName='Test',
            lastName='User',
            email=requestData["email"],
            passwordHash=requestData["email"],
            created=datetime.datetime.now(),
            lastEdit=datetime.datetime.now(),
            lastSignIn=datetime.datetime.now(),
            hostOrTest='test'
        )
        testUser.save()
    except Exception as e:
        print('There was an error in this request')
        print(e)
        return (jsonify('BAD REQUEST'), 400)
    else:
        return (jsonify(testUser))

# checks user types


@app.route('/check/userType', methods=['POST'])
def checkUserType():
    request_data = request.get_json()
    if request_data == None:
        return make_response({"error": "Nothing sent."}, 400)

    email = request_data['email'].lower()
    if not('@' in email):
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


@app.route('/api/questions', methods=['GET'])
def apiQuestionsGet():
    getID = request.args.get("id")

    request_data = request.get_json()
    catPres, data = False, []

    if request_data != None:
        catPres = True if "category" in request_data else False

    if getID:
        res = Question.objects(id=getID).first()
        if not res:
            return make_response({"error": res}, 404)
        else:
            return make_response(res.to_json(), 200)

    if not catPres:
        return (jsonify(Question.objects), 200)

    cat = request_data["category"]
    question = Question.objects(category=cat).first()

    if not question:
        return make_response({"error": question}, 404)

    return (jsonify(Question.objects(category=cat)), 200)


# creates questions
@app.route('/api/questions', methods=['POST'])
def createQuestion():
    requestData = request.get_json()
    try:
        question = Question(
            category=requestData["category"],
            questionType=requestData["questionType"],
            answer=requestData["answer"],
            poll=requestData["poll"],
            title=requestData["title"],
            bodyMD=requestData["bodyMD"],
            videoURL=requestData["videoURL"],
            imageURL=requestData["imageURL"]
        )
        question.save()
    except Exception:
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return question.to_json()

# Edits Question


@app.route('/api/questions', methods=['PUT'])
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
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return(question.to_json())


@app.route('/api/questions', methods=["DELETE"])
def deletesQuestions():
    try:
        requestData = request.get_json()
        id = requestData["id"]
        question = Question.objects(id=id).first()
        if not question:
            raise ResourceNotFound(resourceType='question')
        question.delete()
    except ResourceNotFound:
        print('Question Not Found')
        return(jsonify(f'Question with ID {id} does not exist'), 404)
    except Exception:
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return (jsonify("success"))


@app.route('/api/categories', methods=["GET"])
def getCategories():
    return(jsonify(Categories.objects), 200)


@app.route('/api/categories', methods=["POST"])
def postCategories():
    requestData = request.get_json()
    try:
        catg = Categories(
            name=requestData['name']
        )
        catg.save()
    except Exception:
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return(jsonify(catg))


@app.route('/api/categories', methods=["PUT"])
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
        return(jsonify(category))


@app.route('/api/categories', methods=["DELETE"])
def deletesCategories():
    requestData = request.get_json()
    try:
        id = requestData["id"]
        migrateTo = requestData["migrateTo"]
        category = Categories.objects(id=id).first()
        if not category:
            raise ResourceNotFound(resourceType='category')
        if not category.assocQuestions():
            category.delete()
        else:
            for questions in category.assocQuestions():
                quessy = Question.objects(id=questions).first()
                quessy.category = migrateTo
                quessy.save()
                category.delete()
    except Exception:
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return(jsonify("success"))


@app.route('/exception/badRequestError')
def testBadRequestError():
    raise BadRequestError()


# runs server
if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
