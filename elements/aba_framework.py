from dataclasses import dataclass, field
from elements.components import Rule, Example, Atom, Equality
from copy import deepcopy

@dataclass
class ABAFramework:
    background_knowledge: dict[str,Rule]
    positive_examples: dict[str,Example]
    negative_examples: dict[str,Example]
    assumptions: list[Atom]
    contraries: list[tuple[Atom, Atom]]
    con_body_map: dict[str, list[str]]
    con_pos_ex_map: dict[str, list[str]]
    con_neg_ex_map: dict[str, list[str]]
    arguments: dict[str, list[list[str|Atom]]] = field(default_factory=lambda:{})
    language: list[str] = field(default_factory=lambda:[])


    def create_file(self, filename: str, with_examples=False):
        f = open(filename, "w")
        content = self.get_content(with_examples)
        f.write(content)
        f.close()

    def adjust_arguments(self, rule_id):
        to_remove = []
        removed_arguments = {}
        for accepted, arguments in self.arguments.items():
            removed_args = list(filter(lambda arg:rule_id in arg,arguments))
            if len(removed_args) > 0:
                if accepted not in removed_arguments:
                    removed_arguments[accepted] = []
                removed_arguments[accepted].extend(removed_args)
            self.arguments[accepted] = list(filter(lambda arg:rule_id not in arg,arguments))
            if self.arguments[accepted] == []:
                to_remove.append(accepted)
        for a in to_remove:
            self.arguments.pop(a)
        return removed_arguments
    
    def get_new_rules(self) -> dict[str,Rule]:
        new_rules = {}
        for rule_id, rule in self.background_knowledge.items():
                if rule_id[:2] == 'r_':
                    new_rules[rule_id] = rule
        return new_rules

    def is_assumption(self, atom):
        return any([asm.predicate == atom.predicate for asm in self.assumptions])

    def get_contrary(self, atom):
        for a,c_a in self.contraries:
            if a.predicate == atom.predicate:
                con = deepcopy(c_a)
                con.arguments = atom.arguments
                return con
    
    def get_all_potential_top_rules(self, atom):
        rules = []
        for rule in self.background_knowledge.values():
            if rule.head.predicate == atom.predicate:
                rules.append(rule)
        return rules


    def get_content(self, with_examples=False) -> str:
        content = "% Background Knowledge \n"
        for rule in self.background_knowledge.values():
            content += rule.to_prolog() + "\n"
        
        if with_examples:
            content += "\n% Positive Examples \n"
            for pos_ex in self.positive_examples.values():
                content += pos_ex.to_prolog_pos() + "\n"

            content += "\n% Negative Examples \n"
            for neg_ex in self.negative_examples.values():
                content += neg_ex.to_prolog_neg() + "\n"

        content += "\n% Assumptions \n"
        for assumption in self.assumptions:
            content += assumption.to_prolog_asm() + "\n"

        content += "\n% Contraries \n"
        for contrary in self.contraries:
            content += contrary[0].to_prolog_contrary(contrary[1]) + "\n"

        return content
