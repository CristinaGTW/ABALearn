from dataclasses import dataclass, field
from elements.components import Rule, Example, Atom, Equality
from copy import deepcopy
from collections import defaultdict
from aspforaba.aspforaba import ASPforABA


@dataclass
class ABAFramework:
    background_knowledge: list[Rule]
    positive_examples: list[Example]
    negative_examples: list[Example]
    assumptions: list[Atom]
    contraries: list[tuple[Atom, Atom]]
    con_body_map: dict[str, list[str]]
    con_pos_ex_map: dict[str, list[str]]
    con_neg_ex_map: dict[str, list[str]]
    language: dict[str, int] = field(default_factory=lambda: defaultdict(dict))

    def create_file(self, filename: str):
        f = open(filename, "w")
        content = self.get_content()
        f.write(content)
        f.close()

    def get_content(self) -> str:
        content = "% Background Knowledge \n"
        for rule in self.background_knowledge:
            content += rule.to_prolog() + "\n"

        content += "\n% Positive Examples \n"
        for pos_ex in self.positive_examples:
            content += pos_ex.to_prolog_pos() + "\n"

        content += "\n% Negative Examples \n"
        for neg_ex in self.negative_examples:
            content += neg_ex.to_prolog_neg() + "\n"

        content += "\n% Assumptions \n"
        for assumption in self.assumptions:
            content += assumption.to_prolog_asm() + "\n"

        content += "\n% Contraries \n"
        for contrary in self.contraries:
            content += contrary[0].to_prolog_contrary(contrary[1]) + "\n"

        return content

    def to_asp(self):
        (all_instantiations, consts) = self.get_all_instantiations_and_consts()
        assumptions = self.get_all_assumptions(consts)
        contraries = self.get_all_contraries(consts)
        all_instantiations.sort()
        assumptions.sort()
        contraries.sort()
        language = []
        for r in all_instantiations:
            for atom in r:
                language.append(atom)
        for a in assumptions:
            language.append(a[0])
        for c in contraries:
            for atom in c:
                language.append(atom)
        language = list(set(language))
        language.sort()
        lang_map = {}
        for i, lang in enumerate(language):
            lang_map[lang] = i
        self.language = lang_map

        aspforaba_obj = ASPforABA()
        for r in all_instantiations:
            rule = (lang_map[r[0]]+1, [])
            for atom in r[1:]:
                rule[1].append(lang_map[atom] + 1)
            if rule not in aspforaba_obj.rules:
                aspforaba_obj.rules.append(rule)
        for a in assumptions:
            aspforaba_obj.assumptions.append(lang_map[a[0]] + 1)
        for c in contraries:
            aspforaba_obj.contraries.append(
                (lang_map[c[0]]+1, lang_map[c[1]]+1))
        return aspforaba_obj

    def get_all_assumptions(self, consts):
        ret = []
        for a in self.assumptions:
            result = []
            self._get_all_groundings([a], 0, 0, {}, {0: []}, consts, result)
            ret += result
        return ret

    def get_all_contraries(self, consts):
        ret = []
        for (a, c_a) in self.contraries:
            result = []
            self._get_all_groundings([a, c_a], 0, 0, {}, {
                                     0: [], 1: []}, consts, result)
            ret += result
        return ret

    def get_all_instantiations_and_consts(self):
        consts = []
        var_val_map = defaultdict(dict)
        for r in self.background_knowledge:
            head = r.head
            for arg in head.arguments:
                if not arg[0].isupper():
                    consts.append(arg)
            for b in r.body:
                if isinstance(b, Atom):
                    for arg in b.arguments:
                        if not arg[0].isupper():
                            consts.append(arg)
                else:
                    if not b.var_1[0].isupper():
                        consts.append(b.var_1)
                    else:
                        var_val_map[r.rule_id][b.var_1] = b.var_2
                    if not b.var_2[0].isupper():
                        consts.append(b.var_2)

        rules = deepcopy(self.background_knowledge)
        for i, r in enumerate(rules):
            no_change = False
            while not no_change:
                no_change = True
                for j, b in enumerate(r.body):
                    if isinstance(b, Atom):
                        for k, a in enumerate(b.arguments):
                            if a in var_val_map[r.rule_id]:
                                rules[i].body[j].arguments[k] = var_val_map[r.rule_id][a]
                                no_change = False
                    if isinstance(b, Equality):
                        if b.var_2 in var_val_map[r.rule_id] and var_val_map[r.rule_id][b.var_2] != b.var_1:
                            var_val_map[r.rule_id][b.var_1] = var_val_map[r.rule_id][b.var_2]
                            no_change = False
            for j, a in enumerate(r.head.arguments):
                if a in var_val_map:
                    rules[i].head.arguments[j] = var_val_map[r.rule_id][a]
        consts = list(set(consts))
        consts.sort()
        ret = []
        for r in rules:
            atoms = [r.head] + r.get_atoms()
            result = []
            curr_atoms_args = {}
            for i in range(len(atoms)):
                curr_atoms_args[i] = []
            self._get_all_groundings(
                atoms, 0, 0, var_val_map[r.rule_id], curr_atoms_args, consts, result)
            
            ret += result
        return (ret, consts)

    def _get_all_groundings(self, atoms: list[Atom], idx: int, arg_idx: int, var_val_map: dict[str, str], curr_atoms_args: dict[int, list[str]], consts: list[str], result: list[list[str]]):
        
        while idx < len(atoms):
            while arg_idx < len(atoms[idx].arguments):
                arg = atoms[idx].arguments[arg_idx]
                prev_args = deepcopy(curr_atoms_args[idx][:arg_idx])
                if arg in var_val_map:
                    curr_atoms_args[idx] = prev_args + [var_val_map[arg]]
                    self._replace_all(curr_atoms_args, arg, var_val_map[arg])
                else:
                    if arg[0].isupper():
                        for c in consts:
                            var_val_map[arg] = c
                            curr_atoms_args[idx] = prev_args + [c]
                            curr_atoms_args = self._replace_all(
                                curr_atoms_args, arg, c)
                            self._get_all_groundings(
                                atoms, idx, arg_idx+1, var_val_map, curr_atoms_args, consts, result)
                            
                        arg_idx += 1
                    else:
                        curr_atoms_args[idx] = prev_args+[arg]
                arg_idx += 1
            arg_idx = 0
            idx += 1
        instantiation = []
        for i, a in enumerate(atoms):
            atom_str = a.predicate + '('
            for arg in curr_atoms_args[i]:
                atom_str += arg + ','
            atom_str = atom_str[:-1]
            atom_str += ')'
            instantiation += [atom_str]
        if instantiation not in result:
            result.append(instantiation)
        else:
            var_val_map.popitem()

    def _replace_all(self, d: dict[int, list[str]], a: str, b: str):
        for k in d:
            d[k] = [b if x == a else x for x in d[k]]
        return d
