from base64 import b64encode
from os import urandom

from scrypt import encrypt

print((b64encode(encrypt(urandom(256), input("new passwd:"), maxtime=0.5))).decode())
