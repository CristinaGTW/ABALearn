from coverage.cover_utils import covered, get_covered_solutions
from elements.components import Atom, Example
from pyswip import Prolog

def test_covers():
    prolog = Prolog()
    prolog.consult("prototype/resources/coverage.pl")
    prolog.consult("prototype/resources/flies_example.pl")
    
    result = covered(prolog,[Example("p1",Atom.parse_atom("flies(a)")), Example("p2", Atom.parse_atom("flies(b)"))])

    assert result == True


def test_not_covers():
    prolog = Prolog()
    prolog.consult("prototype/resources/coverage.pl")
    prolog.consult("prototype/resources/flies_example.pl")

    result = covered(prolog,[Example("n1",Atom.parse_atom("flies(c)")), Example("n2", Atom.parse_atom("flies(d)"))])

    assert result == False

def test_get_covered_solutions():
    prolog = Prolog()
    prolog.consult("prototype/resources/coverage.pl")
    prolog.consult("prototype/resources/flies_example.pl")

    result = get_covered_solutions(prolog, Atom("flies",["X"]))

    assert set(result) == set([("e",),("f",),("a",),("b",)])