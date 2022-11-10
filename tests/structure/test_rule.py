from votepy.meta.structure import rule, rules


@rule()
def auto_name_rule(x, y):
    """auto_name_rule"""
    return (x, y)


@rule(name="custom_name")
def custom_name_rule(x, y):
    """custom_name_rule"""
    return (x, y)


def test_auto_name_rule():
    assert "auto_name_rule" in rules
    assert rules["auto_name_rule"].__doc__ == """auto_name_rule"""
    assert rules["auto_name_rule"].__name__ == "auto_name_rule"


def test_custom_name_rule():
    assert "custom_name" in rules
    assert "custom_name_rule" not in rules
    assert rules["custom_name"].__doc__ == """custom_name_rule"""
    assert rules["custom_name"].__name__ == "custom_name_rule"
