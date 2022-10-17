from votepy.testing.structure.structure import rule, impl, algo, implementations, get_implementation

import pytest

from abc import ABC, abstractmethod


class MockBaseAlgorithm(ABC):
    def __init__(self):
        self.__prepared = False

    @abstractmethod
    def _solve(self, x: int, y: int) -> int:
        pass

    def solve(self, x: int, y: int) -> int:
        return self._solve(x, y)

    def prepare(self):
        self.__prepared = True


@algo(name="slow")
class Slow(MockBaseAlgorithm):
    def __init__(self, max_iterations: int) -> None:
        super().__init__()
        self.max_iterations = max_iterations

    def _solve(self, x: int, y: int):
        res = 0
        for _ in range(max(x, self.max_iterations)):
            res += 1
        for _ in range(max(y, self.max_iterations)):
            res += 1
        return res


@algo(name="fast")
class Fast(MockBaseAlgorithm):
    def _solve(self, x: int, y: int) -> int:
        print(self.prompt)
        return x + y

    def prepare(self, custom_prompt: str) -> None:
        self.prompt = custom_prompt
        super().prepare()


@rule()
def add(x: int, y: int, algorithm: MockBaseAlgorithm = Fast()) -> int:
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
