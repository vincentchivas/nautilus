class ServerError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'Server Error:'+repr(self.msg)


class ClientError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'Client Error:'+repr(self.msg)


class InternalError(ServerError):
    def __init__(self, msg):
        self.msg = 'Internal error, '+msg


class ParamError(ClientError):
    def __init__(self, msg):
        self.msg = 'Parameter error, '+msg
