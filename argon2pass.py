from argon2 import PasswordHasher
from argon2 import exceptions as Argon2Exceptions

ph = PasswordHasher()

print("Use this to get argon2 hashes from plaintext")

try:
    while True:
        p = input("Plain text password:")
        op = ph.hash(p)
        print(f"{p} -> {op}")
except KeyboardInterrupt as e:
    print("Goodbye.")
except EOFError as e:
    print("Goodbye.")
except Exception as e:
    print(e)
