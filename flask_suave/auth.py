from base64 import b64encode
from binascii import b2a_hex
from os import urandom
import math
import whirlpool


class Hasher:
    def __init__(self, strength=16):
        self._strength = strength

    def hash(self, password, salt=False, encode=True):
        if salt is False:
            salt = urandom(32)
        if encode:
            salt = b64encode(salt)
        return "$w$%s$%s$%s" % (
            self._strength,
            salt,
            self._hash_multi(salt + password, self._strength)
        )

    def check(self, attempt, h):
        bits = h.split("$")
        try:
            if self._hash_multi(bits[3] + attempt, float(bits[2])) != bits[4]:
                raise HashMismatch()
        except IndexError:
            raise HashMismatch()

    def _hash_multi(self, string, strength):
        for i in range(int(math.pow(2, strength))):
            string = b2a_hex(whirlpool.hash(string))
        return string


class HashMismatch(Exception):
    pass


class Auth:
    def __init__(self, session, db, user_class):
        self.session = session
        self.db = db
        self.user_class = user_class

    def log_in(self, username, password):
        user = self.user_class.query.filter_by(username=username).first()
        if not user:
            raise AuthUserNotFoundError()

        if user.status != 'active':
            raise AuthInactiveError()

        h = Hasher()
        try:
            h.check(password, user.password)
        except HashMismatch:
            raise AuthPasswordIncorrectError()

        return user


class AuthError(Exception):
    pass


class AuthUserNotFoundError(AuthError):
    pass


class AuthPasswordIncorrectError(AuthError):
    pass


class AuthInactiveError(AuthError):
    pass


class AuthPermissionDeniedError(AuthError):
    pass
