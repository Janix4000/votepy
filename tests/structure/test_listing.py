from mock_integration import add, Slow, Fast
from votepy.structure.structure import algo, BaseAlgorithm
from votepy.structure.listing import algorithms, rules


@algo(name="not_impl")
class NotImplemented(BaseAlgorithm):
    pass


def test_lists_all_algos():
    assert {"slow": Slow, "fast": Fast, "not_impl": NotImplemented}.items() <= algorithms().items()


def test_lists_rule_algos():
    assert algorithms(add) == {"slow": Slow, "fast": Fast}
    assert algorithms("add") == {"slow": Slow, "fast": Fast}


def test_lists_rules():
    assert {"add": add}.items() <= rules().items()
