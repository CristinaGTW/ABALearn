from elements.aba_framework import ABAFramework
from elements.components import Example, Atom
import subprocess

def covered(aba_framework: ABAFramework, exs:list[Example]) -> bool:
    aba_framework.to_asp("covered.txt")
    for example in exs:
        ex_str = example.get_predicate() + '('
        for arg in example.get_arguments():
            ex_str += arg + ','
        ex_str = ex_str[:-1]
        ex_str += ')'
        if ex_str not in aba_framework.language:
            return False
        cov = run_asp_for_aba(aba_framework.language[ex_str] + 1)
        if not cov:
            return False
    return True


# Finds all values sol for which atom.predicate(sol) is covered
def get_covered_solutions(aba_framework:ABAFramework, atom: Atom) -> list[dict]:
    aba_framework.to_asp("covered.txt")
    candidates = []
    sols = []
    for k in aba_framework.language:
        predicate = k.split('(')[0]
        if predicate == atom.predicate:
            candidates.append(k)
    for c in candidates:
        if run_asp_for_aba(aba_framework.language[c]+1):
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


def run_asp_for_aba(example: str) -> bool:
    proc = subprocess.Popen(f'python aspforaba/aspforaba.py -p DC-CO -f covered.txt -a {example}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = proc.communicate()[0].decode()
    return result =='YES\n'
