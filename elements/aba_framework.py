from dataclasses import dataclass, field
from elements.components import Rule, Example, Atom, Equality
from copy import deepcopy


@dataclass
class ABAFramework:
    background_knowledge: dict[str, Rule]
    positive_examples: dict[str, Example]
    negative_examples: dict[str, Example]
    assumptions: list[Atom]
    contraries: list[tuple[Atom, Atom]]
    con_body_map: dict[str, list[str]]
    con_pos_ex_map: dict[str, list[str]]
    con_neg_ex_map: dict[str, list[str]]
    language: list[str] = field(default_factory=lambda: [])

    def create_file(self, filename: str, with_examples=False):
        f = open(filename, "w")
        content = self.get_content(with_examples)
        f.write(content)
        f.close()

    def get_new_rules(self) -> dict[str, Rule]:
        new_rules = {}
        for rule_id, rule in self.background_knowledge.items():
            if rule_id[:2] == "r_":
                new_rules[rule_id] = rule
        return new_rules

    def is_assumption(self, atom):
        return any([asm.predicate == atom.predicate for asm in self.assumptions])

    def get_contrary(self, atom):
        for a, c_a in self.contraries:
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
            if len(self.positive_examples) > 0:
                content += "\n% Positive Examples \n"
                for pos_ex in self.positive_examples.values():
                    content += pos_ex.to_prolog_pos() + "\n"

            if len(self.negative_examples) > 0:
                content += "\n% Negative Examples \n"
                for neg_ex in self.negative_examples.values():
                    content += neg_ex.to_prolog_neg() + "\n"

        if len(self.assumptions) > 0:
            content += "\n% Assumptions \n"
            for assumption in self.assumptions:
                content += assumption.to_prolog_asm() + "\n"

            content += "\n% Contraries \n"
            for contrary in self.contraries:
                content += contrary[0].to_prolog_contrary(contrary[1]) + "\n"

        return content

    def get_learned_rules(self):
        content = "\n--- Learned rules --- \n"
        new_rules = self.get_new_rules()
        for rule_id in new_rules:
            content += str(self.background_knowledge[rule_id]).split(":")[1] + "\n"
        return content
