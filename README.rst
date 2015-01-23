.. image:: https://travis-ci.org/ClusterHQ/machinist.png
  :target: https://travis-ci.org/ClusterHQ/machinist

.. image:: https://coveralls.io/repos/ClusterHQ/machinist/badge.png
  :target: https://coveralls.io/r/ClusterHQ/machinist


Installation
~~~~~~~~~~~~

.. code-block:: console

  $ pip install machinist

Machinist's automatic structured logging depends on `eliot <https://github.com/ClusterHQ/eliot>`_.
Logging is declared as a Machinist extra so you can automatically install this dependency:

.. code-block:: console

  $ pip install machinist[logging]


Defining Inputs, Outputs, and States
------------------------------------

Inputs, outputs, and states are all ``twisted.python.constants.NamedConstant``.
Collections of inputs, outputs, and states are ``twisted.python.constants.Names``.

.. code-block:: python

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


Defining the Transitions
------------------------

A transition is defined as an input to a state mapped to a series of outputs and the next state.

These transitions are added to a transition table.

.. code-block:: python

  table = TransitionTable()

  # Any number of things like this
  table = table.addTransitions(
      TurnstileState.UNLOCKED, {
          TurnstileInput.ARM_TURNED:
              ([TurnstileOutput.ENGAGE_LOCK], TurnstileState.ACTIVE),
      })

If an input is received for a particular state for which it is not defined, an ``machinist.IllegalInput`` would be raised.
In the example above, if ``FARE_PAID`` is received as an input while the turnstile is in the ``UNLOCKED`` state, ``machinist.IllegalInput`` will be raised.


Putting together the Finite State Machine
-----------------------------------------

To build an instance of a finite state machine from the transition, pass the inputs, outputs, states, and table (previously defined) to the function ``machinist.constructFiniteStateMachine``.

.. code-block:: python

  turnstileFSM = constructFiniteStateMachine(
      inputs=TurnstileInput,
      outputs=TurnstileOutput,
      states=TurnstileState,
      table=table,
      initial=TurnstileState.LOCKED,
      richInputs=[]
      inputContext={},
      world=MethodSuffixOutputer(Turnstile(hardware)),
  )

Note that ``richInputs`` must be passed and it must be a list of ``IRichInput`` providers mapped to the same input symbols (parameter ``inputs``) the FSM is created with.

``Turnstile`` is a class with methods named ``output_XXX``, where ``XXX`` is one of the outputs.
There should be one such method for each output defined.


Transitioning the Finite State Machine
--------------------------------------

To provide an input to the FSM, ``receive`` on the FSM must be called with an instance of an ``IRichInput`` provider.

.. code-block:: python

  turnstileFSM.receive(TurnstileInput.FARE_PAID)


Further Reading
---------------

For the rest of the example code, see `doc/turnstile.py <https://github.com/ClusterHQ/machinist/blob/master/doc/turnstile.py>`_.

For more discussion of the benefits of using finite state machines, see:

 * https://www.hybridcluster.com/blog/what-is-a-state-machine/
 * https://www.hybridcluster.com/blog/benefits-state-machine/
 * https://www.hybridcluster.com/blog/unit-testing-state-machines/
 * https://www.hybridcluster.com/blog/isolating-side-effects-state-machines/
