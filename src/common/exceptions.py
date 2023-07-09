class UserAlreadyExist(Exception):
    """"""

class UserDoesNotExist(Exception):
    """"""

class InvalidPasswordError(Exception):
    """"""

class AuthenticationError(Exception):
    """"""

class ErrorMessages(Exception):
    """"""

class ErrorMessages:
    ERROR001 = "Authentication Failed. Please verify token"
    ERROR002 = "Signature Expired"
    ERROR003 = "Signature Not Valid"