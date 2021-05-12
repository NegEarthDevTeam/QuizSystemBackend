import globals

def checkRoomExists(room):
    if room in globals.CURRENT_QUIZZES:
        return True
    else:
        return False

def registerRoomExists(room):
    globals.CURRENT_QUIZZES[room] = 'active'