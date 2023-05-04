from elements.aba_framework import ABAFramework
from elements.components import Rule, Atom, Example
from asp_coverage.ASPforABA_cov import covered
from prolog.config import set_up_abalearn
from prolog.info import get_current_aba_framework


def test_get_all_instantiations_and_consts():
    rule_1 = Rule.parse_rule("r1:p(A,B)<-q(A,C),r(C,B),A=B,C=3")
    rule_2 = Rule.parse_rule("r2:p(A,B)<-A=1,B=2")
    rule_3 = Rule.parse_rule("r3:p(A,B)<-A=3")
    background_knowledge = [rule_1, rule_2, rule_3]
    aba_framework = ABAFramework(
        background_knowledge, [], [], [], [], {}, {}, {})
    (asp, _) = aba_framework.get_all_instantiations_and_consts()
    asp.sort()
    assert asp == [['p(1,1)', 'q(1,3)', 'r(3,1)'], ['p(1,2)'], ['p(2,2)', 'q(2,3)', 'r(3,2)'], [
        'p(3,1)'], ['p(3,2)'], ['p(3,3)'], ['p(3,3)', 'q(3,3)', 'r(3,3)']]


def test_get_all_groundings():
    aba_framework = ABAFramework([], [], [], [], [], {}, {}, {})
    atom = [Atom("p", ["A", "2"])]
    result = []
    aba_framework._get_all_groundings(
        atom, 0, 0, {}, {0: []}, ["1", "2", "3"], result)
    assert result == [['p(1,2)'], ['p(2,2)'], ['p(3,2)']]


def test_aspforaba_covered():
    rule_1 = Rule.parse_rule("r1:p(A,B)<-q(A,C),r(C,B),A=B,C=3")
    rule_2 = Rule.parse_rule("r2:p(A,B)<-A=1,B=2")
    rule_3 = Rule.parse_rule("r3:p(A,B)<-A=3")
    background_knowledge = [rule_1, rule_2, rule_3]
    aba_framework = ABAFramework(
        background_knowledge, [], [], [], [], {}, {}, {})
    ex = Example("e", Atom.parse_atom("p(1,2)"))
    assert covered(aba_framework, [ex])


def test_asp_obj():
    prolog = set_up_abalearn("test_resources/asp_obj_test.pl")
    aba_framework = get_current_aba_framework(prolog, None)
    asp_obj = aba_framework.to_asp()
    assert asp_obj.rules == [(1, []), (2, []), (3, [9]), (3, [10]), (3, [11]), (3, [12]), (3, [13]), (3, [14]), (3, [15]), (3, [21]), (3, [27]), (3, [33]), (3, [39]), (4, [10]), (4, [15]), (4, [16]), (4, [17]), (4, [18]), (4, [19]), (4, [20]), (4, [22]), (4, [28]), (4, [34]), (4, [40]), (5, [11]), (5, [17]), (5, [21]), (5, [22]), (5, [23]), (5, [24]), (5, [25]), (5, [26]), (5, [29]), (5, [35]), (5, [41]), (6, [12]), (6, [
        18]), (6, [24]), (6, [27]), (6, [28]), (6, [29]), (6, [30]), (6, [31]), (6, [32]), (6, [36]), (6, [42]), (7, [13]), (7, [19]), (7, [25]), (7, [31]), (7, [33]), (7, [34]), (7, [35]), (7, [36]), (7, [37]), (7, [38]), (7, [43]), (8, [14]), (8, [20]), (8, [26]), (8, [32]), (8, [38]), (8, [39]), (8, [40]), (8, [41]), (8, [42]), (8, [43]), (8, [44]), (10, []), (11, []), (18, []), (19, []), (32, []), (34, [])]
