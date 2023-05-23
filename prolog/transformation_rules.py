from elements.components import Rule

def rote_learn(prolog, example_id):
    query = f"rote_learn({example_id})."
    q = list(prolog.query(query))
    del q


def rote_learn_all(prolog, predicate, arity):
    query = f"rote_learn_all({predicate}/{arity})."
    q= list(prolog.query(query))
    del q


def remove_eq(prolog, rule_id, eq_pos):
    query = f"removeq({rule_id},{eq_pos},(R,H,B))."
    result = list(prolog.query(query))[0]
    new_rule_id = str(result['R'])
    body = ""
    for i in range(len(result["B"])):
        body += str(result["B"][i]) + ","
    body = body[:-1]
    rule_str = new_rule_id + ':' + result['H'] + '<-' + body
    new_rule = Rule.parse_rule(rule_str)
    
    return new_rule



def fold(prolog,rule_id_1, rule_id_2, update = True):
    query = f"fold({rule_id_1},{rule_id_2},(R,H,B))."
    result = list(prolog.query(query))[0]
    body = ""
    for i in range(len(result["B"])):
        body += str(result["B"][i]) + ","
    body = body[:-1]
    rule_id = result['R']
    rule_str = rule_id + ':' + result['H'] + '<-' + body
    new_rule = Rule.parse_rule(rule_str)
    return new_rule


def foldable(prolog, rule_id_1, rule_id_2) -> bool:
    query = f"foldable({rule_id_1},{rule_id_2},S)."
    result = list(prolog.query(query))
    return result != []


def undercut(prolog, rule_id, atom_pos):
    query = f"undercut({rule_id},{atom_pos})."
    q =list(prolog.query(query))
    del q

def gen_eqs(prolog, rule_id):
    query = f"geneqs({rule_id})."
    q = list(prolog.query(query))
    del q