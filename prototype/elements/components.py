from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Atom:
    predicate: str
    arguments: list[str]

    def parse_atom(input: str) -> Atom:
        predicate, arguments_str = input[:-1].split("(",1)
        arguments = arguments_str.split(",")
        return Atom(predicate, arguments) 

    def __str__(self):
        args_str = ""
        for a in self.arguments:
            args_str += a + ","
        args_str = args_str[:-1]
        return self.predicate + "(" + args_str + ")"

    def to_prolog_asm(atom):
        return f"my_asm({atom})."

    def to_prolog_contrary(atom,c_atom):
        return f"contrary({atom},{c_atom})."

@dataclass
class Rule:
    rule_id: str
    head: Atom
    body: list[Atom|Equality]

    
    def parse_rule(input: str) -> Rule:
        (rule_id,_,rule_def) = input.partition(":")
        (head_str,_,body_str) = rule_def.partition("<-")
        head = Atom.parse_atom(head_str)
        print(body_str)
        splits = body_str.split(",")
        body = []
        skip = False
        for i in range(len(splits)):
            if skip:
                skip = False
                continue
            if splits[i][0] == '=':
                body.append(Equality(splits[i][2:], splits[i+1][:-1]))
                skip = True
            elif '=' in splits[i]:
                body.append(Equality.parse_equality(splits[i]))
            else:
                body.append(Atom.parse_atom(splits[i]))
        return Rule(rule_id, head, body)

    def to_prolog(self) -> str:
        body_str = ""
        for x in self.body:
            body_str += str(x) + ','
        body_str = body_str[:-1]
        res = f"my_rule({self.rule_id},{self.head},[{body_str}])."
        return res

    def __str__(self):
        body_str = ""
        for atom in self.body:
            body_str += str(atom) + ","

        return self.rule_id + ":" + str(self.head) + "<-" + body_str[:-1]

@dataclass
class Example:
    example_id: str
    fact: Atom

    def get_predicate(self):
        return self.fact.predicate

    def get_arity(self):
        return len(self.fact.arguments)

    def parse_example(input: str) -> Example:
        example_id,_,example_def = input.partition(":")
        fact = Atom.parse_atom(example_def)
        return Example(example_id, fact)

    def to_prolog_pos(self):
        return f"pos({self.example_id},{self.fact})."
    
    def to_prolog_neg(self):
        return f"neg({self.example_id},{self.fact})."

    def __str__(self):
        return self.example_id + ":" + str(self.fact)

@dataclass
class Equality:
    var_1: str
    var_2: str

    def parse_equality(input:str) -> Equality:
        var_1,_,var_2 = input.partition("=")
        return Equality(var_1, var_2)

    def __str__(self):
        return self.var_1 + "=" + self.var_2