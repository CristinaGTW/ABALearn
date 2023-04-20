from prolog.settings import add_rule, rem_rule
from prolog.config import set_up_abalearn
from prolog.info import get_rules, get_positive_examples
from prolog.transformation_rules import foldable
from elements.components import Rule, Atom, Example


def test_get_rules():
    prolog = set_up_abalearn("prototype/test_resources/flies_example.pl")
    rules = get_rules(prolog)

    assert len(rules) == 8
    assert rules[0] == Rule("r1", Atom("bird", ["A"]), [Atom("penguin", ["A"])])


def test_get_positive_examples():
    prolog = set_up_abalearn("prototype/test_resources/flies_example.pl")
    pos_exs = get_positive_examples(prolog)

    assert len(pos_exs) == 4
    assert pos_exs[0] == Example("p1", Atom("flies", ["a"]))


def test_prolog_can_be_modified():
    prolog = set_up_abalearn("prototype/test_resources/flies_example.pl")
    list(prolog.query("assert(my_rule(r9,bird(s),[has_wings(s)]))."))
    rules = get_rules(prolog)
    assert len(rules) == 9
    rem_rule(prolog, "r9")
    rules = get_rules(prolog)
    assert len(rules) == 8
    list(prolog.query("assert(my_rule(r9,bird(s),[has_wings(s)]))."))
    rules = get_rules(prolog)
    assert len(rules) == 9

def test_foldable():
    prolog = set_up_abalearn("")
    list(prolog.query("assertz(my_rule(r1,free(A,B),[A=4,B=6]))."))
    list(prolog.query("assertz(my_rule(r2,busy(A),[A=6]))."))
    assert foldable(prolog,"r1","r2")
    assert foldable(prolog,"r2","r1")

def test_not_foldable():
    prolog = set_up_abalearn("")
    list(prolog.query("assertz(my_rule(r1,busy(A),[A=4]))."))
    list(prolog.query("assertz(my_rule(r2,busy(A),[A=6]))."))
    assert not foldable(prolog,"r1","r2")
    assert not foldable(prolog,"r2","r1")