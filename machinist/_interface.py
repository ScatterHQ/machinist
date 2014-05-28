# Copyright Hybrid Logic Ltd.  See LICENSE file for details.
# -*- test-case-name: machinist -*-

"""
Interface definitions for machinist.
"""

__all__ = [
    "IFiniteStateMachine", "IOutputExecutor", "IRichInput",
]

from zope.interface import Attribute, Interface


class IFiniteStateMachine(Interface):
    """
    A finite state machine.
    """
    state = Attribute("The current state of the machine.")

    # We could probably make the state, input, and output types part of this
    # interface as well.  This could facilitate more advanced tools for
    # operating on state machines (eg, tools for chaining several together).

    def receive(input):
        """
        Accept an input, transition to the next state, and return the generated
        output.

        @raise UnhandledInput: If the received input is not acceptable in the
            current state.

        @raise IllegalInput: If the received input is not acceptable in any
            state by this state machine.
        """



class IOutputExecutor(Interface):
    """
    Perform tasks and cause side-effects associated with outputs from a
    L{IFiniteStateMachine}.
    """
    def identifier():
        """
        Return a constant L{unicode} string that should uniquely identify this
        executor.  This will be used to uniquely identify log events associated
        with it.

        @rtype: L{unicode}
        """


    def output(output, context):
        """
        Perform the operations associated with a particular output.

        @param output: The output symbol to execute.  This will always be one
            of the output symbols defined by the machine this
            L{IOutputExecutor} is being used with.

        @param context: The adapted rich input which triggered the output
            symbol.
        """



class IRichInput(Interface):
    """
    A L{IRichInput} implementation corresponds to a particular symbol in the
    input alphabet of a state machine but may also carry additional
    information.
    """
    def symbol():
        """
        Return the symbol from the input alphabet to which this input
        corresponds.
        """
