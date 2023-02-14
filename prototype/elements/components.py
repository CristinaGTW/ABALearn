from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Atom:
    predicate: str
    arguments: list[str]

    def parse_atom(input: str) -> Atom:
        predicate, arguments_str = input[:-1].split("(")
        arguments = arguments_str.split(",")
        return Atom(predicate, arguments) 

    def __str__(self):
        args_str = ""
        for a in self.arguments:
            args_str += a + ","
        args_str = args_str[:-1]
        return self.predicate + "(" + args_str + ")"


@dataclass
class Rule:
    rule_id: str
    head: Atom
    body: list[Atom]

    
    def parse_rule(input: str) -> Rule:
        (rule_id,_,rule_def) = input.partition(":")
        (head_str,_,body_str) = rule_def.partition("<-")
        head = Atom.parse_atom(head_str)
        body = [Atom.parse_atom(x) for x in body_str.split(",")]
        return Rule(rule_id, head, body)


    def __str__(self):
        body_str = ""
        for atom in self.body:
            body_str += str(atom) + ","

        return self.rule_id + ":" + str(self.head) + "<-" + body_str[:-1]

@dataclass
class Example:
    example_id: str
    fact: Atom

    
    def parse_example(input: str) -> Example:
        example_id,_,example_def = input.partition(":")
        fact = Atom.parse_atom(example_def)
        return Example(example_id, fact)

    
    def __str__(self):
        return self.example_id + ":" + str(self.fact)
