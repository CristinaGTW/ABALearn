from dataclasses import dataclass
from components import Rule, Example, Atom
@dataclass
class ABAFramework:
    background_knowledge: list[Rule]
    positive_examples: list[Example]
    negative_examples: list[Example]
    assumptions: list[Atom]
    contraries:list[tuple[Atom, Atom]]

    def create_input_file(filename):
        f = open(filename,"x")
        content = get_content()
        f.write(content)
        f.close()
    
    def get_content():
        content = ""
        for rule in background_knowledge:
            content += rule.to_prolog() + '\n'
        
        for pos_ex in positive_examples:
            content += pos_ex.to_prolog_pos() + '\n'
        
        for neg_ex in negative_examples:
            content += neg_ex.to_prolog_neg() + '\n'
        
        for assumption in assumptions:
            content += assumption.to_prolog() + '\n'
        
        for contrary in contraries:
            content += contrary.to_prolog() + '\n'
        
        return content