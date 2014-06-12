# This is example is marked up for piecewise inclusion in basics.rst.  All code
# relevant to machinist must fall between inclusion markers (so, for example,
# __future__ imports may be outside such markers; also this is required by
# Python syntax).  If you damage the markers the documentation will silently
# break.  So try not to do that.

from __future__ import print_function

# begin setup
from twisted.python.constants import Names, NamedConstant

class Input(Names):
    FARE_PAID = NamedConstant()
    ARM_UNLOCKED = NamedConstant()
    ARM_TURNED = NamedConstant()
    ARM_LOCKED = NamedConstant()

class Output(Names):
    ENGAGE_LOCK = NamedConstant()
    DISENGAGE_LOCK = NamedConstant()

class State(Names):
    LOCKED = NamedConstant()
    UNLOCKED = NamedConstant()
    ACTIVE = NamedConstant()
# end setup

# begin table def
from machinist import TransitionTable

table = TransitionTable()
# end table def

# begin first transition
table = table.addTransition(
    State.LOCKED, Input.FARE_PAID, [Output.DISENGAGE_LOCK], State.ACTIVE)
# end first transition

# begin second transition
table = table.addTransition(
    State.UNLOCKED, Input.ARM_TURNED, [Output.ENGAGE_LOCK], State.ACTIVE)
# end second transition

# begin last transitions
table = table.addTransitions(
    State.ACTIVE, {
        Input.ARM_UNLOCKED: ([], State.UNLOCKED),
        Input.ARM_LOCKED: ([], State.LOCKED),
        })
# end last transitions

# begin outputer
from machinist import MethodSuffixOutputer

class Outputer(object):
    def output_ENGAGE_LOCK(self, engage):
        print("Engaging the lock.")

    def output_DISENGAGE_LOCK(self, disengage):
        print("Disengaging the lock.")

outputer = MethodSuffixOutputer(Outputer())
# end outputer

# begin construct
from machinist import constructFiniteStateMachine

turnstile = constructFiniteStateMachine(
    inputs=Input,
    outputs=Output,
    states=State,
    table=table,
    initial=State.LOCKED,
    richInputs=[],
    inputContext={},
    world=outputer,
)
# end construct

# begin inputs
def cycle():
    turnstile.receive(Input.FARE_PAID)
    turnstile.receive(Input.ARM_UNLOCKED)
    turnstile.receive(Input.ARM_TURNED)
    turnstile.receive(Input.ARM_LOCKED)
# end inputs

if __name__ == '__main__':
    cycle()
