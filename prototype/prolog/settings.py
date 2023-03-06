

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