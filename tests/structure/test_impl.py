from mock_integration import add, Slow, Fast

from votepy.testing.structure.structure import implementations, get_implementation

import pytest


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
