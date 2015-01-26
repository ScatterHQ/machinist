# Copyright Hybrid Logic Ltd.  See LICENSE file for details.

"""
Tests for L{machinist}.
"""

from zope.interface import Attribute, Interface, implementer
from zope.interface.exceptions import DoesNotImplement
from zope.interface.verify import verifyObject, verifyClass

from twisted.python.util import FancyStrMixin
from twisted.python.constants import Names, NamedConstant
from twisted.trial.unittest import TestCase

from machinist import (
    ExtraTransitionState, MissingTransitionState,
    ExtraTransitionInput, MissingTransitionInput,
    ExtraTransitionOutput, MissingTransitionOutput,
    ExtraTransitionNextState, MissingTransitionNextState,
    InvalidInitialState, UnhandledInput, IllegalInput,
    ExtraInputContext,

    IRichInput, IFiniteStateMachine,
    MethodSuffixOutputer, trivialInput,
    Transition, TransitionTable, constructFiniteStateMachine,

    WrongState, stateful,

    LOG_FSM_INITIALIZE,
    LOG_FSM_TRANSITION,
    )

from .loglib import (
    MessageType, Logger,
    issuperset, assertContainsFields, LoggedAction, LoggedMessage,
    validateLogging, logSkipReason,
)



class Input(Names):
    apple = NamedConstant()



class MoreInput(Names):
    apple = NamedConstant()
    banana = NamedConstant()


class Output(Names):
    aardvark = NamedConstant()



class State(Names):
    amber = NamedConstant()



class MoreState(Names):
    amber = NamedConstant()
    blue = NamedConstant()



class IRequiredByAardvark(Interface):
    pass



NULL_WORLD = MethodSuffixOutputer(None)



class TransitionTests(TestCase):
    """
    Tests for L{Transition}.
    """
    def test_str(self):
        """
        The string representation of a L{Transition} includes the output and
        next state it represents.
        """
        self.assertEqual(
            "<Transition output='a' nextState='b'>", str(Transition("a", "b")))


    def test_repr(self):
        """
        The other string representation of a L{Transition} includes the output
        and next state it represents.
        """
        self.assertEqual(
            "<Transition output='a' nextState='b'>", repr(Transition("a", "b")))


    def test_equal(self):
        """
        Two L{Transition} instances are equal to each other if their attributes
        have the same values.
        """
        self.assertTrue(Transition("a", "b") == Transition("a", "b"))



class TransitionTableTests(TestCase):
    """
    Tests for L{TransitionTable}.
    """
    def test_empty(self):
        """
        When constructed with no arguments, L{TransitionTable} contains a table
        with no states or transitions.
        """
        table = TransitionTable()
        self.assertEqual({}, table.table)


    def test_initial(self):
        """
        When constructed with a transition table as an argument,
        L{TransitionTable} contains exactly that table.
        """
        expected = {"foo": {"bar": Transition("baz", "quux")}}
        table = TransitionTable(expected)
        self.assertIs(expected, table.table)


    def test_addTransition(self):
        """
        L{TransitionTable.addTransition} accepts a state, an input, an output,
        and a next state and adds the transition defined by those four values
        to a new L{TransitionTable} which it returns.
        """
        table = TransitionTable()
        more = table.addTransition("foo", "bar", "baz", "quux")
        self.assertEqual({"foo": {"bar": Transition("baz", "quux")}}, more.table)


    def test_addTransitionDoesNotMutate(self):
        """
        L{TransitionTable.addTransition} does not change the L{TransitionTable}
        it is called on.
        """
        table = TransitionTable({"foo": {"bar": Transition("baz", "quux")}})
        table.addTransition("apple", "banana", "clementine", "date")
        self.assertEqual({"foo": {"bar": Transition("baz", "quux")}}, table.table)


    def test_addTransitions(self):
        """
        L{TransitionTable.addTransitions} accepts a state and a mapping from
        inputs to output, next state pairs and adds all of those transitions to
        the given state to a new L{TransitionTable} which it returns.
        """
        table = TransitionTable()
        more = table.addTransitions(
            "apple", {
                "banana": ("clementine", "date"),
                "eggplant": ("fig", "grape")})
        self.assertEqual(
            {"apple": {
                    "banana": Transition("clementine", "date"),
                    "eggplant": Transition("fig", "grape")}},
            more.table)


    def test_addTransitionsDoesNotMutate(self):
        """
        L{TransitionTable.addTransitions} does not change the
        L{TransitionTable} it is called on.
        """
        table = TransitionTable({"foo": {"bar": Transition("baz", "quux")}})
        table.addTransitions("apple", {"banana": ("clementine", "date")})
        self.assertEqual({"foo": {"bar": Transition("baz", "quux")}}, table.table)


    def test_addTerminalState(self):
        """
        L{TransitionTable.addTerminalState} returns a L{TransitionTable} that
        includes the given state in its table with no transitions defined.
        """
        table = TransitionTable()
        more = table.addTerminalState("foo")
        self.assertEqual({"foo": {}}, more.table)



