from elements.components import Rule, Atom

def add_rule(prolog, rule:Rule) -> None:
    body = ""
    for atom in rule.body:
        body += str(atom) + ","
    body = body[:-1]
    query = f"add_rule({str(rule.head)},{body})."
    list(prolog.query(query))
    print(f"Added rule {rule}")

def add_pos_ex(prolog, ex_atom:Atom) -> None:
    query = f"add_pos({ex_atom})."
    list(prolog.query(query))   
    print(f"Added positive example {ex_atom}")

def add_neg_ex(prolog, ex_atom:Atom) -> None:
    query = f"add_neg({ex_atom})."
    list(prolog.query(query))   
    print(f"Added negative example {ex_atom}")

def rem_pos_ex(prolog, ex_id:str) -> None:
    query = f"rem_pos({ex_id})."
    list(prolog.query(query))   
    print(f"Removed positive example {ex_id}")

def rem_neg_ex(prolog, ex_id:str) -> None:
    query = f"rem_neg({ex_id})."
    list(prolog.query(query))   
    print(f"Removed negative example {ex_id}")

def rem_rule(prolog, rule_id:str) -> None:
    query = f"rem_rule({rule_id})."
    list(prolog.query(query))  


def adjust_for_coverage(prolog, aba_framework) -> list[str]:
    modified_rules:list[str] = []
    for rule in aba_framework.background_knowledge:
        (parsed_rule, modified) = rule.substitute_eqs()  
        if modified:
            modified_rules.append(rule.rule_id)
            rem_rule(prolog, rule.rule_id)
            list(prolog.query(f"assert({parsed_rule[:-1]}).")) 
    return modified_rules

def restore_prolog(prolog, aba_framework, modified_rules) -> None:
    for rule_id in modified_rules:
        rem_rule(prolog, rule_id)
    
    for rule in aba_framework.background_knowledge:
        if rule.rule_id in modified_rules:
            list(prolog.query(f"assert({rule.to_prolog(True)[:-1]})."))