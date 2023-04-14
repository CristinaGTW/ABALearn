from elements.components import Atom,Example

# Checks if the list of examples is covered
def covered(prolog, exs:list[Example]) -> bool:
    exs_str:str = ""
    for ex in exs:
        exs_str += str(ex.fact) +','
    exs_str = exs_str[:-1]
    query = f"covered([{exs_str}])."    
    result:list[dict] = list(prolog.query(query))
    return result == [{}]

# Finds all values sol for which atom.predicate(sol) is covered
def get_covered_solutions(prolog, atom:Atom) -> list[dict]:
    query:str = f"covered([{atom}])."
    solutions:list[dict] = list(prolog.query(query))
    return solutions
    