def rote_learn(prolog, example_id):
    query = f"rote_learn({example_id})."
    list(prolog.query(query))


def rote_learn_all(prolog, predicate, arity):
    query = f"rote_learn_all({predicate}/{arity})."
    list(prolog.query(query))


def remove_eq(prolog, rule_id, eq_pos):
    query = f"removeq({rule_id},{eq_pos})."
    list(prolog.query(query))


def fold(prolog, rule_id_1, rule_id_2):
    query = f"fold({rule_id_1},{rule_id_2})."
    list(prolog.query(query))


def foldable(prolog, rule_id_1, rule_id_2) -> bool:
    query = f"foldable({rule_id_1},{rule_id_2},S)."
    result = list(prolog.query(query))
    return result != []


def undercut(prolog, rule_id, atom_pos):
    query = f"undercut({rule_id},{atom_pos})."
    list(prolog.query(query))
