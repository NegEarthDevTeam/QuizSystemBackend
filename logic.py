CURRENT_QUIZZES = {}


def checkRoomExists(room):
    if room in CURRENT_QUIZZES:
        return True
    else:
        return False


def registerRoomExists(room):
    CURRENT_QUIZZES[room] = "active"


def assertExists(A: list, B: list) -> bool:
    """
    Returns true if the elements of list A also exist in list B.
    """
    for item in A:
        if not item in B:
            return False
    return True
