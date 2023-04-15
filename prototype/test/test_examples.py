from prolog.config import set_up_abalearn
from strategy import abalearn

def test_flies_example():
    input = "prototype/resources/flies_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert aba_framework == ""

def test_robber_example():
    input = "prototype/resources/robber_example.pl"
    prolog = set_up_abalearn(input)
    aba_framework = abalearn(prolog)
    assert aba_framework == ""