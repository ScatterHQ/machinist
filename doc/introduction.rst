The State Machine Construction Toolkit
======================================

Machinist's aim is to make it easy to structure your code as an explicit state machine.

State machines are defined by supplying Machinist with four things:

  1. A set of states.
  2. A set of inputs.
  3. A set of outputs.
  4. A set of transitions.

State machines are represented by an object with a ``receive`` method which accepts an input object.
The input object is either an object from the set of inputs or an object related to one of those objects in a certain way (more on that later).
When an input is received by the state machine, its state is updated and outputs are generated according to the defined transitions.

If this sounds great to you then you might want to jump ahead to the :ref:`Basic Usage` documentation.
Otherwise, read on.


Benefits of Explicit State Machines
===================================

All software is an implementation of a state machine.
The memory associated with a running program represents its current state.
The executable code defines what transitions are possible.
Myriad inputs and outputs exist in the form of:

  * data read from file descriptors.
  * signals or GUI events such as button clicks.
  * data which is rendered onto displays.
  * sound which is created by speakers.

The difference between an explicit state machine and software written without a state machine (let's call this *implicit state machine* software or *ism* software) mostly comes down to what it is easy to learn about the state machine being represented.


States
------

In the explicit state machine all of the states have been enumerated and can be learned at a glance.
In :abbr:`ism (implicit state machine)` software it is impractical to enumerate the states: imagine a program with just one piece of memory, a 16 bit integer.
There are 2\ :superscript:`16` (65536) states in this program.
Without reading all the program that manipulates this state it's impossible to know which of them are important or how they might interact.
Extend your imagination to any real piece of software which might operate on dozens, hundreds, or thousands of megabytes of memory.
Consider the number of states this amount of memory implies.
It's not just difficult to make sense of this collection of states, it is practically impossible.

Contrast this with an explicit state machine where each state is given a name and put in a list.
The explicit state machine version of that program with a 16 bit integer will make it obvious that only three of the values (states) it can take on are used.


Inputs and Outputs
------------------

In the explicit state machine all of the inputs and outputs are also completely enumerated.
In :abbr:`ism (implicit state machine)` software these are usually only defined by the implementation accepting or producing them.
This means there is just one way to determine what inputs are accepted and what outputs are produced:
read the implementation.
If you're lucky, someone will have done this already and produced some API documentation.
If you're doubly lucky, the implementation won't have changed since they did this.

Contrast this with an explicit state machine where the implementation is derived from the explicit list of inputs and outputs.
The implementation cannot diverge because it is a function of the declaration.


Transitions
-----------

Once again, transitions are completely enumerated in the definition of an explicit state machine.
A single transition specifies that when a specific input is received while the state machine is in a specific state a specific output is produced and the state machine changes to a specific new state.
A collection of transitions completely specifies how the state machine reacts to inputs and how its future behavior is changed by those inputs.
In :abbr:`ism (implicit state machine)` software it is conventional to define a constellation of flags to track the state of the program.
It is left up to the programmer to build and remember the cartesian product of these flags in their head.
There are also usually illegal flag combinations which the program is never *supposed* to encounter.
These are either left as traps to future programmers or the implementer must take the tedious steps of building guards against them arising.
All of this results in greater complexity to handle scenarios which are never even supposed to be encountered.

Contrast this with an explicit state machine where those flags are replaced by the state of the state machine.
The valid states are completely enumerated and there is no need to look at a handful of flags to determine how the program will behave.
Instead of adding complexity to handle impossible cases, those cases are excluded simply by *not* defining an explicit state to represent them.

