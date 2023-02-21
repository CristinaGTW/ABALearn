from dataclasses import dataclass
from elements.components import Rule, Example, Atom
@dataclass
class ABAFramework:
    background_knowledge: list[Rule]
    positive_examples: list[Example]
    negative_examples: list[Example]
    assumptions: list[Atom]
    contraries:list[tuple[Atom, Atom]]

    def create_file(self,filename):
        f = open(filename,"w")
        content = self.get_content()
        f.write(content)
        f.close()
    
    def get_content(self):
        content = ""
        for rule in self.background_knowledge:
            content += rule.to_prolog() + '\n'
        
        for pos_ex in self.positive_examples:
            content += pos_ex.to_prolog_pos() + '\n'
        
        for neg_ex in self.negative_examples:
            content += neg_ex.to_prolog_neg() + '\n'
        
        for assumption in self.assumptions:
            content += assumption.to_prolog() + '\n'
        
        for contrary in self.contraries:
            content += contrary.to_prolog() + '\n'
        
        return content