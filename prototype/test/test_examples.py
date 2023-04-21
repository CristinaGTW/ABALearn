from pyswip import Prolog
from prolog.config import set_up_abalearn, reset
from strategy import abalearn


def test_flies_example():
    prolog = Prolog()
    reset(prolog)
    input = "prototype/test_resources/flies_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("prototype/test_resources/flies_example_solution.pl").read()
    )


def test_robber_example():
    prolog = Prolog()
    reset(prolog)
    input = "prototype/test_resources/robber_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("prototype/test_resources/robber_example_solution.pl").read()
    )


def test_robot_example():
    prolog = Prolog()
    reset(prolog)
    input = "prototype/test_resources/robot_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("prototype/test_resources/robot_example_solution.pl").read()
    )
