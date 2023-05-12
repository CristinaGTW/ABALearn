from pyswip import Prolog
from prolog.config import reset
from prolog.config import set_up_abalearn
from prolog.info import get_current_aba_framework
from elements.aba_framework import ABAFramework

def test_aspartix():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "data/acute/acute.pl"
    prolog = set_up_abalearn(input)
    aba_framework:ABAFramework = get_current_aba_framework(prolog, None)
    aba_framework.aspartix_input(prolog,'test_aspartix.pl')