class ConstructExceptionTests(TestCase):
    """
    Tests for the exceptions that L{constructFiniteStateMachine} raises when
    called with bad inputs.
    """
    def test_extraTransitionState(self):
        """
        L{ExtraTransitionState} is raised if there are any keys in
        C{transitions} that are not defined by C{state}.
        """
        extra = object()
        exc = self.assertRaises(
            ExtraTransitionState,
            constructFiniteStateMachine,
            Input, Output, State,
            TransitionTable({State.amber: {}, extra: {}}),
            State.amber, [], {}, NULL_WORLD)
        self.assertEqual(({extra},), exc.args)


    def test_missingTransitionState(self):
        """
        L{MissingTransitionState} is raised if there are any keys in
        C{transitions} that are not defined by C{state}.
        """
        exc = self.assertRaises(
            MissingTransitionState,
            constructFiniteStateMachine,
            Input, Output, State, TransitionTable({}), State.amber, [], {},
            NULL_WORLD)
        self.assertEqual(({State.amber},), exc.args)


    def test_extraTransitionInput(self):
        """
        L{ExtraTransitionInput} is raised if there are any keys in any of the
        values of C{transitions} that are not defined by C{input}.
        """
        extra = object()
        exc = self.assertRaises(
            ExtraTransitionInput,
            constructFiniteStateMachine,
            Input, Output, State,
            TransitionTable({
                    State.amber: {
                        Input.apple: Transition(Output.aardvark, State.amber),
                        extra: Transition(Output.aardvark, State.amber)}}),
            State.amber, [], {}, NULL_WORLD)
        self.assertEqual(({extra},), exc.args)


    def test_missingTransitionInput(self):
        """
        L{MissingTransitionInput} is raised if any of the values defined by
        C{input} appears in none of the values of C{transitions}.
        """
        exc = self.assertRaises(
            MissingTransitionInput,
            constructFiniteStateMachine,
            Input, Output, State,
            TransitionTable({State.amber: {}}), State.amber, [], {},
            NULL_WORLD)
        self.assertEqual(({Input.apple},), exc.args)


    def test_extraTransitionOutput(self):
        """
        L{ExtraTransitionInput} is raised if there are any output values
        defined by C{transitions} that are not defined by C{output}.
        """
        extra = object()
        exc = self.assertRaises(
            ExtraTransitionOutput,
            constructFiniteStateMachine,
            Input, Output, State,
            TransitionTable({
                    State.amber: {Input.apple: Transition([extra], None)}}),
            State.amber, [], {}, NULL_WORLD)
        self.assertEqual(({extra},), exc.args)


    def test_missingTransitionOutput(self):
        """
        L{MissingTransitionOutput} is raised if any of the values defined by
        C{output} does not appear as an output value defined by C{transitions}.
        """
        exc = self.assertRaises(
            MissingTransitionOutput,
            constructFiniteStateMachine,
            Input, Output, State,
            TransitionTable({
                    State.amber: {Input.apple: Transition([], None)}}),
            State.amber, [], {}, NULL_WORLD)
        self.assertEqual(({Output.aardvark},), exc.args)


    def test_extraTransitionNextState(self):
        """
        L{ExtraTransitionNextState} is raised if any of the next state
        definitions in C{transitions} is not defined by C{state}.
        """
        extra = object()
        exc = self.assertRaises(
            ExtraTransitionNextState,
            constructFiniteStateMachine,
            MoreInput, Output, State,
            TransitionTable().addTransitions(
                State.amber, {
                    MoreInput.apple: ([Output.aardvark], State.amber),
                    MoreInput.banana: ([Output.aardvark], extra)}),
            State.amber, [], {}, NULL_WORLD)
        self.assertEqual(({extra},), exc.args)


    def test_missingTransitionNextState(self):
        """
        L{MissingTransitionNextState} is raised if any of the values defined by
        C{state} appears nowhere in C{transitions} as a next state.
        """
        transitions = TransitionTable()
        transitions = transitions.addTransition(
            MoreState.amber, Input.apple, [Output.aardvark], MoreState.amber)
        transitions = transitions.addTerminalState(MoreState.blue)

        exc = self.assertRaises(
            MissingTransitionNextState,
            constructFiniteStateMachine,
            Input, Output, MoreState, transitions,
            MoreState.amber, [], {}, NULL_WORLD)
        self.assertEqual(({MoreState.blue},), exc.args)


    def test_nextStateNotMissingIfInitial(self):
        """
        L{MissingTransitionNextState} is not raised if a value defined by
        C{state} appears nowhere in C{transitions} as a next state but is given
        as C{initial}.
        """
        transitions = TransitionTable()
        transitions = transitions.addTransition(
            MoreState.amber, Input.apple, [Output.aardvark], MoreState.amber)
        transitions = transitions.addTerminalState(MoreState.blue)

        constructFiniteStateMachine(
            Input, Output, MoreState, transitions,
            MoreState.blue, [], {}, NULL_WORLD)


    def test_invalidInitialState(self):
        """
        L{InvalidInitialState} is raised if the value given for C{initial} is
        not defined by C{state}.
        """
        extra = object()
        transitions = TransitionTable()
        transitions = transitions.addTransition(
            State.amber, Input.apple, [Output.aardvark], State.amber)
        exc = self.assertRaises(
            InvalidInitialState,
            constructFiniteStateMachine,
            Input, Output, State, transitions,
            extra, [], {}, NULL_WORLD)
        self.assertEqual((extra,), exc.args)


    def test_extraInputContext(self):
        """
        L{ExtraInputContext} is raised if there are keys in C{inputContext}
        which are not symbols in the output alphabet.
        """
        extra = object()
        transitions = TransitionTable()
        transitions = transitions.addTransition(
            State.amber, Input.apple, [Output.aardvark], State.amber)
        exc = self.assertRaises(
            ExtraInputContext,
            constructFiniteStateMachine,
            Input, Output, State, transitions,
            State.amber, [], {extra: None}, NULL_WORLD)
        self.assertEqual(({extra},), exc.args)


    def test_richInputInterface(self):
        """
        L{DoesNotImplement} is raised if a rich input type is given which does
        not implement the interface required by one of the outputs which can be
        produced when that input is received.
        """
        apple = trivialInput(Input.apple)
        transitions = TransitionTable()
        transitions = transitions.addTransition(
            State.amber, Input.apple, [Output.aardvark], State.amber)

        self.assertRaises(
            DoesNotImplement,
            constructFiniteStateMachine,
            Input, Output, State, transitions,
            State.amber, [apple], {Output.aardvark: IRequiredByAardvark},
            NULL_WORLD)



