Basic Usage
===========

State machines are constructed using :py:func:`machinist.constructFiniteStateMachine`.

Inputs, Outputs, States
-----------------------

Before a machine can be constructed its inputs, outputs, and states must be defined.
These are all defined using :py:func:`twisted.python.constants`.

.. code-block:: python

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
The transition table is defined using :py:type:`machinist.TransitionTable`.
:py:type:`TransitionTable` instances are immutable and have several methods for creating new tables including more transitions.
For example, here is a transition table which defines exactly one transition.
It defines how the ``FARE_PAID`` input is handled in the ``LOCKED`` state: ``DISENGAGE_LOCK`` is output and the state machine changes to the ``ACTIVE`` state.

.. code-block:: python

   from machinist import TransitionTable

   table = TransitionTable()
   table = table.addTransition(
       State.LOCKED, Input.FARE_PAID, [Output.DISENGAGE_LOCK], State.ACTIVE)

One thing to note here is that the ouput is given as a ``list`` of symbols from the output set.
The output of any transition in Machinist is always a ``list``.
This simplifies the definition of output symbols in many cases and grants more flexibility in how a machine can react to an input.
This is discussed in more detail in the next section, `Output Executors`_.


Output Executors
----------------

The last thing that must be defined in order to create any state machine using Machinist is an *output executor*.
In the previous sections we saw how the outputs of a state machine must be defined and how transitions must specify the outputs of each transition.
The outputs that have been defined so far are only symbols: they can't have any impact on the world.
This makes them somewhat useless until they are combined with code that knows how to turn an output symbol into an **actual** output.
This is the output executor's job.
Machinist provides a helper for writing classes that turn output symbols into side-effects:

.. code-block:: python

   from __future__ import print_function
   from machinist import MethodSuffixOutputer

   class Outputer(MethodSuffixOutputer):
       def output_ENGAGE_LOCK(self, engage):
           print("Engaging the lock.")

       def output_DISENGAGE_LOCK(self, disengage):
           print("Disengaging the lock.")

When used as the output executor for a state machine, the methods of an instance of this class will be called according to the names of the outputs that are produced.
That is, when a transition is executed which has :py:obj:`Output.ENGAGE_LOCK` as an output, :py:meth:`output_ENGAGE_LOCK` will be called.
This lets the application define arbitrary side-effects to associate with outputs.
In this well-defined way the otherwise rigid, structured, explicit state machine can interact with the messy world.


Construction
------------

Having defined these things it is possible to use :py:func:`constructFiniteStateMachine` to construct the finite state machine.

.. code-block:: python

   from machinist import constructFiniteStateMachine

   turnstile = constructFiniteStateMachine(
       inputs=Input,
       outputs=Output,
       states=State,
       table=table,
       initial=State.LOCKED,
       richInputs={},
       inputContext={},
       world=Outputer(),
   )


Apart from the inputs, outputs, states, transition table, and output executor, the only other argument to pay attention to in this call right now is *initial*.
This defines the state that the state machine is in immediately after :py:func:`constructFiniteStateMachine` returns.


Receiving Inputs
----------------

Having created a state machine it is now possible to deliver inputs to it.
The simplest way to do this is to pass input symbols to the :py:attr:`receive` method:

.. code-block:: python

   turnstile.receive(TurnstileInput.FARE_PAID)
   turnstile.receive(TurnstileInput.ARM_UNLOCKED)
   turnstile.receive(TurnstileInput.ARM_TURNED)
   turnstile.receive(TurnstileInput.ARM_LOCKED)
