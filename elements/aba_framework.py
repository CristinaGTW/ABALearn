from dataclasses import dataclass
from elements.components import Rule, Example, Atom
import re
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
    

    
    def _from_prolog_output(self,s: str):
        predicate, arguments_str = s[:-1].split("(", 1)
        arguments = arguments_str.split(",")
        count = 0
        var_dict = {}
        arguments = [arg.strip() for arg in arguments]
        for idx, arg in enumerate(arguments):
            if "$VAR(" in arg:
                n = int(arg[arg.find("$") + 5 : -1])
                var = chr(ord("A") + n)
                arguments[idx] = var
            if arg[0] == "_":
                if arg in var_dict:
                    var = var_dict[arg]
                else:
                    var = chr(ord("A") + count)
                    var_dict[arg] = var
                    count += 1
                arguments[idx] = var
        arguments = [arg.strip() for arg in arguments]
        normalised = predicate + '('
        for arg in arguments:
            normalised += arg +','
        normalised = normalised[:-1]
        normalised += ')'
        return normalised

    def aspartix_input(self,prolog,filename):
        input = ''
        query: str = f"findall(A,argument((A,B),Rule), Result)."
        solutions: list[dict] = list(prolog.query(query))
        for sol in solutions:
            for arg in sol['Result']:
                conc = self._from_prolog_output(str(arg))
                input += 'arg(' + conc + '). \n'

        query: str = f"findall((A,B),attacks((A,A2),(B,B2)), Result)."
        solutions: list[dict] = list(prolog.query(query))
        for sol in solutions:
            for att in sol['Result']:
                att = str(att)[2:-1]
                [att1,att2] = re.split(r',\s*(?=[a-zA-Z])', att)
                att1 =  self._from_prolog_output(att1)
                att2 =  self._from_prolog_output(att2)
                input += 'att(' + att1 + ',' + att2+ '). \n'
        f = open(filename, "w")
        f.write(input)
        f.close()
        return filename
        