class TrivialInputTests(TestCase):
    """
    Tests for L{trivialInput}.
    """
    def test_interface(self):
        """
        The type returned by L{trivialInput} implements L{IRichInput}.
        """
        self.assertTrue(verifyClass(IRichInput, trivialInput(Input.apple)))


    def test_interfaceOnInstance(self):
        """
        The an instance of the object returned by L{trivialInput} provides
        L{IRichInput}.
        """
        self.assertTrue(verifyObject(IRichInput, trivialInput(Input.apple)()))


    def test_symbol(self):
        """
        The C{symbol} method of the object returned by L{trivialInput} returns
        the symbol passed in.
        """
        self.assertIs(Input.apple, trivialInput(Input.apple).symbol())


    def test_repr(self):
        """
        The result of L{repr} when called with an instance of the type returned
        by L{trivialInput} is a string that mentions the symbol name and
        nothing else.
        """
        self.assertEqual("<Apple>", repr(trivialInput(Input.apple)()))


LOG_ANIMAL = MessageType(
    u"testing:fsm:animalworld:aardvark", [],
    u"An animal!  Not really.  A log event actually.  Just a distinct message "
    u"type that can be recognized by tests to verify something was logged.")

class AnimalWorld(FancyStrMixin, object):
    logger = Logger()

    def __init__(self, animals):
        """
        @param animals: A L{list} to which output animals will be appended.
        """
        self.animals = animals


    def identifier(self):
        """
        Generate a stable, useful identifier for this L{AnimalWorld}.
        """
        return u"<AnimalWorld>"


    def output_AARDVARK(self, context):
        self.animals.append((Output.aardvark, context))
        LOG_ANIMAL().write(self.logger)


