from pyswip import Prolog
from elements.aba_framework import ABAFramework
from elements.components import Rule, Example, Atom

def set_up_abalearn(input_file_path):
    prolog = Prolog()
    prolog.consult("prototype/resources/abalearn.pl")
    prolog.consult(input_file_path)
    return prolog


def add_rule(prolog, rule):
    body = ""
    for atom in rule.body:
        body += str(atom) + ","
    body = body[:-1]
    query = f"add_rule({str(rule.head)},{body})."
    list(prolog.query(query))

def add_pos_ex(prolog, ex_atom):
    query = f"add_pos({ex_atom})."
    list(prolog.query(query))   

def add_neg_ex(prolog, ex_atom):
    query = f"add_neg({ex_atom})."
    list(prolog.query(query))   

def rem_pos_ex(prolog, ex_id):
    query = f"rem_pos({ex_id})."
    list(prolog.query(query))   

def rem_neg_ex(prolog, ex_id):
    query = f"rem_neg({ex_id})."
    list(prolog.query(query))   

def rem_rule(prolog, rule_id):
    query = f"rem_rule({rule_id})."
    list(prolog.query(query))   


def rote_learn(prolog,example_id):
    query = f"rote_learn({example_id})."
    list(prolog.query(query))

def rote_learn_all(prolog,predicate,arity):
    query = f"rote_learn_all({predicate}/{arity})."
    list(prolog.query(query))

def remove_eq(prolog, rule_id, eq_pos):
    query = f"removeq({rule_id},{eq_pos})."
    list(prolog.query(query))

def fold(prolog, rule_id_1, rule_id_2):
    query = f"fold({rule_id_1},{rule_id_2})."
    list(prolog.query(query))

def undercut(prolog, rule_id, atom_pos):
    query = f"undercut({rule_id},{atom_pos})."
    list(prolog.query(query))

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
    return ABAFramework(rules, pos_exs, neg_exs, assumptions, contraries)