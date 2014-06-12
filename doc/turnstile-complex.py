#
# Note: This is not a runnable example!  It depends on a fictional library for
# manipulating some imaginary hardware that might drive a real-world, physical
# turnstile.  However, the machinist-using code in this file is intended to be
# realistic and correct.
#

import time

from twisted.python.constants import Names, NamedConstant

from machinist import (
    TransitionTable, MethodSuffixOutputer, constructFiniteStateMachine,
)

from turnstilelib import TurnstileController

class TurnstileInput(Names):
    FARE_PAID = NamedConstant()
    ARM_UNLOCKED = NamedConstant()
    ARM_TURNED = NamedConstant()
    ARM_LOCKED = NamedConstant()

class TurnstileOutput(Names):
    ENGAGE_LOCK = NamedConstant()
    DISENGAGE_LOCK = NamedConstant()

class TurnstileState(Names):
    LOCKED = NamedConstant()
    UNLOCKED = NamedConstant()
    ACTIVE = NamedConstant()

table = TransitionTable()
table = table.addTransitions(
    TurnstileState.UNLOCKED, {
        TurnstileInput.ARM_TURNED:
            ([TurnstileOutput.ENGAGE_LOCK], TurnstileState.ACTIVE),
    })
table = table.addTransitions(
    TurnstileState.ACTIVE, {
        TurnstileInput.ARM_LOCKED: ([], TurnstileState.LOCKED),
        TurnstileInput.ARM_UNLOCKED: ([], TurnstileState.UNLOCKED),
    })
table = table.addTransitions(
    TurnstileState.LOCKED, {
        TurnstileInput.FARE_PAID:
            ([TurnstileOutput.DISENGAGE_LOCK], TurnstileState.ACTIVE),
      })

class Turnstile(object):
    def __init__(self, hardware):
        self._hardware = hardware

    def output_ENGAGE_LOCK(self, engage):
        self._hardware.engageLock()

    def output_DISENGAGE_LOCK(self, disengage):
        self._hardware.disengageLock()

def main():
    hardware = TurnstileController(digitalPin=0x13)
    turnstileFSM = constructFiniteStateMachine(
        inputs=TurnstileInput,
        outputs=TurnstileOutput,
        states=TurnstileState,
        table=table,
        initial=TurnstileState.LOCKED,
        richInputs=[],
        inputContext={},
        world=MethodSuffixOutputer(Turnstile(hardware)),
    )
    while True:
        if hardware.paymentMade():
            hardware.resetNotification()
            turnstileFSM.receive(TurnstileInput.FARE_PAID)
        elif hardware.armTurned():
            hardware.resetNotification()
            turnstileFSM.receive(TurnstileInput.ARM_TURNED)
        elif hardware.finishedLocking():
            hardware.resetNotification()
            turnstileFSM.receive(TurnstileInput.ARM_LOCKED)
        elif hardware.finishedUnlocking():
            hardware.resetNotification()
            turnstileFSM.receive(TurnstileInput.ARM_UNLOCKED)
        else:
            time.sleep(0.1)

