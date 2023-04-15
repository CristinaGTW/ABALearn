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
