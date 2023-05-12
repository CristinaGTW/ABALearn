from dataclasses import dataclass, field
from elements.components import Rule, Example, Atom
from prolog.coverage import make_grounded_extension
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
    language: list[str] = field(default_factory=lambda: [])
    grounded_extension: list[str] = None

    def get_grounded_extension(self, prolog):
        if self.grounded_extension == None:
                self.grounded_extension = make_grounded_extension(prolog, self)
        return self.grounded_extension

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

    def set_language(self):
        lang = []
        for r in self.background_knowledge:
            for arg in r.head.arguments:
                if not arg[0].isupper():
                    lang.append(arg)
            for b in r.body:
                if isinstance(b, Atom):
                    for arg in b.arguments:
                        if not arg[0].isupper():
                            lang.append(arg)
                else:
                    if not b.var_1[0].isupper():
                        lang.append(b.var_1)
                    if not b.var_2[0].isupper():
                        lang.append(b.var_2)
        self.language = list(set(lang))

    def _ground_atom(self, arguments, val_map, curr_args, res):
        if len(arguments) == 0:
            val_map.popitem()
            res += [curr_args]
        else:
            if arguments[0][0].isupper():
                if arguments[0] in val_map:
                    self._ground_atom(
                        arguments[1:], val_map, curr_args + [val_map[arguments[0]]], res)
                else:
                    for c in self.language:
                        val_map[arguments[0]] = c
                        self._ground_atom(
                            arguments[1:], val_map, curr_args + [c], res)
            else:
                self._ground_atom(
                    arguments[1:], val_map, curr_args + [arguments[0]], res)

    def _ground_both(self, arguments1, arguments2, val_map, curr_args1, curr_args2, res):
        if len(arguments2) == 0:
            res += [(curr_args1, curr_args2)]
            val_map.popitem()
        elif len(arguments1) > 0:
            if arguments1[0][0].isupper():
                if arguments1[0] in val_map:
                    self._ground_both(
                        arguments1[1:], arguments2, val_map, curr_args1 + [val_map[arguments1[0]]], curr_args2, res)
                else:
                    for c in self.language:
                        val_map[arguments1[0]] = c
                        self._ground_both(
                            arguments1[1:], arguments2, val_map, curr_args1 + [c], curr_args2, res)
            else:
                self._ground_both(
                    arguments1[1:], arguments2, val_map, curr_args1 + [arguments1[0]], curr_args2, res)
        else:
            if arguments2[0][0].isupper():
                if arguments2[0] in val_map:
                    self._ground_both(
                        arguments1, arguments2[1:], val_map, curr_args1, curr_args2 + [val_map[arguments2[0]]], res)
                else:
                    for c in self.language:
                        val_map[arguments2[0]] = c
                        self._ground_both(
                            arguments1, arguments2[1:], val_map, curr_args1, curr_args2+[c], res)
            else:
                self._ground_both(
                    arguments1, arguments2[1:], val_map, curr_args1, curr_args2 + [arguments2[0]], res)

    def _get_pred_and_args(self, s):
        predicate, arguments_str = s[:-1].split("(", 1)
        arguments = arguments_str.split(",")
        count = 0
        var_dict = {}
        arguments = [arg.strip() for arg in arguments]
        has_vars = False
        for idx, arg in enumerate(arguments):
            if "$VAR(" in arg:
                n = int(arg[arg.find("$") + 5: -1])
                var = chr(ord("A") + n)
                arguments[idx] = var
                has_vars = True
            if arg[0] == "_":
                has_vars = True
                if arg in var_dict:
                    var = var_dict[arg]
                else:
                    var = chr(ord("A") + count)
                    var_dict[arg] = var
                    count += 1
                arguments[idx] = var
        arguments = [arg.strip() for arg in arguments]
        return predicate, arguments, has_vars

    def _from_prolog_att_output(self, s1, s2):
        predicate1, arguments1, has_vars1 = self._get_pred_and_args(s1)
        predicate2, arguments2, has_vars2 = self._get_pred_and_args(s2)
    
        if not has_vars1 and not has_vars2:
            normalised1 = predicate1 + '('
            for arg in arguments1:
                normalised1 += arg + ','
            normalised1 = normalised1[:-1]
            normalised1 += ')'
            normalised2 = predicate2 + '('
            for arg in arguments2:
                normalised2 += arg + ','
            normalised2 = normalised2[:-1]
            normalised2 += ')'
            return [(normalised1, normalised2)]
        elif not has_vars1:
            normalised1 = predicate1 + '('
            for arg in arguments1:
                normalised1 += arg + ','
            normalised1 = normalised1[:-1]
            normalised1 += ')'
            normalised = []
            groundings2 = []
            self._ground_atom(arguments2, {}, [], groundings2)
            for gr in groundings2:
                curr = predicate2 + '('
                for arg in gr:
                    curr += arg + ','
                curr = curr[:-1]
                curr += ')'
                normalised.append((normalised1, curr))
            return normalised
        elif not has_vars2:
            normalised2 = predicate2 + '('
            for arg in arguments2:
                normalised2 += arg + ','
            normalised2 = normalised2[:-1]
            normalised2 += ')'
            normalised = []
            groundings1 = []
            self._ground_atom(arguments1, {}, [], groundings1)
            for gr in groundings1:
                curr = predicate1 + '('
                for arg in gr:
                    curr += arg + ','
                curr = curr[:-1]
                curr += ')'
                normalised.append((curr, normalised2))
            return normalised
        else:
            groundings = []
            normalised = []
            self._ground_both(arguments1, arguments2, {}, [], [], groundings)
            for gr1, gr2 in groundings:
                curr1 = predicate1 + '('
                for arg in gr1:
                    curr1 += arg + ','
                curr1 = curr1[:-1]
                curr1 += ')'
                curr2 = predicate2 + '('
                for arg in gr2:
                    curr2 += arg + ','
                curr2 = curr2[:-1]
                curr2 += ')'
                normalised.append((curr1, curr2))
            return normalised

    def _from_prolog_arg_output(self, s: str) -> list[str]:
        predicate, arguments_str = s[:-1].split("(", 1)
        arguments = arguments_str.split(",")
        count = 0
        var_dict = {}
        arguments = [arg.strip() for arg in arguments]
        normalised = []
        has_vars = False
        for idx, arg in enumerate(arguments):
            if "$VAR(" in arg:
                n = int(arg[arg.find("$") + 5: -1])
                var = chr(ord("A") + n)
                arguments[idx] = var
                has_vars = True
            if arg[0] == "_":
                has_vars = True
                if arg in var_dict:
                    var = var_dict[arg]
                else:
                    var = chr(ord("A") + count)
                    var_dict[arg] = var
                    count += 1
                arguments[idx] = var
        arguments = [arg.strip() for arg in arguments]
        if not has_vars:
            normalised = predicate + '('
            for arg in arguments:
                normalised += arg + ','
            normalised = normalised[:-1]
            normalised += ')'
            return [normalised]
        else:
            groundings = []
            self._ground_atom(arguments, {}, [], groundings)
            for gr in groundings:
                curr = predicate + '('
                for arg in gr:
                    curr += arg + ','
                curr = curr[:-1]
                curr += ')'
                normalised.append(curr)
            return normalised

    def aspartix_input(self, prolog, filename):
        input = ''
        query: str = f"findall(A,argument((A,B),Rule), Result)."
        solutions: list[dict] = list(prolog.query(query))
        for sol in solutions:
            for arg in sol['Result']:
                concs = self._from_prolog_arg_output(str(arg))
                for conc in concs:
                    input += 'arg(' + conc + '). \n'

        query: str = f"findall((A,B),attacks((A,A2),(B,B2)), Result)."
        solutions: list[dict] = list(prolog.query(query))
        for sol in solutions:
            for att in sol['Result']:
                att = str(att)[2:-1]
                [att1, att2] = re.split(r',\s*(?=[a-zA-Z])', att)
                atts = self._from_prolog_att_output(att1, att2)
                for (att1, att2) in atts:
                    input += 'att(' + att1 + ',' + att2 + '). \n'
        f = open(filename, "w")
        f.write(input)
        f.close()
        return filename
