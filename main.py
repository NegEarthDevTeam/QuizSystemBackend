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

global db
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
            send(f'ID {quizId}')
            break


# join room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print('the join event was run')
    send(f'{username} has entered the quizspace', to=room, )

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

@app.route('/sm')
def sm():
    return('API is working')


@app.route('create/hostUser', methods=['POST'])
def createHostUser():
    pass


@app.route('create/testUser', methods=['POST'])
def createTestUser():
    pass


@app.route('check/userType', methods=['GET'])
def checkUserType():
    pass


if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)
