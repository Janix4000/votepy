# Votepy
![Tests](https://github.com/Janix4000/votepy/actions/workflows/tests.yml/badge.svg)

Votepy provides ready-to-use tools to calculate multi-winning ordinal elections, under different voting rules.

## Installation 

 1. Clone the repository: `git clone https://github.com/Janix4000/votepy.git path/to/lib`
 2. Create and source new virtual environment: `cd path/to/your/project && python3 -m venv venv && source venv/bin/activate`
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
    [3, 0, 2, 1]  # third voter's preference
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
    [3, 0, 2, 1]  # third voter's preference
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
# this is equivalent of calling vp.rules.bloc
committee = vp.solve('bloc', voting, committee_size)
```

### Voting-solving algorithms
Some of the voting rules are extremely costly to compute and finding the best committee may be very time-consuming for a greater number of candidates and voters. Luckily, many voting rules are defined by the maximization of some objective function (`scoring function`), so the best committees can be approximated using different tricks and methods. 

Let's look at the `chamberlin_courant` (shortly `cc`) rule, which turns out to be NP-Complete, and so no efficient algorithm is known for finding the best committees for the given election. For such a rules additional parameter `algorithm` must be provided. Algorithms can be specified by their name:

```py
committee = vp.rules.chamberlin_courant(
    voting, 
    committee_size, 
    algorithm='brute_force'
)
```

or by using their corresponding algorithms objects:

```py
from votepy.algorithms import BruteForce

# this is equivalent of 'brute_force' string name
committee = vp.rules.chamberlin_courant(
    voting, 
    committee_size, 
    algorithm=BruteForce()
) 
```

In this case, the `brute force` algorithm will check every possible combination of the candidates and take the best one to create committee.

Some algorithms can accept additional parameters, and it is only possible by using their corresponding classes:

```py
# numeric algorithm, similar to simulated annealing, giving approximate results
from votepy.algorithms import BasinHopping  

committee = vp.rules.chamberlin_courant(
    voting, 
    committee_size, 
    algorithm=BasinHopping(niter=100, seed=1)
)
```

There are better methods than brute force for getting exact solutions. We can check all algorithms implemented for the cc rule:

```py
# prints rule_name->algorithm_class dictionary
print(vp.get_algorithms('chamberlin_courant'))
```

One of the most common technice used for solving NP-Complete problems is using `ILP` solvers. However, in contrast to the brute force algorithm, we need to specify solver engine during the initialization of the ILP.
```py
from votepy.algorithms import ILP
# Gurobi solver must be previously installed and activated on the machine
from votepy.generic_ilp import Gurobi 

committee = vp.rules.chamberlin_courant(
    voting, 
    committee_size, 
    algorithm=ILP(Gurobi)
)
```


## Contribution guide

### Installation

 1. Clone the repository: `git clone https://github.com/Janix4000/votepy.git && cd votepy`
 2. Create and source new virtual environment: `python3 -m venv venv && source venv/bin/activate`
 3. Install the main package: `pip3 install -e .`
 4. Install development packages: `pip3 install -r ./requirements_dev.txt`
 5. Run tests: `pytest`

### Adding a new voting rule
See the [guide](votepy/rules/README.md) for adding new voting rule.
