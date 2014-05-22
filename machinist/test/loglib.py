__all__ = [
    "MessageType", "Logger", "LoggedAction", "LoggedMessage",

    "issuperset", "assertContainsFields", "validateLogging",

    "logSkipReason",
]

try:
    __import__("eliot")
except ImportError as e:
    class MessageType(object):
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self):
            return self

        def write(*args, **kwargs):
            pass

    Logger = lambda *args, **kwargs: None

    LoggedAction = LoggedMessage = issuperset = assertContainsFields = None

    def validateLogging(*args, **kwargs):
        def decorator(function):
            def logger(self):
                return function(self, None)
            return logger
        return decorator

    logSkipReason = str(e)
else:
    from eliot import MessageType, Logger
    from eliot.testing import (
        issuperset, assertContainsFields, LoggedAction, LoggedMessage,
        validateLogging,
    )
    logSkipReason = None
