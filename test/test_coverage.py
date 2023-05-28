from coverage.engine import covered, get_cov_solutions
from elements.components import Atom, Example
from pyswip import Prolog
from prolog.config import set_up_abalearn, reset
from prolog.info import set_up_aba_framework

def test_covers():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    prolog = set_up_abalearn("test_resources/flies_example.pl")
    aba_framework = set_up_aba_framework(prolog)
    result_1 = covered(
        aba_framework,Atom.parse_atom("bird(a)"))
    result_2 = covered(aba_framework, Atom.parse_atom("bird(f)"))
    assert result_1 == True
    assert result_2 == True


def test_not_covers():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    prolog = set_up_abalearn("test_resources/flies_example.pl")
    aba_framework = set_up_aba_framework(prolog)
    result_1 = covered(aba_framework,Atom.parse_atom("flies(a)"))
    result_2 = covered(aba_framework,Atom.parse_atom("flies(b)"))
    assert result_1 == False
    assert result_2 == False


def test_get_covered_solutions():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    prolog = set_up_abalearn("test_resources/flies_example.pl")
    aba_framework = set_up_aba_framework(prolog)

    result = get_cov_solutions(aba_framework, Atom("bird", ["X"]))

    assert result == [
        {"X": "e"},
        {"X": "f"},
        {"X": "c"},
        {"X": "d"},
        {"X": "a"},
        {"X": "b"},
    ]
