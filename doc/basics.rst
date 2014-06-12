.. _Basic Usage:

Basic Usage
===========

State machines are constructed using :py:func:`machinist.constructFiniteStateMachine`.

Inputs, Outputs, States
-----------------------

Before a machine can be constructed its inputs, outputs, and states must be defined.
These are all defined using :py:mod:`twisted.python.constants`.

.. literalinclude:: turnstile.py
   :start-after: begin setup
   :end-before: end setup

Transitions
-----------

Also required is a transition table.
The transition table is defined using :py:class:`machinist.TransitionTable`.
:py:class:`TransitionTable` instances are immutable and have several methods for creating new tables including more transitions.

.. literalinclude:: turnstile.py
   :start-after: begin table def
   :end-before: end table def

First, define how the ``FARE_PAID`` input is handled in the ``LOCKED`` state: output ``DISENGAGE_LOCK`` and change the state to the ``ACTIVE``.

.. literalinclude:: turnstile.py
   :start-after: begin first transition
   :end-before: end first transition

Next, define how the ``ARM_TURNED`` input is handled in the ``UNLOCKED`` state: output ``ENGAGE_LOCK`` and  change the state to ``ACTIVE``.

.. literalinclude:: turnstile.py
   :start-after: begin second transition
   :end-before: end second transition

Last, define two transitions at once for getting out of the ``ACTIVE`` state.
``addTransitions`` is a convenient way to define more than one transition at once.
It is equivalent to several ``addTransition`` calls.

.. literalinclude:: turnstile.py
   :start-after: begin last transitions
   :end-before: end last transitions

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

.. literalinclude:: turnstile.py
   :start-after: begin outputer
   :end-before: end outputer

When used as the output executor for a state machine, the methods of this instance will be called according to the names of the outputs that are produced.
That is, when a transition is executed which has :py:obj:`Output.ENGAGE_LOCK` as an output, :py:meth:`output_ENGAGE_LOCK` will be called.
This lets the application define arbitrary side-effects to associate with outputs.
In this well-defined way the otherwise rigid, structured, explicit state machine can interact with the messy world.


Construction
------------

Having defined these things, we can now use :py:func:`constructFiniteStateMachine` to construct the finite state machine.

.. literalinclude:: turnstile.py
   :start-after: begin construct
   :end-before: end construct

Apart from the inputs, outputs, states, transition table, and output executor, the only other argument to pay attention to in this call right now is *initial*.
This defines the state that the state machine is in immediately after :py:func:`constructFiniteStateMachine` returns.


Receiving Inputs
----------------

Having created a state machine, we can now deliver inputs to it.
The simplest way to do this is to pass input symbols to the :py:attr:`receive` method:

.. literalinclude:: turnstile.py
   :start-after: begin inputs
   :end-before: end inputs

If we combine all of these snippets and call :py:func:`cycle` the result is a program that produces this result:

.. testsetup:: turnstile

   import turnstile

.. testcode:: turnstile
   :hide:

   turnstile.cycle()

.. testoutput:: turnstile

   Disengaging the lock.
   Engaging the lock.

.. testcode:: turnstile-main
   :hide:

   execfile("turnstile.py", {"__name__": "__main__"})

.. testoutput:: turnstile-main
   :hide:

   Disengaging the lock.
   Engaging the lock.

