from pyswip import Prolog
from elements.components import Rule

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


def rote_learn(prolog,example_id):
    query = f"rote_learn({example_id})."
    list(prolog.query(query))

def rote_learn_all(prolog,predicate,arity):
    query = f"rote_learn_all({predicate},{arity})."
    list(prolog.query(query))

def remove_eq(prolog, rule_id, eq_pos):
    query = f"removeq({rule_id},{eq_pos})."
    list(prolog.query(query))

def fold(prolog, rule_id_1, rule_id_2):
    query = f"fold({rule_id_1},{rule_id_2})."
    list(prolog.query(query))

def assumption_introduction(prolog, rule_id, atom_pos):
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

def get_current_aba_framework(prolog):
    rules = get_rules(prolog)
