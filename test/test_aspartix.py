from pyswip import Prolog
from prolog.config import reset
from prolog.config import set_up_abalearn
from prolog.info import get_current_aba_framework
from elements.aba_framework import ABAFramework
from prolog.coverage import make_grounded_extension

def test_aspartix():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/flies_example_solution.pl"
    prolog = set_up_abalearn(input)
    aba_framework:ABAFramework = get_current_aba_framework(prolog, None)
    aba_framework.aspartix_input(prolog,'test_aspartix.pl')
    
def test_grounded_extension():
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    reset(prolog)
    input = "test_resources/robot_example_solution.pl"
    prolog = set_up_abalearn(input)
    aba_framework:ABAFramework = get_current_aba_framework(prolog, None)
    grounded_ext = make_grounded_extension(prolog, aba_framework)
    assert 'busy(3)' in grounded_ext