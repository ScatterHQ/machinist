.. _Basic Usage:

Basic Usage
===========

State machines are constructed using :py:func:`machinist.constructFiniteStateMachine`.

Inputs, Outputs, States
-----------------------

Before a machine can be constructed its inputs, outputs, and states must be defined.
These are all defined using :py:mod:`twisted.python.constants`.

.. testcode:: turnstile

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


Transitions
-----------

Also required is a transition table.
The transition table is defined using :py:class:`machinist.TransitionTable`.
:py:class:`TransitionTable` instances are immutable and have several methods for creating new tables including more transitions.

.. testcode:: turnstile

   from machinist import TransitionTable

   table = TransitionTable()

First, define how the ``FARE_PAID`` input is handled in the ``LOCKED`` state: output ``DISENGAGE_LOCK`` and change the state to the ``ACTIVE``.

.. testcode:: turnstile

   table = table.addTransition(
       State.LOCKED, Input.FARE_PAID, [Output.DISENGAGE_LOCK], State.ACTIVE)

Next, define how the ``ARM_TURNED`` input is handled in the ``UNLOCKED`` state: output ``ENGAGE_LOCK`` and  change the state to ``ACTIVE``.

.. testcode:: turnstile

   table = table.addTransition(
       State.UNLOCKED, Input.ARM_TURNED, [Output.ENGAGE_LOCK], State.ACTIVE)

Last, define two transitions at once for getting out of the ``ACTIVE`` state.
``addTransitions`` is a convenient way to define more than one transition at once.
It is equivalent to several ``addTransition`` calls.

.. testcode:: turnstile

   table = table.addTransitions(
       State.ACTIVE, {
           Input.ARM_UNLOCKED: ([], State.UNLOCKED),
           Input.ARM_LOCKED: ([], State.LOCKED),
       })

One thing to note here is that the outputs are  ``list``\ s of symbols from the output set.
The output of any transition in Machinist is always a ``list``.
This simplifies the definition of output symbols in many cases and grants more flexibility in how a machine can react to an input.
You can see one way in which this is useful already: the transitions out of the ``ACTIVE`` state have no useful outputs and so use an empty ``list``.
The handling of these ``list``\ s of outputs is discussed in more detail in the next section, `Output Executors`_.


Output Executors
----------------

The last thing that must be defined in order to create any state machine using Machinist is an *output executor*.
In the previous sections we saw how the outputs of a state machine must be defined and how transitions must specify the outputs of each transition.
The outputs that have been defined so far are only symbols: they can't have any impact on the world.
This makes them somewhat useless until they are combined with code that knows how to turn an output symbol into an **actual** output.
This is the output executor's job.
Machinist provides a helper for writing classes that turn output symbols into side-effects:

.. testcode:: turnstile

   from __future__ import print_function
   from machinist import MethodSuffixOutputer

   class Outputer(object):
       def output_ENGAGE_LOCK(self, engage):
           print("Engaging the lock.")

       def output_DISENGAGE_LOCK(self, disengage):
           print("Disengaging the lock.")

   outputer = MethodSuffixOutputer(Outputer())

When used as the output executor for a state machine, the methods of this instance will be called according to the names of the outputs that are produced.
That is, when a transition is executed which has :py:obj:`Output.ENGAGE_LOCK` as an output, :py:meth:`output_ENGAGE_LOCK` will be called.
This lets the application define arbitrary side-effects to associate with outputs.
In this well-defined way the otherwise rigid, structured, explicit state machine can interact with the messy world.


Construction
------------

Having defined these things, we can now use :py:func:`constructFiniteStateMachine` to construct the finite state machine.

.. testcode:: turnstile

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


Apart from the inputs, outputs, states, transition table, and output executor, the only other argument to pay attention to in this call right now is *initial*.
This defines the state that the state machine is in immediately after :py:func:`constructFiniteStateMachine` returns.


Receiving Inputs
----------------

Having created a state machine, we can now deliver inputs to it.
The simplest way to do this is to pass input symbols to the :py:attr:`receive` method:

.. testcode:: turnstile

   turnstile.receive(Input.FARE_PAID)
   turnstile.receive(Input.ARM_UNLOCKED)
   turnstile.receive(Input.ARM_TURNED)
   turnstile.receive(Input.ARM_LOCKED)

Combining all of these snippets results in a program that produces this result:

.. testoutput:: turnstile

   Disengaging the lock.
   Engaging the lock.