class MethodSuffixOutputerTests(TestCase):
    """
    Tests for L{MethodSuffixOutputer}.
    """
    def test_wrappedIdentifier(self):
        """
        If the wrapped object has an C{identifier} method then its return value
        is returned by L{MethodSuffixOutputer.identifier}.
        """
        world = AnimalWorld([])
        outputer = MethodSuffixOutputer(world)
        self.assertEqual(world.identifier(), outputer.identifier())


    def test_fallbackIdentifier(self):
        """
        If the wrapped object has no C{identifier} method then
        L{MethodSuffixOutputer.identifier} generates an identifier for the
        wrapped object and returns that.
        """
        world = object()
        outputer = MethodSuffixOutputer(world)
        self.assertEqual(repr(world), outputer.identifier())


    def test_unicodeFallbackIdentifier(self):
        """
        If the wrapped object has no C{identifier} method then the identifier
        generated by L{MethodSuffixOutputer.identifier} is a L{unicode} string.
        """
        world = object()
        outputer = MethodSuffixOutputer(world)
        self.assertIsInstance(outputer.identifier(), unicode)


    def test_fallbackIdentifierStable(self):
        """
        If L{MethodSuffixOutputer} generates an identifier for the wrapped
        object then it generates the same identifier for all calls to
        C{identifier} regardless of changes to the wrapped object.
        """
        world = ["first state"]
        outputer = MethodSuffixOutputer(world)
        firstIdentifier = outputer.identifier()
        world.append("second state")
        secondIdentifier = outputer.identifier()
        self.assertEqual(firstIdentifier, secondIdentifier)


    def test_dispatch(self):
        """
        When L{MethodSuffixOutputer.output} is called with an input and the
        wrapped object has a method named like I{output_INPUT} where I{INPUT}
        is the name of the input given, that method is called with the context
        object given.
        """
        context = object()
        animals = []
        world = AnimalWorld(animals)
        outputer = MethodSuffixOutputer(world)
        outputer.output(Output.aardvark, context)
        self.assertEqual([(Output.aardvark, context)], animals)


    def test_prefix(self):
        """
        If a value is given for the optional second L{MethodSuffixOutputer}
        initializer argument then it is used instead of C{"output_"} as the
        method dispatch prefix.
        """
        animals = []

        class AlternatePrefixWorld(object):
            def foobar_AARDVARK(self, context):
                animals.append(context)

        context = object()
        world = AlternatePrefixWorld()
        outputer = MethodSuffixOutputer(world, "foobar_")
        outputer.output(Output.aardvark, context)
        self.assertEqual([context], animals)


    def test_repr(self):
        """
        The result of L{MethodSuffixOutputer.__repr__} is a string that
        mentions the wrapped object.
        """
        world = object()
        self.assertEqual(
            "<Output / %s>" % (world,),
            repr(MethodSuffixOutputer(world)))



class IFood(Interface):
    radius = Attribute("The radius of the food (all food is spherical)")



