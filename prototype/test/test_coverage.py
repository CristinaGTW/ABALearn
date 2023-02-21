from coverage.cover_utils import covered
from elements.components import Atom, Example

def test_covers():
    result = covered("prototype/resources/flies_example.pl",[Example("p1",Atom.parse_atom("flies(a)")), Example("p2", Atom.parse_atom("flies(b)"))])

    assert result == True


def test_not_covers():
    result = covered("prototype/resources/flies_example.pl",[Example("n1",Atom.parse_atom("flies(c)")), Example("n2", Atom.parse_atom("flies(d)"))])

    assert result == False