from pyswip import Prolog

def set_up_abalearn():
    prolog = Prolog()
    prolog.consult("prototype/resources/abalearn.pl")
    return prolog


def add_rule(prolog, rule):
    body = ""
    for atom in rule.body:
        body += str(atom) + ","
    body = body[:-1]
    query = f"add_rule({str(rule.head)},{body})."
    list(prolog.query(query))



def add_rule(prolog, rule):
    body = ""
    for atom in rule.body:
        body += str(atom) + ","
    body = body[:-1]
    query = f"add_rule({str(rule.head)},{body})."
    list(prolog.query(query))

def role_learn(prolog,example_id):
    query = f"rote_learn({example_id})."
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
    all_rules = list(prolog.query("get_rules(N,H,B)."))
    all_rules_str = []
    for rule in all_rules:
        rule_str = rule['N'] + ': ' + rule['H'] + '<-' + rule['B']
        all_rules_str.append(rule_str)  
    return all_rules_str

