from pyswip import Prolog

def set_up_abalearn(input_file_path):
    prolog = Prolog()
    prolog.consult("prototype/resources/abalearn.pl")
    prolog.consult("prototype/resources/coverage.pl")
    prolog.consult(input_file_path)
    list(prolog.query("assert(my_asm(fake_asm(X)))."))
    list(prolog.query("assert(contrary(fake_alpha(X),fake_c_alpha(X)))."))
    return prolog