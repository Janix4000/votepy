from votepy.meta.structure import rule, impl


@rule()
def rule_without_implementation(voting, committee_size):
    return []


@impl('rule_without_algorithm', algorithm=None)
@rule()
def rule_without_algorithm(voting, committee_size):
    return []
