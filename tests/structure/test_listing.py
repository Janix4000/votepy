from mock_integration import add, Slow, Fast
from votepy.meta.structure import algo, BaseAlgorithm
from votepy.meta.listing import get_algorithms, get_rules


@algo(name="not_impl")
class NotImplemented(BaseAlgorithm):
    pass


def test_lists_all_algos():
    assert {"slow": Slow, "fast": Fast, "not_impl": NotImplemented}.items() <= get_algorithms().items()


def test_lists_rule_algos():
    assert get_algorithms(add) == {"slow": Slow, "fast": Fast}
    assert get_algorithms("add") == {"slow": Slow, "fast": Fast}


def test_lists_rules():
    assert {"add": add}.items() <= get_rules().items()
