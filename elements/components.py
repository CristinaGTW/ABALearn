from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class Atom:
    predicate: str
    arguments: list[str]

    def parse_atom(input: str) -> Atom:
        predicate, arguments_str = input[:-1].split("(", 1)
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
        return Atom(predicate, arguments)

    def __str__(self):
        args_str = ""
        for a in self.arguments:
            args_str += a + ","
        args_str = args_str[:-1]
        return self.predicate + "(" + args_str + ")"

    def to_prolog_asm(self) -> str:
        return f"my_asm({self})."

    def to_prolog_contrary(self, c_atom) -> str:
        return f"contrary({self},{c_atom})."


@dataclass
class Rule:
    rule_id: str
    head: Atom
    body: list[Atom | Equality]

    def _split_body(body: str) -> list[str]:
        result = []

        start = 0
        level = 0
        for i in range(len(body)):
            if body[i] == "," and level == 0:
                result.append(body[start:i])
                start = i + 1
            elif body[i] == "(":
                level += 1
            elif body[i] == ")":
                level -= 1

        result.append(body[start:])
        return result

    def parse_rule(input: str) -> Rule:
        (rule_id, _, rule_def) = input.partition(":")
        (head_str, _, body_str) = rule_def.partition("<-")
        head = Atom.parse_atom(head_str)
        splits = Rule._split_body(body_str)
        body = []
        for b in splits:
            if b[0] == "=":
                vars = b[2:-1].split(",")
                var_1 = vars[0].strip()
                var_2 = vars[1].strip()
                if "$VAR(" in var_1:
                    n = int(var_1[5:-1])
                    var_1 = chr(ord("A") + n)
                if "$VAR(" in var_2:
                    n = int(var_2[5:-1])
                    var_2 = chr(ord("A") + n)
                body.append(Equality(var_1, var_2))
            elif "=" in b:
                body.append(Equality.parse_equality(b))
            else:
                body.append(Atom.parse_atom(b))
        return Rule(rule_id, head, body)

    def has_constants(self):
        for b in self.body:
            if isinstance(b,Atom):
                if any([not arg[0].isupper() for arg in b.arguments]):
                    return True
        return False


    def extract_eqs(self):
        new_rule = deepcopy(self)

        body_str = ""
        all_vars = []
        for a in self.head.arguments:
            if a[0].isupper():
                all_vars.append(a)
        for b in self.body:
            if isinstance(b,Atom):
                for a in b.arguments:
                    if a[0].isupper():
                        all_vars.append(a)
            if isinstance(b,Equality):
                if b.var_1[0].isupper():
                    all_vars.append(b.var_1)
                if b.var_2[0].isupper():
                    all_vars.append(b.var_2)
        all_vars.sort()

        for i,x in enumerate(self.body):
            if isinstance(x,Atom):
                for idx,arg in enumerate(x.arguments):
                    if arg[0].islower() or arg[0].isdigit():
                        next_chr = chr(ord(all_vars[-1]) + 1)
                        all_vars.append(next_chr)
                        new_rule.body.append(Equality(next_chr,arg))
                        new_rule.body[i].arguments[idx]=next_chr
        return new_rule


    def get_equalities(self) -> list[Equality]:
        eqs: list[Equality] = []
        for b in self.body:
            if isinstance(b, Equality):
                eqs.append(b)
        return eqs

    def get_atoms(self) -> list[Atom]:
        atoms: list[Atom] = []
        for b in self.body:
            if isinstance(b, Atom):
                atoms.append(b)
        return atoms

    def get_vars(self) -> set[str]:
        vars: list[str] = []
        for x in self.head.arguments:
            if x[0].isupper():
                vars.append(x)
        for b in self.body:
            if isinstance(b, Atom):
                for x in b.arguments:
                    if x[0].isupper():
                        vars.append(x)
            else:
                assert isinstance(b, Equality)
                if b.var_1[0].isupper():
                    vars.append(b.var_1)
                if b.var_2[0].isupper():
                    vars.append(b.var_2)
        return set(vars)

    def to_prolog(self) -> str:
        body_str = ""
        for x in self.body:
            body_str += str(x) + ","
        body_str = body_str[:-1]
        res = f"my_rule({self.rule_id},{self.head},[{body_str}])."
        return res

    def __str__(self):
        body_str = ""
        for atom in self.body:
            body_str += str(atom) + ","

        return self.rule_id + ":" + str(self.head) + "<-" + body_str[:-1]

    def __hash__(self):
        return hash(self.rule_id)


@dataclass
class Example:
    example_id: str
    fact: Atom

    def get_predicate(self) -> str:
        return self.fact.predicate

    def get_arguments(self) -> list[str]:
        return self.fact.arguments

    def get_arity(self) -> int:
        return len(self.fact.arguments)

    def to_prolog_pos(self) -> str:
        return f"pos({self.example_id},{self.fact})."

    def to_prolog_neg(self) -> str:
        return f"neg({self.example_id},{self.fact})."

    def __str__(self):
        return self.example_id + ":" + str(self.fact)

    def __hash__(self):
        return hash(self.example_id)


    def __eq__(self, obj):
        return isinstance(obj, Example) and obj.fact == self.fact

@dataclass
class Equality:
    var_1: str
    var_2: str

    def parse_equality(input: str) -> Equality:
        var_1, _, var_2 = input.partition("=")
        return Equality(var_1, var_2)

    def __str__(self):
        return self.var_1 + "=" + self.var_2
