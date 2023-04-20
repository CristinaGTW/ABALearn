from pyswip import Prolog


def set_up_abalearn(input_file_path: str) -> Prolog:
    prolog = Prolog()
    prolog.consult("prototype/resources/abalearn.pl")
    prolog.consult("prototype/resources/coverage.pl")
    if input_file_path != "":
        prolog.consult(input_file_path)
    return prolog


def reset(prolog: Prolog) -> None:
    list(prolog.query("restart."))
    return prolog
