from logging import error, exception
from os import name
import logic
import random
import string
from flask_mongoengine import *
from flask_socketio import *
from flask import *
import datetime
#from dbclasses import HostUser, TestUser, Quizzes, Question
global db

app = Flask(__name__)


app.config["MONGODB_SETTINGS"] = {
    "db": "quizsystemdb",
    "host": "localhost",
    "port": 27017
}
db = MongoEngine(app)


app.secret_key = "quizSystemSecretKey"

socketio = SocketIO(app, cors_allowed_origins='*')

# create room is actually just a string generator that then initiates the quiz in the DB
# check that the room code isn't currently in sure with any of the other active quizzes


#####################
# CLASSES FOR MONGO #
#####################
class HostUser(db.Document):
    firstName = db.StringField()
    lastName = db.StringField()
    email = db.StringField()
    passwordHash = db.StringField()
    created = datetime.datetime.now()
    lastEdit = datetime.datetime.now()

    def to_json(self):
        return jsonify({
            '_id': str(self.pk),
            'First Name': self.firstName,
            'Last Name': self.lastName,
            'Email': self.email,
            'Creation Date': self.created,
            'Edit Date': self.lastEdit
        })


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


class Quizzes(db.Document):
    questions = db.ListField()
    hostId = db.StringField()
    testUsersId = db.ListField()
    timeDate = db.DateTimeField()
    def to_json(self):
        return jsonify({
            '_id': str(self.pk),
            'Questions': self.questions,
            'Host ID': self.hostId,
            'Test Users ID': self.testUsersId,
            'Time + Date': self.timeDate
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
        return josnify({
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
            '_id' : str(self.pk),
            'name' : self.name
        })

    def assocQuestions(self):
        op = []
        for question in Question.objects:
            if question.category == self.name:
                op.append(str(question.pk))
        return op

        

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
            



# raise MyCustomError

#raise MyCustomError('We have a problem')





####################
# Socket IO Events #
####################


@socketio.event
def createRoom(data):
    while True:
        quizId = ''.join(random.choice(string.ascii_lowercase)
                         for i in range(6))
        if not logic.checkRoomExists(quizId):
            logic.registerRoomExists(quizId)
            print(f'room created with quiz ID: {quizId}')
            print(data)
            emit(f'ID {quizId}')
            return(f'ID {quizId}')


# join room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print('the join event was run')
    send(f'{username} has entered the quizspace', to=room)
    emit('notify')
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
    answer = data['answer']
    questionId = data['questionId']
    print(f'received answer: {answer} for question: {questionId}')
    send('Received answer')

# Send Question to quizspace
# namespace is implied from the originating event


@socketio.event
def sendQuestion(data):
    send('QUESTION')


@socketio.event
def finishQuiz(data):
    room = data['room']
    close_room(room)


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
        hostUser = HostUser(
            firstName=requestData["firstName"],
            lastName=requestData["lastName"],
            email=requestData["email"],
            passwordHash=requestData["passwordHash"],
        )
        hostUser.save()
    except Exception:
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return (jsonify(hostUser.to_json()))

# creates test users


@app.route('/create/testUser', methods=['POST'])
def createTestUser():
    try:
        requestData = request.get_json()
        testUser = TestUser(
            email=requestData["email"],
        )
        testUser.save()
    except Exception:
        print(f'There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return testUser.to_json()

# checks user types


@app.route('/check/userType', methods=['POST'])
def checkUserType():
    request_data = request.get_json()
    email = request_data['email'].lower()
    emailDomain = email.split("@", 1)[1]
    try:
        testUser = TestUser.objects(email=email).first()
        hostUser = HostUser.objects(email=email).first()
        if emailDomain != "negearth.co.uk":
            raise NotNegResource('Please use a NEG Earth Email address')
        if not testUser and not hostUser:
            raise ResourceNotFound(resourceType = 'user')
    except Exception:
        print(f'There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        if hostUser:
            return jsonify('hostUser')
        if testUser:
            return jsonify('testUser')


@app.route('/api/questions', methods=['GET'])
def apiQuestionsGet():
        
        request_data = request.get_json()
        catPres = False
        try:
            if request_data["category"] != "":
                global category
                category = request_data['category']
                catPres = True
                op = {}
                x = 0
                if not catPres:
                    for question in Question.objects:
                        op[x] = question
                        x += 1
                if catPres:
                    question = Question.objects(category=category).first()
                    # Error handling
                    if question:
                        for question in Question.objects(category=category):
                            op[x] = question.to_json()
                            x += 1
        except TypeError:
            print("requestBody was Empty")
            return(jsonify('BAD REQUEST'), 400)
        except Exception:
            print("requestBody was Empty")
            return(jsonify('BAD REQUEST'), 400)
        else:
            return(jsonify(op), 200)


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

#Edits Question
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
            raise ResourceNotFound(resourceType = 'question')
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
    op = {}
    x = 0
    for category in Categories.objects:
        op[x] = category.to_json()
        x += 1
    return op

@app.route('/api/categories', methods=["POST"])
def postCategories():
    requestData = request.get_json()
    try:
        catg = Categories(
            name = requestData['name']
        )
        catg.save()
    except Exception:
        print('There was an error in this request')
        return (jsonify('BAD REQUEST'), 400)
    else:
        return(jsonify(catg.to_json()))


@app.route('/api/categories', methods=["PUT"])
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
        return(jsonify(category.to_json()))

@app.route('/api/categories', methods=["DELETE"])
def deletesCategories():
    requestData = request.get_json()
    try:
        id = requestData["id"]
        migrateTo = requestData["migrateTo"]
        category = Categories.objects(id=id).first()
        if not category:
            raise ResourceNotFound(resourceType = 'category')
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
