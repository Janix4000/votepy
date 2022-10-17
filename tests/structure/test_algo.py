from re import A
from votepy.testing.structure.structure import algo, algorithms


@algo(name="name")
class A:
    def __init__(self):
        pass


def test_algo():
    test = A()
    assert test.name == "name"
    assert A.name == "name"


def test_algo_as_param(test=A()):
    assert test.name == "name"


def test_algo_as_param_with_hint(test: A = A()):
    assert test.name == "name"


def test_algo_registered():
    assert "name" in algorithms
    assert algorithms["name"] == A
