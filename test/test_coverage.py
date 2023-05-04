from asp_coverage.ASPforABA_cov import covered, get_covered_solutions
from elements.components import Atom, Example
from prolog.config import set_up_abalearn
from prolog.info import get_current_aba_framework


def test_covers():
    prolog = set_up_abalearn("test_resources/flies_example.pl")
    aba_framework = get_current_aba_framework(prolog, None)
    breakpoint()
    result = covered(
        aba_framework,
        [
            Example("e1", Atom.parse_atom("bird(a)")),
            Example("e2", Atom.parse_atom("bird(f)")),
        ],
    )

    assert result == True


def test_not_covers():
    prolog = set_up_abalearn("test_resources/flies_example.pl")
    aba_framework = get_current_aba_framework(prolog, None)
    breakpoint()

    result = covered(
        aba_framework,
        [
            Example("p1", Atom.parse_atom("flies(a)")),
            Example("p2", Atom.parse_atom("flies(b)")),
        ],
    )

    assert result == False


def test_get_covered_solutions():
    prolog = set_up_abalearn("test_resources/flies_example.pl")
    aba_framework = get_current_aba_framework(prolog, None)
    breakpoint()

    result = get_covered_solutions(aba_framework, Atom("bird", ["X"]))

    assert result == [
        {"X": "a"},
        {"X": "b"},
        {"X": "c"},
        {"X": "d"},
        {"X": "e"},
        {"X": "f"},
    ]
