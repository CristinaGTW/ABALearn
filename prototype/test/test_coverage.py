from prolog.coverage import covered, get_covered_solutions
from elements.components import Atom, Example
from prolog.config import set_up_abalearn

def test_covers():
    prolog = set_up_abalearn("prototype/resources/flies_example.pl")
    
    result = covered(prolog,[Example("e1",Atom.parse_atom("bird(a)")), Example("e2", Atom.parse_atom("bird(f)"))])

    assert result == True


def test_not_covers():
    prolog = set_up_abalearn("prototype/resources/flies_example.pl")

    result = covered(prolog,[Example("p1",Atom.parse_atom("flies(a)")), Example("p2", Atom.parse_atom("flies(b)"))])

    assert result == False

def test_get_covered_solutions():
    prolog = set_up_abalearn("prototype/resources/flies_example.pl")

    result = get_covered_solutions(prolog, Atom("bird",["X"]))

    assert result == [{"X":"e"},{"X":"f"},{"X":"c"},{"X":"d"},{"X":"a"},{"X":"b"}]