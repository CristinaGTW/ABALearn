from dataclasses import dataclass, field
from elements.components import Rule, Example, Atom, Equality
@dataclass
class ABAFramework:
    background_knowledge: list[Rule]
    positive_examples: list[Example]
    negative_examples: list[Example]
    assumptions: list[Atom]
    contraries:list[tuple[Atom, Atom]]
    language: set[str] = field(default_factory=set)

    def create_file(self,filename:str, with_eq:bool):
        f = open(filename,"w")
        content = self.get_content(with_eq)
        f.write(content)
        f.close()
    
    def get_content(self, with_eq:bool) -> str:
        content = "% Background Knowledge \n"
        for rule in self.background_knowledge:
            content += rule.to_prolog(with_eq) + '\n'
        
        content += "\n% Positive Examples \n"
        for pos_ex in self.positive_examples:
            content += pos_ex.to_prolog_pos() + '\n'
        
        content += "\n% Negative Examples \n"        
        for neg_ex in self.negative_examples:
            content += neg_ex.to_prolog_neg() + '\n'

        
        content += "\n% Assumptions \n"        
        for assumption in self.assumptions:
            if not assumption.predicate == "fake_asm":
                content += assumption.to_prolog_asm() + '\n'
        
        
        content += "\n% Contraries \n"   
        for contrary in self.contraries:
            if not contrary[0].predicate == "fake_alpha":
                content += contrary[0].to_prolog_contrary(contrary[1]) + '\n'
            
        return content

    def get_language_size(self):
        return len(self.language)


    def set_language(self):
        variables = []
        for rule in self.background_knowledge:
            for arg in rule.head.arguments:
                if arg.islower():
                    variables.append(arg)
            for x in rule.body:
                if isinstance(x, Atom):
                    for arg in x.arguments:
                        if arg.islower():
                            variables.append(arg)
                else:
                    assert isinstance(x, Equality)
                    variables.append(x.var_2)
        for examples in self.positive_examples + self.negative_examples:
            for arg in examples.fact.arguments:
                if arg.islower():
                    variables.append(arg)
        language = set(variables)