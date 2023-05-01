from dataclasses import dataclass, field
from elements.components import Rule, Example, Atom, Equality


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
