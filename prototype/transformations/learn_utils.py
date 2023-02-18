from pyswip import Prolog

def set_up_abalearn():
    prolog = Prolog()
    prolog.consult("../resources/abalearn.pl")
    return prolog


def add_rule(prolog, rule):
    if rule == "":
        query = "add_rule(bird(X),[penguin(X)])."
    else:
        body = ""
        for atom in rule.body:
            body += str(atom) + ","
        body = body[:-1]
        query = f"add_rule({str(rule.head)},{body})."
    list(prolog.query(query))


def get_rules(prolog):
    all_rules = list(prolog.query("get_rules(N,H,B)."))
    all_rules_str = []
    for rule in all_rules:
        body = ""
        for i in range(len(rule['B'])):
            body += str(rule['B'][i]) + ','
        body = body[:-1]
        rule_str = rule['N'] + ': ' + rule['H'] + '<-' + body
        all_rules_str.append(rule_str)  
    return all_rules_str

if __name__=="__main__":
    prolog = set_up_abalearn()
    add_rule(prolog, "")
    print(get_rules(prolog))