from pyswip import Prolog
from prolog.config import set_up_abalearn, reset
from strategy import abalearn


def test_flies_example():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/flies_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("test_resources/flies_example_solution.pl").read()
    )


def test_flies_2_example():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/flies_2_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("test_resources/flies_2_example_solution.pl").read()
    )


def test_flies_3_example():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/flies_3_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("test_resources/flies_3_example_solution.pl").read()
    )


def test_robber_example():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/robber_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("test_resources/robber_example_solution.pl").read()
    )


def test_robot_example():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/robot_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("test_resources/robot_example_solution.pl").read()
    )


def test_path_example():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/path_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("test_resources/path_example_solution.pl").read()
    )


def test_nixon_diamond_example():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/nixon_diamond_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert (
        aba_framework.get_content()
        == open("test_resources/nixon_diamond_example_solution.pl").read()
    )
