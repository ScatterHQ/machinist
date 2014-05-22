# Copyright Hybrid Logic Ltd.  See LICENSE file for details.
# -*- test-case-name: machinist -*-

"""
Eliot-based logging functionality for machinist.
"""

__all__ = [
    "LOG_FSM_INITIALIZE", "LOG_FSM_TRANSITION",

    "FiniteStateLogger",

    "Field", "ActionType", "Logger",
]

from twisted.python.components import proxyForInterface

from eliot import __version__

if tuple(int(part) for part in __version__.split(".")[:2]) < (0, 4):
    raise ImportError("eliot version %s is too old for machinist")

from eliot import Field, ActionType, Logger

from ._interface import IFiniteStateMachine, IRichInput

def _system(suffix):
    return u":".join((u"fsm", suffix))


FSM_IDENTIFIER = Field.forTypes(
    u"fsm_identifier", [unicode],
    u"An unique identifier for the FSM to which the event pertains.")
FSM_STATE = Field.forTypes(
    u"fsm_state", [unicode], u"The state of the FSM prior to the transition.")
FSM_RICH_INPUT = Field.forTypes(
    u"fsm_rich_input", [unicode, None],
    (u"The string representation of the rich input delivered to the FSM, "
     u"or None, if there was no rich input."))
FSM_INPUT = Field.forTypes(
    u"fsm_input", [unicode],
    u"The string representation of the input symbol delivered to the FSM.")
FSM_NEXT_STATE = Field.forTypes(
    u"fsm_next_state", [unicode],
    u"The string representation of the state of the FSM after the transition.")
FSM_OUTPUT = Field.forTypes(
    u"fsm_output", [list], # of unicode
    u"A list of the string representations of the outputs produced by the "
    u"transition.")
FSM_TERMINAL_STATE = Field.forTypes(
    u"fsm_terminal_state", [unicode],
    u"The string representation of the terminal state entered by the the FSM.")

LOG_FSM_INITIALIZE = ActionType(
    _system(u"initialize"),
    [FSM_IDENTIFIER, FSM_STATE],
    [FSM_TERMINAL_STATE],
    u"A finite state machine was initialized.")

LOG_FSM_TRANSITION = ActionType(
    _system(u"transition"),
    [FSM_IDENTIFIER, FSM_STATE, FSM_RICH_INPUT, FSM_INPUT],
    [FSM_NEXT_STATE, FSM_OUTPUT],
    u"A finite state machine received an input made a transition.")



class FiniteStateLogger(proxyForInterface(IFiniteStateMachine, "_fsm")):
    """
    L{FiniteStateLogger} wraps another L{IFiniteStateMachine} provider and adds
    to it logging of all state transitions.
    """
    def __init__(self, fsm, logger, identifier):
        super(FiniteStateLogger, self).__init__(fsm)
        self.logger = logger
        self.identifier = identifier
        self._action = LOG_FSM_INITIALIZE(
            logger, fsm_identifier=identifier, fsm_state=unicode(fsm.state))


    def receive(self, input):
        """
        Add logging of state transitions to the wrapped state machine.

        @see: L{IFiniteStateMachine.receive}
        """
        if IRichInput.providedBy(input):
            richInput = unicode(input)
            symbolInput = unicode(input.symbol())
        else:
            richInput = None
            symbolInput = unicode(input)

        action = LOG_FSM_TRANSITION(
            self.logger,
            fsm_identifier=self.identifier,
            fsm_state=unicode(self.state),
            fsm_rich_input=richInput,
            fsm_input=symbolInput)

        with action as theAction:
            output = super(FiniteStateLogger, self).receive(input)
            theAction.addSuccessFields(
                fsm_next_state=unicode(self.state), fsm_output=[unicode(o) for o in output])

        if self._action is not None and self._isTerminal(self.state):
            self._action.addSuccessFields(
                fsm_terminal_state=unicode(self.state))
            self._action.finish()
            self._action = None

        return output


    def _isTerminal(self, state):
        """
        Determine if a state is terminal.

        A state is terminal if there are no outputs or state changes defined
        for any inputs in that state.

        @rtype: L{bool}
        """
        # This only works with _FiniteStateMachine since it uses a private
        # method of that type.
        return self._fsm._isTerminal(state)
