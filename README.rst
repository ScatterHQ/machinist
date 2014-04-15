
machinist - put together finite state machines
----------------------------------------------

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

  table = TransitionTable()

  # Any number of things like this
  table = table.addTransitions(
      TurnstileState.UNLOCKED, {
          TurnstileInput.ARM_TURNED:
              ([TurnstileOutput.ENGAGE_LOCK], TurnstileState.ACTIVE),
      })

  turnstileFSM = constructFiniteStateMachine(
      inputs=TurnstileInput,
      outputs=TurnstileOutput,
      states=TurnstileState,
      table=table,
      initial=TurnstileState.LOCKED,
      richInputs={},
      inputContext={},
      world=MethodSuffixOutputer(Turnstile(hardware)),
  )


For the rest of this example, see `doc/turnstile.py <https://github.com/hybridlogic/machinist/blob/master/doc/turnstile.py>`_.

For more discussion of the benefits of this style, see:

 * https://www.hybridcluster.com/blog/what-is-a-state-machine/
 * https://www.hybridcluster.com/blog/benefits-state-machine/
 * https://www.hybridcluster.com/blog/unit-testing-state-machines/

installation
~~~~~~~~~~~~

.. code-block:: console

  $ pip install machinist

contributing
~~~~~~~~~~~~

See http://github.com/hybridcluster/machinist for development.

.. image:: https://coveralls.io/repos/hybridlogic/machinist/badge.png
  :target: https://coveralls.io/r/hybridlogic/machinist
