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
        content = "% Background Knowledge \n"
        for rule in self.background_knowledge:
            content += rule.to_prolog() + '\n'
        
        content += "\n% Positive Examples \n"
        for pos_ex in self.positive_examples:
            content += pos_ex.to_prolog_pos() + '\n'
        
        content += "\n% Negative Examples \n"        
        for neg_ex in self.negative_examples:
            content += neg_ex.to_prolog_neg() + '\n'

        
        content += "\n% Assumptions \n"        
        # if len(self.assumptions) == 0:
        #     content += "% my_asm(_) placeholder \n"
        #     content += "my_asm(fake_asm(X)). \n"
        # else:
        for assumption in self.assumptions:
            content += assumption.to_prolog_asm() + '\n'
        
        
        content += "\n% Contraries \n"   
        # if len(self.assumptions) == 0:
        #     content += "% contrary(_,_) placeholder \n"
        #     content += "contrary(fake_alpha(X),fake_c_alpha(X)). \n"     
        # else:
        for contrary in self.contraries:
            content += contrary[0].to_prolog_contrary(contrary[1]) + '\n'
        
        return content