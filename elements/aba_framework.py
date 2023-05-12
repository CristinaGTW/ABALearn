from dataclasses import dataclass
from elements.components import Rule, Example, Atom

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
        content = self.get_content()
        f = open(filename, "w")
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

    def aspartix_input(self,prolog,filename):
        input = ''
        query: str = f"findall(arg(A,B),argument((A,B),Rule), Result)."
        solutions: list[dict] = list(prolog.query(query))
        for sol in solutions:
            for arg in sol['Result']:
                conc = str(arg.args[0])
                support = [str(a) for a in arg.args[1]]
                support_str = '['
                for s in support:
                    support_str += s +','
                if len(support_str)>1:
                    support_str = support_str[:-1]
                support_str += ']'    
                input += 'arg(' + conc + ',' + support_str + '). \n'

        query: str = f"findall(att(A,B),attacks(A,B), Result)."
        solutions: list[dict] = list(prolog.query(query))
        for sol in solutions:
            for att in sol['Result']:
                concA = str(att.args[0].args[0])
                supportA = [str(a) for a in att.args[0].args[1]]
                supportA_str = '['
                for s in supportA:
                    supportA_str += s +','
                if len(supportA_str) > 1:
                    supportA_str = supportA_str[:-1]
                supportA_str += ']'    
                concB = str(att.args[1].args[0])
                supportB = [str(a) for a in att.args[1].args[1]]
                supportB_str = '['
                for s in supportB:
                    supportB_str += s +','
                if len(supportB_str) > 1:
                    supportB_str = supportB_str[:-1]
                supportB_str += ']'    
                input += 'att((' + concA + ',' + supportA_str +'),('+ concB +',' + supportB_str +')). \n'
        f = open(filename, "w")
        f.write(input)
        f.close()
        