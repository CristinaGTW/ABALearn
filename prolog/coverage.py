from elements.components import Atom, Example
from elements.aba_framework import ABAFramework
from copy import deepcopy

def covered(aba_framework, atom: Atom):
    if str(atom) in aba_framework.arguments:
        for argument in aba_framework.arguments[str(atom)]:
            asms = list(filter(lambda a: isinstance(a,Atom), argument))
            if len(asms) == 0:
                return True
            if not any([covered(aba_framework, Atom('c_'+ a.predicate, a.arguments)) for a in asms]):
                return True
        return False
    for accepted in aba_framework.arguments:
        flag, _ = atom.correct_grounding(accepted)
        if flag:
            if covered(aba_framework, Atom.parse_atom(accepted)):
                return True
    return False

def get_top_rule(aba_framework, atom: Atom):
    if str(atom) in aba_framework.arguments:
        arguments = aba_framework.arguments[str(atom)]
        top_rules = []
        for arg in arguments:
            if isinstance(arg[0], str):
                top_rules.append(arg[0])
        return top_rules
    for accepted,arguments in aba_framework.arguments.items():
        flag, _ = atom.correct_grounding(accepted)
        if flag:
            top_rules = []
            for arg in arguments:
                if isinstance(arg[0], str):
                    top_rules.append(arg[0])
            return top_rules
    return []
            
# Finds all values sol for which atom.predicate(sol) is covered
def get_covered_solutions(aba_framework, atom: Atom) -> list[dict]:
    sols = []
    for argument in aba_framework.arguments:
        if covered(aba_framework, Atom.parse_atom(argument)):
            flag, res = atom.correct_grounding(argument)
            if flag:
                sols.append(res)
    return sols



def update_covered(prolog, aba_framework:ABAFramework, rule):
    target_atom = deepcopy(aba_framework.background_knowledge[rule].head)
    args = {}
    for (idx,arg) in enumerate(target_atom.arguments):
        if arg[0].isupper():
            args[arg] = idx
    target_str = str(target_atom)
    query = f'accepted({target_str}, Rules, Asms).'
    solutions: list[dict] = list(prolog.query(query))
    for sol in solutions:
        for arg in args:
            target_atom.arguments[args[arg]] = str(sol[arg])
        target_atom = Atom.parse_atom(str(target_atom))
        if(str(target_atom) not in aba_framework.arguments):
            aba_framework.arguments[str(target_atom)] = []
        argument = [str(rule) for rule in sol['Rules']] + [Atom.parse_atom(str(asm)) for asm in sol['Asms']]
        if argument not in aba_framework.arguments[str(target_atom)]:
            aba_framework.arguments[str(target_atom)].append(argument) 


def set_covered(prolog, aba_framework:ABAFramework):
    for r in aba_framework.background_knowledge:
        update_covered(prolog, aba_framework, r) 



def count_neg_covered(aba_framework:ABAFramework, predicate) -> int:
    count = 0
    for ex in aba_framework.negative_examples.values():
        if str(ex.fact) in aba_framework.arguments:
            count += 1
    return count