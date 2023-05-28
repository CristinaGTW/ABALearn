from elements.aba_framework import ABAFramework
from elements.components import Atom,Rule,Equality
from copy import deepcopy

def covered(aba_framework:ABAFramework, atom:Atom):
    return cov_and_grounding(aba_framework,atom, {}, [])[0]

def cov_and_grounding(aba_framework:ABAFramework, atom:Atom, var_dict, asms:list[Atom]):
    if aba_framework.is_assumption(atom):
        if atom in asms:
            return True, var_dict
        return not cov_and_grounding(aba_framework, aba_framework.get_contrary(atom), {}, asms+[atom])[0], var_dict
    else:
        rules = aba_framework.get_all_potential_top_rules(atom)
        for rule in rules:
            var_dict = map_vars(rule.head, atom)
            if rule_supports(aba_framework, rule, atom, var_dict, asms):
                return True, var_dict
    return False, var_dict

def get_var_dict(eqs:list[Equality], var_dict:dict[str,str]):
    change = False
    for eq in eqs:
        if eq.var_1[0].isupper():
            if eq.var_1 not in var_dict:
                change = True
                var_dict[eq.var_1] = eq.var_2
            else:
                if var_dict[eq.var_1] != eq.var_2:
                    if eq.var_2[0].isupper():
                        if eq.var_2 in var_dict:
                            if var_dict[eq.var_1] != var_dict[eq.var_2]:
                                change = True
                                var_dict[eq.var_1] = var_dict[eq.var_2]
                        else:
                            change = True
                            var_dict[eq.var_2] = eq.var_1
                    else:
                        if var_dict[eq.var_1][0].isupper():
                            var_dict[var_dict[eq.var_1]] = eq.var_2
                            var_dict[eq.var_1] = eq.var_2
                            change = True
                        else:
                            var_dict[eq.var_1] = eq.var_2
                            change = True
                        
    if change:
        return get_var_dict(eqs,var_dict)
    return var_dict

def eqs_ground(atom: Atom, eqs: list[Equality], var_dict):
    var_dict = get_var_dict(eqs, var_dict)
    return ground_from_dict(atom, var_dict), var_dict

def ground_from_dict(atom, var_dict):
    gr_atom = deepcopy(atom)
    for idx,arg in enumerate(gr_atom.arguments):
        if arg[0].isupper():
            if arg in var_dict:
                gr_atom.arguments[idx] = var_dict[arg]
    return gr_atom

def map_vars(atom_1,atom_2):
    var_dict = {}
    for arg1,arg2 in zip(atom_1.arguments, atom_2.arguments):
        var_dict[arg1] = arg2
    return var_dict

def rule_supports(aba_framework:ABAFramework, rule:Rule, atom:Atom, var_dict,asms):
    if rule.head.predicate == atom.predicate:
        eqs = rule.get_equalities()
        ground_atom, var_dict = eqs_ground(rule.head, eqs, var_dict)
        if len(rule.body) == len(eqs) and ground_atom.correct_grounding(str(atom))[0]:
            return True
        else:
            if len(rule.get_atoms()) > 0:
                for b in rule.get_atoms():
                    cov, var_dict = cov_and_grounding(aba_framework, ground_from_dict(b, var_dict), var_dict,asms)
                    if not cov:
                        return False
                return True 
    return False