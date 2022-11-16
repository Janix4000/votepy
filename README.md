# Votepy
![Tests](https://github.com/Janix4000/votepy/actions/workflows/tests.yml/badge.svg)

Votepy provides ready-to-use tools to calculate multi-winning ordinal elections, under different voting rules.

## Installation 

 1. Clone the repository: `git clone URL path/to/lib`
 2. Create and source new virtual environment: `cd path/to/lib && python3 -m venv venv && source venv/bin/activate`
 3. Install the main package: `pip3 install -e path/to/lib/votepy`

## Usage

### Ordered preference and election

When working with the ordered elections, we need to represent such data. Given `n` candidates, we can represent voter's preference by permutation of length `n`, using a standard Python list:
```py
n = 4
voting_preference = [2, 1, 3, 0]
```

We will call such a preference a `voting ballot`.
Having `m` voters, we can group their preferences into the `ordered election`:

```py
n = 4
m = 3

voting = [
    [2, 1, 3, 0], # first voter's preference
    [1, 2, 3, 0], # second voter's preference
    [3, 0, 3, 1]  # third voter's preference
]
```

Votepy also provides special data types for them, but they are not obligatory and all functions support python's primitives.
However, they give additional functionalities, such as mapping candidates to more human-readable representations:

```py
from votepy.ordinal_election import OrdinalElection, OrdinalBallot

mapping = {0: 'Joe', 1: 'John', 2: 'Sue', 3: 'Anna'}

single_voting_preference = OrdinalBallot([2, 1, 3, 0], mapping=mapping)

voting = OrdinalElection([
    [2, 1, 3, 0], # first voter's preference
    [1, 2, 3, 0], # second voter's preference
    [3, 0, 3, 1]  # third voter's preference
], mapping=mapping)

print(voting) # prints election using mapping representation

```

### Voting rules

For a given election, we want to choose a set of representatives, with the predefined number `k` (or `committee size`) of the delegates.
However, there are many strategies to choose such a `committee`. These strategies are commonly called `voting rules` and may optimize different objectives. We can print all of the implemented voting rules, with the corresponding python functions:

```py
import votepy as vp

print(vp.get_rules()) # prints rule_name->rule_function dictionary
```

Let's use for an example `bloc` rule on the previously defined election:

```py
committee_size = 2
committee = vp.rules.bloc(voting, committee_size)
print(committee)
```

Votepy gives additional way to call the voting rules:

```py 
committee = vp.solve('bloc', voting, committee_size) # this is equivalent of calling vp.rules.bloc
```

### Voting-solving algorithms
Some of the voting rules are extremely costly to compute and finding the best committee may be very time-consuming for a greater number of candidates and voters. Luckily, many voting rules are defined by the maximization of some objective function (`scoring function`), so the best committees can be approximated using different tricks and methods. 

Let's look at the `chamberlin_courant` (shortly `cc`) rule, which turns out to be NP-Complete, and so no efficient algorithm is known for finding the best committees for the given election. For such a rules additional parameter `algorithm` must be provided:

```py
committee = vp.rules.chamberlin_courant(voting, committee_size, algorithm='brute_force')
```

In this case, the `brute force` algorithm will check every possible combination of the candidates and take the best one to create committee. There are of course better methods for getting exact solutions. We can check all algorithms implemented for the cc rule:

```py
print(vp.get_algorithms('chamberlin_courant')) # prints rule_name->algorithm_class dictionary
```

One of the most common technice used for solving NP-Complete problems is using `ILP` solvers. However, in contrast to the brute force algorithm, we need to specify solver engine during the initialization of the ILP. Fortunately, all votepy's functions accepts also constructed objects as algorithm parameter:
```py
from votepy.algorithms import ILP
from votepy.generic_ilp import Gurobi # Gurobi solver must be previously installed on the machine

committee = vp.rules.chamberlin_courant(voting, committee_size, algorithm=ILP(Gurobi))
```


## Contribution guide

 1. Clone the repository: `git clone URL && cd votepy`
 2. Create and source new virtual environment: `python3 -m venv venv && source venv/bin/activate`
 3. Install the main package: `pip3 install -e .`
 4. Install development packages: `pip3 install -r ./requirements_dev.txt`
 5. Run tests: `pytest`
