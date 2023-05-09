from pyswip import Prolog


def set_up_abalearn(input_file_path: str) -> Prolog:
    prolog = Prolog()
    prolog.consult("prolog_scripts/abalearn.pl")
    prolog.consult("prolog_scripts/coverage.pl")
    if input_file_path != "":
        prolog.consult(input_file_path)
    return prolog


def reset(prolog: Prolog) -> None:
    q = list(prolog.query("restart."))
    del q
    return prolog
