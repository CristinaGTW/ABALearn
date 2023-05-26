from elements.components import Atom, Example
import subprocess
import re
# Checks if the list of examples is covered
def covered(prolog, aba_framework, exs: list[Example]) -> bool:
    grounded_extension = aba_framework.get_grounded_extension(prolog)
    for ex in exs:
        if str(ex.fact) not in aba_framework.claim_to_arguments:
            return False
        if not any([aba_framework.arguments_to_id[arg] in grounded_extension for arg in aba_framework.claim_to_arguments[str(ex.fact)]]):
            return False
    return True
        

def extract_in_terms(input_string):
    in_terms = re.findall(r'in\((.*?)\)', input_string)
    return [int(term) for term in in_terms]

def make_grounded_extension(prolog, aba_framework):
    input_file = aba_framework.aspartix_input(prolog, "input.af")
    process = subprocess.Popen(f'clingo {input_file} aspartix/ground.dl aspartix/filter.lp 0', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = process.communicate()
    grounded_extension = extract_in_terms(out.decode())
    return grounded_extension

def get_top_rule(prolog, atom: Atom):
    query = f"covered([{atom}],[TopRule])."
    result: list[dict] = list(prolog.query(query))
    return [r['TopRule'] for r in result]

# Finds all values sol for which atom.predicate(sol) is covered
def get_covered_solutions(prolog, aba_framework, atom: Atom) -> list[dict]:
    grounded_extension = aba_framework.get_grounded_extension(prolog)
    solutions = []
    keys = {}
    for idx,arg in enumerate(atom.arguments):
        if arg[0].isupper():
            keys[arg] = idx
    for at in grounded_extension:
        argument = aba_framework.id_to_arguments[at].split(',alpha',1)[0]
        [pred,_] = argument.split('(',1)
        if pred == atom.predicate:
            at_sol = Atom.parse_atom(argument)
            sol_dict = {}
            for key in keys:
                sol_dict[key] = at_sol.arguments[keys[key]]
            solutions.append(sol_dict)

    
    return solutions

def _format_res(result: list):
    return [r if r[0] != ',' else r.split(',',1)[1] for r in result]


def count_neg_covered(prolog, aba_framework, predicate) -> tuple[int, int]:
    grounded_extension = aba_framework.get_grounded_extension(prolog)
    neg_count = 0
    for ex in aba_framework.negative_examples.values():
        if ex.get_predicate() == predicate and str(ex.fact) in grounded_extension:
            neg_count+=1
    return neg_count
