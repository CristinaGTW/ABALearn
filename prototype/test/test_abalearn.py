from transformations.learn_utils import set_up_abalearn, add_rule, get_rules
from elements.components import Rule, Atom

def test_get_rules():
    prolog = set_up_abalearn("prototype/resources/input.pl")
    rules = get_rules(prolog)

    assert len(rules) == 8
    assert rules[0] == Rule("r1", Atom("bird",["$VAR(0)"]), [Atom("penguin",["$VAR(0)"])])