from votepy.testing.structure.structure import rule, impl, algo, implementations, get_implementation, get_algorithm
from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
from votepy.testing.solve import solve

import pytest


@algo(name="slow")
class Slow(BaseAlgorithm):
    def __init__(self, max_iterations: int) -> None:
        super().__init__()
        self.max_iterations = max_iterations

    def _solve(self, x: int, y: int):
        res = 0
        for _ in range(min(x, self.max_iterations)):
            res += 1
        for _ in range(min(y, self.max_iterations)):
            res += 1
        return res

    def solve(self, x: int, y: int) -> int:
        """# Summary
        This method should not be overridden. It is for testing purposes only.
        """
        return self._solve(x, y)


@algo(name="fast")
class Fast(BaseAlgorithm):
    def _solve(self, x: int, y: int) -> int:
        print(self.prompt)
        return x + y

    def prepare(self, custom_prompt: str) -> None:
        self.prompt = custom_prompt
        super().prepare()

    def solve(self, x: int, y: int) -> int:
        """# Summary
        This method should not be overridden. It is for testing purposes only.
        """
        return self._solve(x, y)


@rule()
def add(x: int, y: int, algorithm: BaseAlgorithm = Fast()) -> int:
    """# Summary
    Add two numbers

    ## Args:
        `x` (int): First number to add
        `y` (int): Second number to add

    ## Returns:
        -> int: Sum of two numbers

    ## Examples
    >>> add(1, 2)
    specific prompt for add_fast
    3
    """
    implementation = get_implementation(add, algorithm)
    algorithm = get_algorithm(algorithm)
    return implementation(x, y, algorithm)


@impl(add, Slow)
def add_slow(x, y, algorithm: Slow) -> int:
    return algorithm.solve(x, y)


@impl(add, Fast)
def add_fast(x, y, algorithm: Fast = Fast()) -> int:
    algorithm.prepare("specific prompt for add_fast")
    return algorithm.solve(x, y)


def test_implementations_registered():
    assert 'add' in implementations
    add_imps = implementations['add']
    assert 'slow' in add_imps
    assert 'fast' in add_imps


def test_get_existing_implementations():
    assert get_implementation(add, Slow)
    assert get_implementation(add, "slow")
    assert get_implementation("add", Slow)
    assert get_implementation("add", "slow")

    assert get_implementation(add, Fast)
    assert get_implementation(add, "fast")
    assert get_implementation("add", Fast)
    assert get_implementation("add", "fast")


def test_get_non_existing_implementations():
    with pytest.raises(ValueError):
        get_implementation("sub", Slow)

    with pytest.raises(ValueError):
        get_implementation(add, "int")


def test_main_function_invocation():
    assert add(1, 2, algorithm="fast") == 3
    assert add(1, 2, algorithm=Fast()) == 3

    slow = Slow(max_iterations=10)
    assert add(1, 2, algorithm=slow) == 3


def test_solve():
    assert solve(add, 1, 2, algorithm="fast") == 3
    assert solve(add, 1, 2, algorithm=Fast()) == 3

    assert solve("add", 1, 2, algorithm="fast") == 3
    assert solve("add", 1, 2, algorithm=Fast()) == 3

    slow = Slow(max_iterations=10)
    assert solve(add, 1, 2, algorithm=slow) == 3
    assert solve("add", 1, 2, algorithm=slow) == 3
