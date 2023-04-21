from elements.components import Rule, Atom


def add_rule(prolog, rule: Rule) -> None:
    body = ""
    for atom in rule.body:
        body += str(atom) + ","
    body = body[:-1]
    query = f"add_rule({str(rule.head)},{body})."
    list(prolog.query(query))
    print(f"Added rule {rule}")


def add_pos_ex(prolog, ex_atom: Atom) -> None:
    query = f"add_pos({ex_atom})."
    list(prolog.query(query))
    print(f"Added positive example {ex_atom}")


def add_neg_ex(prolog, ex_atom: Atom) -> None:
    query = f"add_neg({ex_atom})."
    list(prolog.query(query))
    print(f"Added negative example {ex_atom}")


def rem_pos_ex(prolog, ex_id: str) -> None:
    query = f"rem_pos({ex_id})."
    list(prolog.query(query))


def rem_neg_ex(prolog, ex_id: str) -> None:
    query = f"rem_neg({ex_id})."
    list(prolog.query(query))


def rem_rule(prolog, rule_id: str) -> None:
    query = f"rem_rule({rule_id})."
    list(prolog.query(query))


def restore_framework(prolog, aba_framework) -> None:
    query = "retractall(my_rule(_,_,_))."
    list(prolog.query(query))
    query = "retractall(contrary(_,_))."
    list(prolog.query(query))
    query = "retractall(my_asm(_))."
    list(prolog.query(query))
    query = "retractall(pos(_,_))."
    list(prolog.query(query))
    query = "retractall(neg(_,_))."
    list(prolog.query(query))

    for rule in aba_framework.background_knowledge:
        query = f"assertz({rule.to_prolog()[:-1]})."
        list(prolog.query(query))

    for contrary in aba_framework.contraries:
        query = f"assertz({contrary[0].to_prolog_contrary(contrary[1])[:-1]})."
        list(prolog.query(query))

    for assumption in aba_framework.assumptions:
        query = f"assertz({assumption.to_prolog_asm()[:-1]})."
        list(prolog.query(query))

    for pos in aba_framework.positive_examples:
        query = f"assertz({pos.to_prolog_pos()[:-1]})."
        list(prolog.query(query))

    for neg in aba_framework.negative_examples:
        query = f"assertz({neg.to_prolog_neg()[:-1]})."
        list(prolog.query(query))
