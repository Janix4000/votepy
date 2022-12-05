# Implementing new voting rules

Voting rules are simple python functions that take a description of the voting (`voting` and `committee size`) and return chosen `committee`.

## Simple Rules

There is an example of the implementation of the `bloc` rule:

```py
# my_bloc.py
def my_bloc(voting: list[list[int]], committee_size: int) -> list[int]:
    n = len(voting[0])

    candidates_scores = [0] * n
    for vote in voting:
        for candidate in vote[:committee_size]:
            candidates_scores[candidate] += 1

    sorted_indices_by_score, _sorted_scores = zip(
        *sorted(enumerate(candidates_scores), reverse=True, key=lambda idx_score: idx_score[1]))
    
    committee = sorted_indices_by_score[:committee_size]
    return committee
```

Votepy tries to automatically synchronize and configure all its components. To keep everything in sync, voting rules must be decorated with the `@votepy.meta.structure.rule()` decorator:

```py
# my_bloc.py
from votepy.meta.structure import rule


@rule()
def my_bloc(voting: list[list[int]], committee_size: int) -> list[int]:
    ...
    return committee
```



At this moment, if we include a python file with the `my_bloc` function, it will be listed by the `votepy.get_rules()` function:

```py
# main.py
import my_bloc
import votepy as vp

# you can search for your rule using a string with the function name
print('my_bloc' in vp.get_rules())  # True
```

If you want to use different identification (string) name for your rule, simply use the `name=` parameter:

```py
# my_bloc.py
@rule(name='own_bloc')
def my_bloc(voting: list[list[int]], committee_size: int) -> list[int]:
    ...
    return committee

...

print('own_bloc' in vp.get_rules())  # True
```

However, `@rule()` is only a declaration of the voting rule. 

An attempt to use `votepy.solve` will end up with the following error:

```py
>>> import votepy as vp
>>> import my_bloc
>>> voting = [
...   [0, 1, 2, 3],
...   [3, 2, 1, 0],
...   [2, 1, 3, 0]
... ]
>>> vp.solve('my_bloc', voting, 2)
ValueError: my_bloc has no default implementation. If a rule does not need any algorithm, its rule function should be additionally decorated with `@impl(rule='name', algorithm=None)`. See `@impl` docs.
```

In many cases, voting rules are NP-Hard and a user may want to use different techniques to find exact solutions or only approximations. For such scenarios, votepy needs to know what type of `algorithm` should use to solve a given rule. In our case, we can calculate `bloc` results directly, and to do so we need to tag the `my_bloc` function with an additional `votepy.meta.structure.impl` decorator:

```py
# my_bloc.py
from votepy.meta.structure import rule
from votepy.meta.structure import impl


@impl('my_bloc', algorithm=None)
@rule()
def my_bloc(voting: list[list[int]], committee_size: int) -> list[int]:
    ...
    return committee
```

First of all, we pass the `name` of the rule. It is a bit redundant, but Python requires this step. Next, we specify the algorithm used in this implementation. In our case, we do not need any algorithm, so we just pass the `None` argument.

Now we can use the `my_bloc` rule in the `votepy.solve` function.

## Implementation using algorithms

As mentioned earlier, some rules are NP-Hard, and finding exact solutions may be impossible (or at least very time-consuming). In such cases, we can use approximation algorithms. 

For example, let's use the `greedy` algorithm to find the `chamberlin-courant` solution. First of all, we need to declare the `cc` rule, without default implementation:

```py
# own_cc.py
from votepy.meta.structure import rule
from votepy.solve import solve
from votepy.algorithms import BaseAlgorithm

@rule()
def my_cc(voting: list[list[int]], committee_size: int, algorithm: BaseAlgorithm) -> list[int]:
    return solve(my_cc, voting, committee_size, algorithm=algorithm)
```

Note, that in the main rule function we don't implement any specific rule logic. It can be treated as a header of the function and can contain all necessary documentation and type hints. However, this function should return the committee chosen by the provided algorithm (which is an obligatory argument). To do so, we use the `solve()` function, which automatically finds the proper implementation for us, which we create in the next section:


```py
# own_cc.py
from votepy.algorithms import Greedy
from votepy.meta.structure import impl
from votepy.ordinal_election import OrdinalElection

...

@impl(my_cc, algorithm=Greedy)
def __my_cc_greedy(voting: OrdinalElection, committee_size: int, algorithm: Greedy) -> list[int]:

    def greedy_scoring_function(current_committee: list[int], voting: OrdinalElection, candidate: int) -> float:
        candidate_committee = set(current_committee) | {candidate}
        return __cc_scoring_function(candidate_committee, voting)

    algorithm.prepare(greedy_scoring_function)
    return algorithm.solve(voting, committee_size)

def __cc_scoring_function(committee: list[int], voting: OrdinalElection) -> float:
    committee = set(committee)
    score = 0
    m = voting.ballot_size
    for voter in voting:
        score += max(m - voter.pos(candidate) for candidate in committee)
    return score
```
First of all, we create a new private function (it is by `__` prefix) `__my_cc_greedy()` and decorate it with the `@impl(rule, algorithm)` decorator. Note that this function won't be part of public API and it will be only called by the `solve()` function. 
Then, we need to prepare an algorithm for our specific voting rule. All algorithms are universal across all voting rules and they need to be adapted to solve specific ones. Additionally, algorithms can be passed as already initialized Python objects, with custom parameters set by users. To do so, we need to use the `algorithm.prepare()` function and pass custom parameters (very often scoring function of the rule). A greedy algorithm accepts the function of the form `(previous committee, voting, candidate) -> score with the candidate`. In this example, we construct it using the original scoring function of the `cc` rule.

In another example, we adapt the `brute force` algorithm to the `cc` rule:

```py
from votepy.algorithms import BruteForce

@impl(my_cc, algorithm=BruteForce)
def __my_cc_brute_force(voting: OrdinalElection, committee_size: int, algorithm: BruteForce) -> list[int]:
    algorithm.prepare(__cc_scoring_function)
    return algorithm.solve(voting, committee_size)
```

The brute force needs only the scoring function of the form `(current committee, voting) -> score of the committee` to be prepared, so we could use `__cc_scoring_function`.