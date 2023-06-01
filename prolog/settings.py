from elements.components import Example, Rule, Atom


def add_rule(prolog, rule: Rule) -> None:
    body = ""
    for atom in rule.body:
        body += str(atom) + ","
    body = body[:-1]
    query = f"add_rule({str(rule.head)},{body})."
    q = list(prolog.query(query))
    del q


def add_pos_ex(prolog, aba_framework, ex_atom: Atom) -> None:
    query = f"add_pos({ex_atom},N)."
    q = list(prolog.query(query))
    result = list(prolog.query(query))[0]
    aba_framework.positive_examples[result['N']] = Example(result['N'], ex_atom)
    del q


def add_neg_ex(prolog, aba_framework, ex_atom: Atom) -> None:
    query = f"add_neg({ex_atom},N)."
    result = list(prolog.query(query))[0]
    aba_framework.negative_examples[result['N']] = Example(result['N'], ex_atom)


def rem_pos_ex(prolog, aba_framework, ex_id: str) -> None:
    query = f"rem_pos({ex_id})."
    list(prolog.query(query))
    aba_framework.positive_examples.pop(ex_id)

def rem_neg_ex(prolog, aba_framework, ex_id: str) -> None:
    query = f"rem_neg({ex_id})."
    list(prolog.query(query))
    aba_framework.negative_examples.pop(ex_id)

def rem_rule(prolog, rule_id: str) -> None:
    query = f"rem_rule({rule_id})."
    q = list(prolog.query(query))
    del q

def unfold_and_replace(prolog, aba_framework, rule: Rule) -> Rule:
    new_rule = rule.extract_eqs()
    query = f"rem_rule({rule.rule_id})."
    list(prolog.query(query))
    query = f"assertz({new_rule.to_prolog()[:-1]})."
    list(prolog.query(query))
    aba_framework.background_knowledge[rule.rule_id] = new_rule
    return new_rule


def set_framework(prolog, aba_framework) -> None:
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

    for rule_id in aba_framework.background_knowledge:
        rule = aba_framework.background_knowledge[rule_id]
        query = f"assertz({rule.to_prolog()[:-1]})."
        list(prolog.query(query))

    for contrary in aba_framework.contraries:
        query = f"assertz({contrary[0].to_prolog_contrary(contrary[1])[:-1]})."
        list(prolog.query(query))

    for assumption in aba_framework.assumptions:
        query = f"assertz({assumption.to_prolog_asm()[:-1]})."
        list(prolog.query(query))

    for pos in aba_framework.positive_examples.values():
        query = f"assertz({pos.to_prolog_pos()[:-1]})."
        list(prolog.query(query))

    for neg in aba_framework.negative_examples.values():
        query = f"assertz({neg.to_prolog_neg()[:-1]})."
        list(prolog.query(query))