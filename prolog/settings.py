from elements.components import Rule, Atom


def add_rule(prolog, rule: Rule) -> None:
    body = ""
    for atom in rule.body:
        body += str(atom) + ","
    body = body[:-1]
    query = f"add_rule({str(rule.head)},{body})."
    q = list(prolog.query(query))
    del q
    print(f"Added rule {rule}")


def add_pos_ex(prolog, ex_atom: Atom) -> None:
    query = f"add_pos({ex_atom})."
    q = list(prolog.query(query))
    del q
    print(f"Added positive example {ex_atom}")


def add_neg_ex(prolog, ex_atom: Atom) -> None:
    query = f"add_neg({ex_atom})."
    q = list(prolog.query(query))
    del q
    print(f"Added negative example {ex_atom}")


def rem_pos_ex(prolog, ex_id: str) -> None:
    query = f"rem_pos({ex_id})."
    q = list(prolog.query(query))
    del q

def rem_neg_ex(prolog, ex_id: str) -> None:
    query = f"rem_neg({ex_id})."
    q = list(prolog.query(query))
    del q

def rem_rule(prolog, rule_id: str) -> None:
    query = f"rem_rule({rule_id})."
    q = list(prolog.query(query))
    del q

def unfold_and_replace(prolog, rule: Rule) -> Rule:
    new_rule = rule.extract_eqs()
    query = f"rem_rule({rule.rule_id})."
    q = list(prolog.query(query))
    query = f"assertz({new_rule.to_prolog()[:-1]})."
    q =list(prolog.query(query))
    del q
    return new_rule


def restore_framework(prolog, aba_framework) -> None:
    query = "retractall(my_rule(_,_,_))."
    q = list(prolog.query(query))
    del q
    query = "retractall(contrary(_,_))."
    q = list(prolog.query(query))
    del q
    query = "retractall(my_asm(_))."
    q = list(prolog.query(query))
    del q
    query = "retractall(pos(_,_))."
    q = list(prolog.query(query))
    del q
    query = "retractall(neg(_,_))."
    q = list(prolog.query(query))
    del q

    for rule in aba_framework.background_knowledge:
        query = f"assertz({rule.to_prolog()[:-1]})."
        q =list(prolog.query(query))
        del q

    for contrary in aba_framework.contraries:
        query = f"assertz({contrary[0].to_prolog_contrary(contrary[1])[:-1]})."
        q = list(prolog.query(query))
        del q

    for assumption in aba_framework.assumptions:
        query = f"assertz({assumption.to_prolog_asm()[:-1]})."
        q = list(prolog.query(query))
        del q

    for pos in aba_framework.positive_examples:
        query = f"assertz({pos.to_prolog_pos()[:-1]})."
        q = list(prolog.query(query))
        del q

    for neg in aba_framework.negative_examples:
        query = f"assertz({neg.to_prolog_neg()[:-1]})."
        q = list(prolog.query(query))
        del q
