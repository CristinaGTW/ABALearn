from elements.aba_framework import ABAFramework
from elements.components import Rule, Example, Atom

def get_rules(prolog):
    result = list(prolog.query("get_rules(N,H,B)."))
    all_rules = []
    for rule in result:
        body = ""
        for i in range(len(rule['B'])):
            body += str(rule['B'][i]) + ','
        body = body[:-1]
        rule_str = rule['N'] + ':' + rule['H'] + '<-' + body
        all_rules.append(Rule.parse_rule(rule_str))  
    return all_rules

def get_positive_examples(prolog):
    result = list(prolog.query("pos(N,E)."))
    pos_exs = []
    for ex in result:
        pos_exs.append(Example(ex['N'], Atom.parse_atom(ex['E'])))
    return pos_exs

def get_negative_examples(prolog):
    result = list(prolog.query("neg(N,E)."))
    neg_exs = []
    for ex in result:
        neg_exs.append(Example(ex['N'], Atom.parse_atom(ex['E'])))
    return neg_exs

def get_contraries(prolog):
    result = list(prolog.query("contrary(A,B)."))
    contraries = []
    for contrary in result:
        contraries.append((Atom.parse_atom(contrary['A']), Atom.parse_atom(contrary['B'])))
    return contraries


def get_assumptions(prolog):
    result = list(prolog.query("my_asm(A)."))
    asms = []
    for asm in result:
        asms.append(Atom.parse_atom(asm['A']))
    return asms

def get_current_aba_framework(prolog):
    rules = get_rules(prolog)
    pos_exs = get_positive_examples(prolog)
    neg_exs = get_negative_examples(prolog)
    assumptions = get_assumptions(prolog)
    contraries = get_contraries(prolog)
    aba_framework = ABAFramework(rules, pos_exs, neg_exs, assumptions, contraries)
    aba_framework.set_language()
    return aba_framework