@implementer(IFood)
class Gravenstein(trivialInput(Input.apple)):
    # Conveniently, apples are approximately spherical.
    radius = 3



TRANSITIONS = TransitionTable()
TRANSITIONS = TRANSITIONS.addTransition(
    MoreState.amber, Input.apple, [Output.aardvark], MoreState.blue)
TRANSITIONS = TRANSITIONS.addTerminalState(MoreState.blue)


class FiniteStateMachineTests(TestCase):
    """
    Tests for the L{IFiniteStateMachine} provider returned by
    L{constructFiniteStateMachine}.
    """
    def setUp(self):
        self.animals = []
        self.initial = MoreState.amber

        self.world = AnimalWorld(self.animals)
        self.fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, self.initial,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(self.world))


    def test_interface(self):
        """
        L{constructFiniteStateMachine} returns an L{IFiniteStateMachine} provider.
        """
        self.assertTrue(verifyObject(IFiniteStateMachine, self.fsm))


    def test_initial(self):
        """
        L{IFiniteStateMachine.state} is set to the initial state.
        """
        self.assertEqual(self.initial, self.fsm.state)


    def assertOutputLogging(self, logger):
        """
        The L{IOutputExecutor} is invoked in the FSM's transition action
        context.
        """
        loggedTransition = LoggedAction.ofType(
            logger.messages, LOG_FSM_TRANSITION)[0]
        loggedAnimal = LoggedMessage.ofType(logger.messages, LOG_ANIMAL)[0]
        self.assertIn(loggedAnimal, loggedTransition.children)


    @validateLogging(assertOutputLogging)
    def test_outputFromRichInput(self, logger):
        """
        L{IFiniteStateMachine.receive} finds the transition for the given rich
        input in the machine's current state and returns the corresponding
        output.
        """
        self.fsm.logger = logger
        self.world.logger = logger
        self.assertEqual([Output.aardvark], self.fsm.receive(Gravenstein()))


    @validateLogging(assertOutputLogging)
    def test_outputFromSymbolInput(self, logger):
        """
        L{IFiniteStateMachine.receive} finds the transition for the symbol
        input in the machine's current state and returns the corresponding
        output.
        """
        self.fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, self.initial,
            [Gravenstein], {}, MethodSuffixOutputer(self.world))

        self.fsm.logger = logger
        self.world.logger = logger
        self.assertEqual([Output.aardvark], self.fsm.receive(Input.apple))


    def assertTransitionLogging(self, logger, richInput):
        """
        State transitions by L{IFiniteStateMachine} are logged.
        """
        loggedTransition = LoggedAction.ofType(
            logger.messages, LOG_FSM_TRANSITION)[0]
        assertContainsFields(
            self, loggedTransition.startMessage,
            {u"fsm_identifier": u"<AnimalWorld>",
             u"fsm_state": u"<MoreState=amber>",
             u"fsm_input": u"<Input=apple>",
             u"fsm_rich_input": richInput
             })
        self.assertTrue(loggedTransition.succeeded)
        assertContainsFields(self, loggedTransition.endMessage,
                             {u"fsm_next_state": u"<MoreState=blue>",
                              u"fsm_output": [u"<Output=aardvark>"],
                              })


    @validateLogging(assertTransitionLogging, None)
    def test_nextStateGivenSymbolInput(self, logger):
        """
        L{IFiniteStateMachine.receive} changes L{IFiniteStateMachine.state} to
        the next state defined for the given symbolic input in the machine's
        current state.
        """
        self.fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, MoreState.amber,
            [Gravenstein], {}, MethodSuffixOutputer(AnimalWorld([])), logger)
        self.fsm.logger = logger
        self.fsm.receive(Input.apple)
        self.assertEqual(MoreState.blue, self.fsm.state)


    @validateLogging(assertTransitionLogging, u"<Gravenstein>")
    def test_nextStateGivenRichInput(self, logger):
        """
        L{IFiniteStateMachine.receive} changes L{IFiniteStateMachine.state} to
        the next state defined for the given rich input in the machine's
        current state.
        """
        self.fsm.logger = logger
        self.fsm.receive(Gravenstein())
        self.assertEqual(MoreState.blue, self.fsm.state)


    def test_unhandledInput(self):
        """
        L{IFiniteStateMachine.receive} raises L{UnhandledInput} if called with
        an input that isn't handled in the machine's current state.
        """
        self.fsm.receive(Gravenstein())
        exc = self.assertRaises(UnhandledInput, self.fsm.receive,
                                Gravenstein())
        self.assertEqual((MoreState.blue, Input.apple), exc.args)


    def test_illegalRichInput(self):
        """
        L{IFiniteStateMachine.receive} raises L{IllegalInput} if called with a
        rich input that doesn't map to a symbol in the input alphabet.
        """
        banana = trivialInput(MoreInput.banana)
        exc = self.assertRaises(IllegalInput, self.fsm.receive, banana())
        self.assertEqual((MoreInput.banana,), exc.args)


    def test_illegalInput(self):
        """
        L{IFiniteStateMachine.receive} raises L{IllegalInput} if called with
        an input that isn't in the input alphabet.
        """
        exc = self.assertRaises(IllegalInput, self.fsm.receive, "not symbol")
        self.assertEqual(("not symbol",), exc.args)


    def test_inputContext(self):
        """
        The context passed to L{IOutputExecutor.output} is the input.
        """
        apple = Gravenstein()
        self.fsm.receive(apple)
        self.assertEqual([(Output.aardvark, apple)], self.animals)


    def test_FiniteStateInterpreterRepr(self):
        """
        The result of L{_FiniteStateInterpreter.__repr__} is a string that
        includes the L{IOutputExecutor} provider that
        L{_FiniteStateInterpreter} can drive.
        """
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, self.initial,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(self.world), None)
        self.assertEqual(
            repr(fsm),
            "<FSM / %s>" % (MethodSuffixOutputer(self.world),))



