from elements.aba_framework import ABAFramework
from elements.components import Rule, Atom, Example
from asp_coverage.ASPforABA_cov import covered


def test_get_all_instantiations_and_consts():
    rule_1 = Rule.parse_rule("r1:p(A,B)<-q(A,C),r(C,B),A=B,C=3")
    rule_2 = Rule.parse_rule("r2:p(A,B)<-A=1,B=2")
    rule_3 = Rule.parse_rule("r3:p(A,B)<-A=3")
    background_knowledge = [rule_1, rule_2, rule_3]
    aba_framework = ABAFramework(
        background_knowledge, [], [], [], [], {}, {}, {})
    (asp,_) = aba_framework.get_all_instantiations_and_consts()
    asp.sort()
    assert asp == [['p(1,1)', 'q(1,3)', 'r(3,1)'], ['p(1,2)'], ['p(2,2)', 'q(2,3)', 'r(3,2)'], [
        'p(3,1)'], ['p(3,2)'], ['p(3,3)'], ['p(3,3)', 'q(3,3)', 'r(3,3)']]


def test_get_all_groundings():
    aba_framework = ABAFramework([], [], [], [], [], {}, {}, {})
    atom = [Atom("p", ["A", "2"])]
    result = []
    aba_framework._get_all_groundings(
        atom, 0, 0,{}, {0:[]},["1", "2", "3"], result)
    assert result == [['p(1,2)'], ['p(2,2)'], ['p(3,2)']]

def test_asp_file():
    rule_1 = Rule.parse_rule("r1:p(A,B)<-q(A,C),r(C,B),A=B,C=3")
    rule_2 = Rule.parse_rule("r2:p(A,B)<-A=1,B=2")
    rule_3 = Rule.parse_rule("r3:p(A,B)<-A=3")
    a_1 = Atom.parse_atom("alpha(A)")
    c_a_1 = Atom.parse_atom("c_alpha(A)")
    background_knowledge = [rule_1, rule_2, rule_3]
    aba_framework = ABAFramework(
        background_knowledge, [], [], [a_1], [(a_1,c_a_1)], {}, {}, {})
    aba_framework.to_asp("test_asp.pl")
    assert 'p aba 18\nr 7 13 16\nr 8\nr 9 14 17\nr 10\nr 11\nr 12\nr 12 15 18\na 1\na 2\na 3\nc 1 4\nc 2 5\nc 3 6\n' == open("test_asp.pl").read()

def test_aspforaba_covered():
    rule_1 = Rule.parse_rule("r1:p(A,B)<-q(A,C),r(C,B),A=B,C=3")
    rule_2 = Rule.parse_rule("r2:p(A,B)<-A=1,B=2")
    rule_3 = Rule.parse_rule("r3:p(A,B)<-A=3")
    background_knowledge = [rule_1, rule_2, rule_3]
    aba_framework = ABAFramework(
        background_knowledge, [], [], [], [], {}, {}, {})
    ex = Example("e", Atom.parse_atom("p(1,2)"))
    breakpoint()
    assert covered(aba_framework, ex)