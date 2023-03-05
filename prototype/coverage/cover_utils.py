from subprocess import Popen, PIPE
import os


def covered(prolog, exs):
    exs_str = ""
    for ex in exs:
        exs_str += str(ex.fact) +','
    exs_str = exs_str[:-1]
    query = f"covered([{exs_str}])."    
    result = list(prolog.query(query))
    return result == [{}]

def get_covered_solutions(prolog, atom):
    query = f"covered([{atom}])."
    result = list(prolog.query(query))
    sol = get_sol(result, atom.arguments)
    return sol
    

def get_sol(solutions, variables):
    result = []
    for sol in solutions:
        result.append(list(sol.values()))
    return result