class IsTerminalTests(TestCase):
    """
    Tests for L{_FiniteStateMachine._isTerminal}.
    """
    def test_empty(self):
        """
        L{_FiniteStateMachine._isTerminal} returns C{True} if a state that
        defines handling of no input symbols.
        """
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])))
        self.assertTrue(fsm._isTerminal(MoreState.blue))


    def test_selfTransition(self):
        """
        L{_FiniteStateMachine._isTerminal} returns C{True} if a state defines
        handling of inputs that generate no outputs and do not change the state
        of the machine.
        """
        transitions = TRANSITIONS.addTransition(
            MoreState.blue, Input.apple, [], MoreState.blue)
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, transitions, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])))
        self.assertTrue(fsm._isTerminal(MoreState.blue))


    def test_output(self):
        """
        L{_FiniteStateMachine._isTerminal} returns C{False} if a state defines
        handling of inputs that generate any output.
        """
        transitions = TRANSITIONS.addTransition(
            MoreState.blue, Input.apple, [Output.aardvark], MoreState.blue)
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, transitions, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])))
        self.assertFalse(fsm._isTerminal(MoreState.blue))


    def test_stateChange(self):
        """
        L{_FiniteStateMachine._isTerminal} returns C{False} if a state defines
        handling of inputs that cause a state change.
        """
        transitions = TRANSITIONS.addTransition(
            MoreState.blue, Input.apple, [], MoreState.amber)
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, transitions, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])))
        self.assertFalse(fsm._isTerminal(MoreState.blue))



