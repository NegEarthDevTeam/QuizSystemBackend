
CURRENT_QUIZZES = {}

def checkRoomExists(room):
    return room in CURRENT_QUIZZES

def registerRoomExists(room):
    CURRENT_QUIZZES[room] = 'active'