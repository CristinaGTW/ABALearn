from transformations.learn_utils import set_up_abalearn, add_rule, get_rules
from elements.components import Rule, Atom

def test_add_rule():
    prolog = set_up_abalearn()
    rule = Rule("r_1", Atom("bird",["A"]), [Atom("penguin",["A"])])
    add_rule(prolog, rule)
    rules = get_rules(prolog)

    assert len(rules) == 1
    assert rules[0] == "r_1: bird(A) <- penguin(A)"