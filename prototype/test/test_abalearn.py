from transformations.learn_utils import set_up_abalearn, add_rule, get_rules, get_positive_examples
from elements.components import Rule, Atom, Example

def test_get_rules():
    prolog = set_up_abalearn("prototype/resources/input.pl")
    rules = get_rules(prolog)

    assert len(rules) == 8
    assert rules[0] == Rule("r1", Atom("bird",["$VAR(0)"]), [Atom("penguin",["$VAR(0)"])])

def test_get_positive_examples():
    prolog = set_up_abalearn("prototype/resources/input.pl")
    pos_exs = get_positive_examples(prolog)

    assert len(pos_exs) == 4
    assert pos_exs[0] == Example("p1",Atom("flies",["a"]))