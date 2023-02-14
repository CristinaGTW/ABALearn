from dataclasses import dataclass

rule_counter = 0
example_counter = 0

@dataclass
class Atom:
    predicate: str
    arguments: list[str]

    def parse_atom(input: str) -> Atom:
        predicate, arguments_str = input[:-1].split("(")
        arguments = arguments_str.split(",")
        return Atom(predicate, arguments) 

@dataclass
class Rule:
    rule_id: str
    head: Atom
    body: list[Atom]

    
    def parse_rule(input: str) -> Rule:
        (head_str,_, body_str) = input.partition("<-")
        head = parse_atom(head_str)
        body = [parse_atom(x) for x in body_str.split(",")]
        rule_counter += 1
        rule_id = "r_" + str(rule_counter)
        return Rule(rule_id, head, body)
    

@dataclass
class Example:
    example_id: str
    fact: Atom

    
    def parse_example(input: str) -> Example:
        fact = parse_atom(input)
        example_counter += 1
        example_id = "r_" + str(example_counter)
        return Example(example_id, fact)

