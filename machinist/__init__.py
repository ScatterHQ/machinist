# Copyright Hybrid Logic Ltd.  See LICENSE file for details.
# -*- test-case-name: machinist -*-

"""
General tools for building finite state machines.

A finite state machine maps simple, symbolic inputs (called the I{input
alphabet}) to simple, symbolic outputs (called the I{output alphabet}).  In
this context, I{symbolic} means that nothing differentiates the values from
each other apart from their identity.  There is no additional state attached to
inputs or outputs.

The finite state machine does this mapping in a stateful way.  The machine has
a I{current} state and the mapping between inputs and outputs may be different
for each possible value of that current state.  Current states are also
represented as simple, symbolic values.

The mapping from inputs to outputs also includes definitions for state
transitions.  The current state of the machine changes to a new value each time
an input is mapped to an output (though the new value may be the same as the
old value).

For this implementation of finite state machines, L{twisted.python.constants}
is used for the definitions of all inputs, outputs, and states.  All inputs
must be defined as L{NamedConstant} attributes of a L{Names} subclass.  All
outputs must be similarly defined on another class.  And likewise, all states
must be defined this way as well.

For example, the symbols for an extremely simple finite state machine might be
defined like this::

    from twisted.python.constants import Names, NamedConstant

    class Input(Names):
        foo = NamedConstant()

    class Output(Names):
        bar = NamedConstant()

    class State(Names):
        baz = NamedConstant()

A transition table is also required to construct a new finite state machine.
The transition table is a L{dict} that has all of the possible states as its
keys.  Associated with each key is a value that is another L{dict}.  These
inner L{dict} have inputs as their keys.  It is not required that all input
symbols be present in all of these inner L{dict}s (however it will be an error
if an input is received and missing).  The values in these inner L{dict} are
L{Transition} instances that define both the output associated with the
transition as well as the next state which will become the current state of the
machine when this transition occurs.

For example, a transition table using the inputs, outputs, and states defined
in the example above might be defined like this::

    transitions = TransitionTable({
        State.baz: {
            Input.foo: Transition([Output.bar], State.baz),
            },
        })

Taken all together these will define a state machine with one possible state
(I{baz}) which accepts one possible input (I{foo}).  When I{foo} is received
the machine will output I{bar} and transition to (remain in) the I{baz} state.

Notice that the output from a transition is actually a list of symbols from the
output alphabet - not just a single output.  This is intended to allow more
expressive side-effects without requiring a (possibly combinatorial) explosion
of the number of symbols in the output alphabet.  The order of outputs in this
list may or may not be significant: it is up to the L{IOutputExecutor}
implementation paired with the state machine.

L{constructFiniteStateMachine} is the only constructor supplied for creating a
state machine from a transition table (and some other inputs).  This
constructor performs some correctness checking of the transition table and
refuses to construct a state machine that has certain statically detectable
errors.  When it does construct a state machine, it constructs one with a
couple extra behaviors beyond the basic state machine features described above.

First, the resulting state machine automatically logs all inputs, outputs, and
state transitions it undergoes.

Second, the C{world} argument to L{constructFiniteStateMachine} (an object
which provides L{IOutputExecutor}) is passed each output from each state
transition.  C{world} is intended to encapsulate all of side-effects on the
application the state machine is part of.

The L{IFiniteStateMachine} implemented in this module also logs information
using L{eliot}.  The following events are logged:

  - the initialization of a new finite state machine
  - the receipt of an input by a finite state machine
  - the finalization of a finite state machine (by entering a terminal state)

Give the code a try (or read it) to see the particular fields these messages
have.
"""

__all__ = [
    "IFiniteStateMachine", "IOutputExecutor", "IRichInput",
    "StateMachineDefinitionError", "ExtraTransitionState",
    "MissingTransitionState", "ExtraTransitionInput",
    "MissingTransitionInput", "ExtraTransitionOutput",
    "MissingTransitionOutput", "ExtraTransitionNextState",
    "MissingTransitionNextState", "InvalidInitialState",
    "ExtraInputContext",
    "UnhandledInput", "IllegalInput", "WrongState",

    "Transition", "TransitionTable", "trivialInput",
    "constructFiniteStateMachine",
    "MethodSuffixOutputer", "stateful",

    "LOG_FSM_INITIALIZE",
    "LOG_FSM_TRANSITION",

    "__version__",
    ]

from ._interface import (
    IFiniteStateMachine, IOutputExecutor, IRichInput,
)

try:
    from ._logging import (
        LOG_FSM_INITIALIZE,
        LOG_FSM_TRANSITION,
    )
except ImportError:
    LOG_FSM_INITIALIZE = LOG_FSM_TRANSITION = None

from ._fsm import (
    StateMachineDefinitionError, ExtraTransitionState,
    MissingTransitionState, ExtraTransitionInput,
    MissingTransitionInput, ExtraTransitionOutput,
    MissingTransitionOutput, ExtraTransitionNextState,
    MissingTransitionNextState, InvalidInitialState,
    ExtraInputContext,
    UnhandledInput, IllegalInput, WrongState,

    Transition, TransitionTable, trivialInput, constructFiniteStateMachine,
    MethodSuffixOutputer, stateful,
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
