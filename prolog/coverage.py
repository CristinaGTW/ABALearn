from elements.components import Atom, Example
from elements.aba_framework import ABAFramework

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

def _format_res(result: list):
    return [r if r[0] != ',' else r.split(',',1)[1] for r in result]


def count_covered(prolog, aba_framework:ABAFramework, predicate, arity) -> tuple[int, int]:
    query_atom = f'('
    for i in range(arity):
        query_atom += chr(ord('A')+i) + ','
    query_atom = query_atom[:-1]
    query_atom += ')'
    query: str = f"findall({query_atom},covered([{predicate}{query_atom}],Rule), Result)."
    solutions: list[dict] = list(prolog.query(query))
    results = [sol['Result'] for sol in solutions]
    covered = []
    for result in results:
        covered.extend([str(r) for r in result])
    covered = _format_res(covered)
    covered = set(covered)
    pos_count = 0
    neg_count = 0
    for cov_ex in covered:
        if arity > 1:
            ex = Example("e", Atom.parse_atom(f'{predicate}{cov_ex}'))
        else:
            ex = Example("e", Atom.parse_atom(f'{predicate}({cov_ex})'))
        if ex in aba_framework.positive_examples:
            pos_count += 1
        elif ex in aba_framework.negative_examples:
            neg_count +=1

    return (pos_count, neg_count)
