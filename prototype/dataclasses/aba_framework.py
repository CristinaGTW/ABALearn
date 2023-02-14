from dataclasses import dataclass

@dataclass
class ABAFramework:
    background_knowledge: list[Rule]
    assumptions: list[Assumption]
    positive_examples: list[Example]
    negative_examples: list[Example]