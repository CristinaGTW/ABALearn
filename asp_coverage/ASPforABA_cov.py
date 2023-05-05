from elements.aba_framework import ABAFramework
from elements.components import Example, Atom
from aspforaba.aspforaba import ASPforABA

def covered(aba_framework: ABAFramework, exs:list[Example]) -> bool:
    aspforaba_obj = aba_framework.to_asp()
    for example in exs:
        ex_str = example.get_predicate() + '('
        for arg in example.get_arguments():
            ex_str += arg + ','
        ex_str = ex_str[:-1]
        ex_str += ')'
        if ex_str not in aba_framework.language:
            return False
        cov = run_asp_for_aba(aspforaba_obj, aba_framework.language[ex_str] + 1)
        if not cov:
            return False
    return True


# Finds all values sol for which atom.predicate(sol) is covered
def get_covered_solutions(aba_framework:ABAFramework, atom: Atom) -> list[dict]:
    aspforaba_obj=aba_framework.to_asp()
    candidates = []
    sols = []
    for k in aba_framework.language:
        k_atom = Atom.parse_atom(k)
        if k_atom.predicate == atom.predicate:
            args_match = True
            for i,arg in enumerate(atom.arguments):
                if not arg[0].isupper():
                    if k_atom.arguments[i] != arg:
                        args_match = False
                        break
            if args_match:
                candidates.append(k)
    for c in candidates:
        if run_asp_for_aba(aspforaba_obj, aba_framework.language[c]+1):
            a = Atom.parse_atom(c)
            sols.append(dict(zip(atom.arguments, a.arguments)))
    return sols




def count_covered(aba_framework) -> tuple[int, int]:
    pos_count = 0
    for pos_ex in aba_framework.positive_examples:
        if covered(aba_framework, [pos_ex]):
            pos_count += 1
    neg_count = 0
    for neg_ex in aba_framework.negative_examples:
        if covered(aba_framework, [neg_ex]):
            neg_count += 1

    return (pos_count, neg_count)


def run_asp_for_aba(aspforaba_obj:ASPforABA,example: int) -> bool:
    clingo_loc = 'aspforaba/clingo/bin/clingo'
    res = aspforaba_obj.credulous(clingo_loc,'CO',example)
    return res
