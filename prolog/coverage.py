from elements.components import Atom, Example


# Checks if the list of examples is covered
def covered(prolog, exs: list[Example]) -> bool:
    for ex in exs:
        exs_str = str(ex.fact)
        query = f"covered([{exs_str}],[R])."
        result: list[dict] = list(prolog.query(query))
        if len(result) == 0:
            return False
    return True

def get_top_rule(prolog, atom: Atom):
    query = f"covered([{atom}],[TopRule])."
    result: list[dict] = list(prolog.query(query))
    return [r['TopRule'] for r in result]

# Finds all values sol for which atom.predicate(sol) is covered
def get_covered_solutions(prolog, atom: Atom) -> list[dict]:
    query: str = f"covered([{atom}],[Rule])."
    solutions: list[dict] = list(prolog.query(query))
    for sol in solutions:
        sol.pop('Rule',None)
        for k in sol:
            sol[k] = str(sol[k])
    i = 0
    size = len(solutions)
    while i < size:
        temp_sols = solutions[0:i] + solutions[i + 1 :]
        if i in temp_sols:
            solutions = temp_sols
            size -= 1
        i += 1
    return solutions


def count_covered(prolog, aba_framework) -> tuple[int, int]:
    pos_count = 0
    for pos_ex in aba_framework.positive_examples:
        if covered(prolog, [pos_ex]):
            pos_count += 1
    neg_count = 0
    for neg_ex in aba_framework.negative_examples:
        if covered(prolog, [neg_ex]):
            neg_count += 1

    return (pos_count, neg_count)
