import hashlib

SECRET_KEY = "%^&quizSystem*()SecretKey!£$"

password = input("Password to XChange: ")
passwordWiSalt = password + SECRET_KEY
passwordHash = hashlib.md5(passwordWiSalt.encode())
passwordHash = passwordHash.hexdigest()


print("goes to " + passwordHash)