class FiniteStateMachineLoggingTests(TestCase):
    """
    Tests for logging behavior of the L{IFiniteStateMachine} returned by
    L{constructFiniteStateMachine}.
    """
    if logSkipReason is not None:
        skip = logSkipReason

    def test_logger(self):
        """
        L{constructFiniteStateMachine} returns a FSM that also has a C{logger}
        attribute that is an L{eliot.Logger} instance.
        """
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])))
        self.assertIsInstance(fsm.logger, Logger)


    @validateLogging(None)
    def test_loggerOverride(self, logger):
        """
        If an argument is given for the C{logger} argument to
        L{constructFiniteStateMachine} then that object is used as the logger
        of the resulting finite state machine.
        """
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])), logger)
        self.assertIs(logger, fsm.logger)


    @validateLogging(None)
    def test_initializationLogging(self, logger):
        """
        The initialization of the L{IFiniteStateMachine} created by
        L{constructFiniteStateMachine} is logged.
        """
        constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])), logger)
        self.assertTrue(
            issuperset(logger.messages[0], {
                    u"fsm_identifier": u"<AnimalWorld>",
                    u"fsm_state": u"<MoreState=amber>",
                    u"action_status": u"started",
                    u"action_type": u"fsm:initialize",
                    }))


    @validateLogging(None)
    def test_terminalLogging(self, logger):
        """
        When the L{IFiniteStateMachine} enters a terminal state the
        initialization action is finished successfully.
        """
        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, TRANSITIONS, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])), logger)

        fsm.receive(Gravenstein())

        (initialize,) = LoggedAction.of_type(
            logger.messages, LOG_FSM_INITIALIZE
        )

        assertContainsFields(
            self, initialize.end_message, {
                u"fsm_terminal_state": u"<MoreState=blue>",
                u"action_status": u"succeeded",
            }
        )

    @validateLogging(None)
    def test_noRepeatedTerminalLogging(self, logger):
        """
        When the L{IFiniteStateMachine} receives an input in a terminal state
        (and does not generate an output or change to a different state, as is
        required in terminal states) it does not re-log the completion of its
        initialization event.
        """
        # Accept this input in MoreState.blue but remain a terminal state (no
        # output, no state change).
        transitions = TRANSITIONS.addTransition(
            MoreState.blue, Input.apple, [], MoreState.blue)

        fsm = constructFiniteStateMachine(
            Input, Output, MoreState, transitions, MoreState.amber,
            [Gravenstein], {Output.aardvark: IFood},
            MethodSuffixOutputer(AnimalWorld([])), logger)

        fsm.receive(Gravenstein())
        howMany = len(logger.messages)

        fsm.receive(Gravenstein())

        # No additional initialization messages please!
        self.assertEqual([], [
                msg for msg in logger.messages[howMany:]
                if msg[u"action_type"] == u"fsm:initialize"])



class Restricted(object):
    foo = "a"
    attribute = stateful(lambda r: r.foo, "a")



class StatefulTests(TestCase):
    """
    Tests for L{stateful}.
    """
    def test_allowedSet(self):
        """
        In an allowed state, the value of the descriptor can be get and set
        using normal attribute access.
        """
        value = object()
        obj = Restricted()
        obj.attribute = value
        self.assertIs(value, obj.attribute)


    def test_allowedDelete(self):
        """
        In an allowed state, the value of the descriptor can be deleted
        using normal attribute deletion.
        """
        value = object()
        obj = Restricted()
        obj.attribute = value
        del obj.attribute
        self.assertRaises(AttributeError, getattr, obj, "attribute")


    def test_allowedDeleteMissing(self):
        """
        In an allowed state, if the descriptor has no value, an attempt to
        delete it raises L{AttributeError}.
        """
        obj = Restricted()
        self.assertRaises(AttributeError, delattr, obj, "attribute")


    def test_disallowedGet(self):
        """
        Out of the allowed states, L{WrongState} is raised by an attempt to get
        the value of the descriptor.
        """
        obj = Restricted()
        obj.foo = "b"
        self.assertRaises(WrongState, getattr, obj, "attribute")


    def test_disallowedSet(self):
        """
        Out of the allowed states, L{WrongState} is raised by an attempt to
        set the value of the descriptor.
        """
        obj = Restricted()
        obj.foo = "b"
        self.assertRaises(WrongState, setattr, obj, "attribute", object())


    def test_disallowedDelete(self):
        """
        Out of the allowed states, L{WrongState} is raised by an attempt to
        delete the value of the descriptor.
        """
        obj = Restricted()
        obj.foo = "b"
        self.assertRaises(WrongState, delattr, obj, "attribute")


    def test_typeAccess(self):
        """
        Getting the descriptor attribute from the type it is defined on returns
        the L{stateful} instance itself.
        """
        self.assertIs(Restricted.__dict__["attribute"], Restricted.attribute)
