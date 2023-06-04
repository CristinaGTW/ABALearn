from elements.aba_framework import ABAFramework
from elements.components import Atom, Rule, Equality
from copy import deepcopy
from exceptions.abalearn import IncorrectGroundingException


def covered(aba_framework: ABAFramework, atom: Atom):
    return cov_helper(aba_framework, atom, [], {})[0]


def get_top_rules(aba_framework: ABAFramework, atom: Atom):
    rules = aba_framework.get_all_potential_top_rules(atom)
    top_rules = []
    for rule in rules:
        var_dict = map_vars(rule.head, atom)
        if rule_supports(aba_framework, rule, atom, var_dict, [])[0]:
            top_rules.append(rule)
    return top_rules


def get_cov_solutions_with_atoms(aba_framework, atom):
    var_dicts = all_cov_groundings(aba_framework, atom, {}, [], [])[1]
    res = []
    for d in var_dicts:
        new_dict = {}
        for arg, k in zip(atom.arguments, d.keys()):
            new_dict[arg] = d[k]
        res.append((ground_from_dict(atom, new_dict), new_dict))
    return res


def get_cov_solutions(aba_framework, atom):
    var_dicts = all_cov_groundings(aba_framework, atom, {}, [], [])[1]
    res = []
    for d in var_dicts:
        new_dict = {}
        for arg, k in zip(atom.arguments, d.keys()):
            new_dict[arg] = d[k]
        res.append(new_dict)
    return res


def all_cov_groundings(aba_framework, atom, var_dict, asms, var_dicts):
    if aba_framework.is_assumption(atom):
        if not cov_helper(
            aba_framework, aba_framework.get_contrary(atom), asms + [atom], var_dict
        )[0]:
            return True, var_dicts
        else:
            return False, []
    else:
        rules = aba_framework.get_all_potential_top_rules(atom)
        for rule in rules:
            var_dict = map_vars(rule.head, atom)
            cov, new_dicts = rule_supports_with_gr(
                aba_framework, rule, atom, var_dict, [], []
            )
            if cov:
                var_dicts += new_dicts
    if len(var_dicts) > 0:
        return True, var_dicts
    return False, []


def count_covered(aba_framework: ABAFramework) -> int:
    neg_count = 0
    for ex in aba_framework.negative_examples.values():
        if covered(aba_framework, ex.fact):
            neg_count += 1
    pos_count = 0
    for ex in aba_framework.positive_examples.values():
        if covered(aba_framework, ex.fact):
            pos_count += 1
    return (pos_count, neg_count)


def cov_helper(aba_framework: ABAFramework, atom: Atom, asms: list[Atom], var_dict):
    if aba_framework.is_assumption(atom):
        if atom in asms:
            return True, [var_dict]
        return not cov_helper(
            aba_framework, aba_framework.get_contrary(atom), asms + [atom], {}
        )[0], [var_dict]
    else:
        rules = aba_framework.get_all_potential_top_rules(atom)
        var_dicts = []
        for rule in rules:
            new_dict = var_dict | map_vars(rule.head, atom)
            cov, res_dict = rule_supports(aba_framework, rule, atom, new_dict, asms)
            if cov:
                var_dicts += res_dict
        if len(var_dicts) > 0:
            return True, var_dicts
    return False, []



def rule_supports(aba_framework: ABAFramework, rule: Rule, atom: Atom, var_dict, asms):
    if rule.head.predicate == atom.predicate:
        eqs = rule.get_equalities()
        try:
            ground_atom, var_dict = eqs_ground(rule.head, eqs, var_dict)
        except IncorrectGroundingException:
            return False, []
        if len(rule.body) == len(eqs) and ground_atom.correct_grounding(str(atom))[0]:
            return True, [var_dict]
        else:
            atoms = rule.get_atoms()
            res = solve_with_dict(aba_framework, atoms, asms, var_dict, 0)
            if len(res) > 0:
                return True, res
    return False, []


def solve_with_dict(aba_framework, atoms, asms, var_dict, idx):
    if idx == len(atoms):
        return [var_dict]
    b = atoms[idx]
    b_gr = ground_from_dict(b, var_dict)
    cov, new_dicts = cov_helper(aba_framework, b_gr, asms, var_dict)
    solution = []
    if cov:
        for d in new_dicts:
            solution += solve_with_dict(aba_framework, atoms, asms, d, idx + 1)
    return solution


def get_var_dict(eqs: list[Equality], var_dict: dict[str, str]):
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
                            raise IncorrectGroundingException()

    if change:
        return get_var_dict(eqs, var_dict)
    return var_dict


def eqs_ground(atom: Atom, eqs: list[Equality], var_dict):
    var_dict = get_var_dict(eqs, var_dict)
    return ground_from_dict(atom, var_dict), var_dict


def ground_from_dict(atom, var_dict):
    gr_atom = deepcopy(atom)
    for idx, arg in enumerate(gr_atom.arguments):
        if arg[0].isupper():
            if arg in var_dict:
                gr_atom.arguments[idx] = var_dict[arg]
    return gr_atom


def map_vars(atom_1, atom_2):
    var_dict = {}
    for arg1, arg2 in zip(atom_1.arguments, atom_2.arguments):
        if not arg2[0].isupper():
            var_dict[arg1] = arg2
    return var_dict


def rule_supports_with_gr(
    aba_framework: ABAFramework, rule: Rule, atom: Atom, var_dict, asms, var_dicts
):
    if rule.head.predicate == atom.predicate:
        eqs = rule.get_equalities()
        try:
            ground_atom, var_dict = eqs_ground(rule.head, eqs, var_dict)
        except IncorrectGroundingException:
            return False, []
        if len(rule.body) == len(eqs) and ground_atom.correct_grounding(str(atom))[0]:
            return True, [var_dict]
        else:
            if len(rule.get_atoms()) > 0:
                res = []
                for b in rule.get_atoms():
                    cov, new_dicts = all_cov_groundings(
                        aba_framework,
                        ground_from_dict(b, var_dict),
                        var_dict,
                        asms,
                        var_dicts,
                    )
                    if not cov:
                        return False, []
                    else:
                        res += new_dicts
                return True, res
    return False, []
