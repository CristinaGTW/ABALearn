from elements.components import Atom, Rule


def rote_learn(prolog, example_id):
    query = f"rote_learn({example_id})."
    q = list(prolog.query(query))
    del q


def rote_learn_all(prolog, aba_framework, predicate, arity):
    query = f"rote_learn_all({predicate}/{arity},(R,H,B))."
    result = list(prolog.query(query))
    new_rules = []
    for rule in result:
        body = ""
        for i in range(len(rule["B"])):
            body += str(rule["B"][i]) + ","
        body = body[:-1]
        rule_str = rule["R"] + ":" + rule["H"] + "<-" + body
        new_rule = Rule.parse_rule(rule_str)
        new_rules.append(new_rule)
        aba_framework.background_knowledge[new_rule.rule_id] = new_rule
    return new_rules


def remove_eq(prolog, aba_framework, rule_id, eq_pos):
    query = f"removeq({rule_id},{eq_pos},(R,H,B))."
    result = list(prolog.query(query))[0]
    new_rule_id = str(result["R"])
    body = ""
    for i in range(len(result["B"])):
        body += str(result["B"][i]) + ","
    body = body[:-1]
    rule_str = new_rule_id + ":" + result["H"] + "<-" + body
    new_rule = Rule.parse_rule(rule_str)
    aba_framework.background_knowledge.pop(rule_id)
    aba_framework.background_knowledge[new_rule_id] = new_rule

    return new_rule


def fold(prolog, aba_framework, rule_id_1, rule_id_2) -> Rule:
    query = f"fold({rule_id_1},{rule_id_2},(R,H,B))."
    result = list(prolog.query(query))[0]
    body = ""
    for i in range(len(result["B"])):
        body += str(result["B"][i]) + ","
    body = body[:-1]
    rule_id = result["R"]
    rule_str = rule_id + ":" + result["H"] + "<-" + body
    new_rule = Rule.parse_rule(rule_str)
    aba_framework.background_knowledge[rule_id] = new_rule
    aba_framework.background_knowledge.pop(rule_id_1)
    return new_rule


def foldable(prolog, rule_1, rule_2, safe=True) -> bool:
    if safe:
        if rule_1.head.predicate == rule_2.head.predicate:
            return False
    query = f"foldable({rule_1.rule_id},{rule_2.rule_id},S)."
    result = list(prolog.query(query))
    return result != []


def undercut(prolog, aba_framework, rule_id, atom_pos):
    query = f"undercut({rule_id},{atom_pos},(R1,H,B1,Asm,CAsm,B))."
    result = list(prolog.query(query))[0]
    body = ""
    for i in range(len(result["B1"])):
        body += str(result["B1"][i]) + ","
    body = body[:-1]
    new_rule_id = result["R1"]
    rule_str = new_rule_id + ":" + result["H"] + "<-" + body
    new_rule = Rule.parse_rule(rule_str)
    aba_framework.background_knowledge[new_rule_id] = new_rule
    aba_framework.background_knowledge.pop(rule_id)
    con = Atom.parse_atom(str(result["CAsm"]))
    asm = Atom.parse_atom(str(result["Asm"]))
    aba_framework.assumptions.append(asm)
    aba_framework.contraries.append((asm, con))
    aba_framework.con_body_map[con.predicate] = [
        Atom.parse_atom(str(b)).predicate for b in result["B"]
    ]


def gen_eqs(prolog, aba_framework, rule_id):
    query = f"geneqs({rule_id}, H, B, (R1,B1))."
    result = list(prolog.query(query))
    if len(result) > 0:
        result = result[0]
        body = ""
        for i in range(len(result["B1"])):
            body += str(result["B1"][i]) + ","
        body = body[:-1]
        new_rule_id = result["R1"]
        rule_str = new_rule_id + ":" + result["H"] + "<-" + body
        new_rule = Rule.parse_rule(rule_str)
        aba_framework.background_knowledge.pop(rule_id)
        aba_framework.background_knowledge[new_rule_id] = new_rule
        return new_rule
    return None
