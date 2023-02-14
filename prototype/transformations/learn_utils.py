import subprocess
from pyswip import Prolog


# Runs abalearn.pl and returns the associated subrpocess
def set_up_abalearn():
    prolog = Prolog()
    prolog.consult("abalearn.pl")
    return prolog


def add_rule(prolog, head, body):
    prolog.query(f"add_rule({head},{body}).")


def show_rules(prolog):
    prolog.query("show_rules.")

if __name__=="__main__":
    prolog = set_up_abalearn()
    add_rule(prolog,"bird(X)","[penguin(X)]")
    rules = show_rules(prolog)
    for r in rules:
        print(r)