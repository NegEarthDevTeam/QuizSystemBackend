global db
from dbclasses import *
from flask import *
from flask_socketio import *
from flask_mongoengine import *
import string
import random
import logic
import globals

app = Flask(__name__)

globals.init()

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

#test route
@app.route('/sm')
def sm():
    return('API is working')

#creates host users
@app.route('/create/hostUser', methods=['POST'])
def createHostUser():
    requestData = request.get_json()
    hostUser = HostUser(
        firstName=requestData["firstName"],
        lastName=requestData["lastName"],
        email=requestData["email"],
        passwordHash=requestData["passwordHash"],
    )
    hostUser.save()
    return hostUser.to_json()

#creates test users
@app.route('/create/testUser', methods=['POST'])
def createTestUser():
    requestData = request.get_json()
    testUser = TestUser(
        email=requestData["email"],
    )
    testUser.save()
    return testUser.to_json()

#checks user types
@app.route('/check/userType', methods=['GET'])
def checkUserType():
    request_data = request.get_json()
    email = request_data['email'].lower()
    emailDomain = email.split("@", 1)[1]
    testUser = TestUser.objects(email=email).first()
    hostUser = HostUser.objects(email=email).first()
    if emailDomain != "negearth.co.uk":
        return ("email is not a NEGEARTH email", 400)
    else:
        if testUser and hostUser:
            return ('Email is associated with both host and test user type', 400)
        if not testUser and not hostUser:
            return ('User not found')
        if hostUser:
            return ('hostUser')
        if testUser:
            return ('testUser')




#runs server
if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
