# Copyright Hybrid Logic Ltd.  See LICENSE file for details.

"""
Log-related testing helpers.

Eliot is an optional dependency.  This module provides a point of indirection
so that the rest of the test suite can ignore the details of how to work out
whether Eliot is installed or not.
"""

__all__ = [
    "MessageType", "Logger", "LoggedAction", "LoggedMessage",

    "issuperset", "assertContainsFields", "validateLogging",

    "logSkipReason",
]

try:
    from eliot import __version__
    if tuple(int(part) for part in __version__.split(".")[:2]) < (0, 4):
        raise ImportError("eliot %s is too old" % (__version__,))
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
