from elements.aba_framework import ABAFramework
from elements.components import Rule, Example, Atom


def get_rules(prolog) -> list[Rule]:
    result = list(prolog.query("get_rules(N,H,B)."))
    all_rules = []
    for rule in result:
        body = ""
        for i in range(len(rule["B"])):
            body += str(rule["B"][i]) + ","
        body = body[:-1]
        rule_str = rule["N"] + ":" + rule["H"] + "<-" + body
        all_rules.append(Rule.parse_rule(rule_str))
    return all_rules


def get_positive_examples(prolog) -> list[Example]:
    result: list[dict] = list(prolog.query("pos(N,E)."))
    pos_exs: list[Example] = []
    for ex in result:
        pos_exs.append(Example(ex["N"], Atom.parse_atom(ex["E"])))
    return pos_exs


def get_negative_examples(prolog) -> list[Example]:
    result: list[dict] = list(prolog.query("neg(N,E)."))
    neg_exs: list[Example] = []
    for ex in result:
        neg_exs.append(Example(ex["N"], Atom.parse_atom(ex["E"])))
    return neg_exs


def get_contraries(prolog) -> list[tuple[Atom, Atom]]:
    result: list[dict] = list(prolog.query("contrary(A,B)."))
    contraries: list[tuple[Atom, Atom]] = []
    for contrary in result:
        contraries.append(
            (Atom.parse_atom(contrary["A"]), Atom.parse_atom(contrary["B"]))
        )
    return contraries


def get_assumptions(prolog) -> list[Atom]:
    result: list[dict] = list(prolog.query("my_asm(A)."))
    asms: list[Atom] = []
    for asm in result:
        asms.append(Atom.parse_atom(asm["A"]))
    return asms


def get_con_body_map(prolog) -> dict[str, list[str]]:
    result: list[dict] = list(prolog.query("con_body(C,B)."))
    con_bodies: dict[Atom, list[Atom]] = {}
    for con_body in result:
        con_bodies[Atom.parse_atom(con_body["C"]).predicate] = [
            Atom.parse_atom(str(b)).predicate for b in con_body["B"]
        ]
    return con_bodies


def get_current_aba_framework(prolog, aba_framework) -> ABAFramework:
    rules: list[Rule] = get_rules(prolog)
    pos_exs: list[Example] = get_positive_examples(prolog)
    neg_exs: list[Example] = get_negative_examples(prolog)
    assumptions: list[Atom] = get_assumptions(prolog)
    contraries: list[tuple[Atom, Atom]] = get_contraries(prolog)
    con_body_map: dict[str, list[str]] = get_con_body_map(prolog)
    if aba_framework is not None:
        con_pos_ex_map: dict[str, list[str]] = aba_framework.con_pos_ex_map
        con_neg_ex_map: dict[str, list[str]] = aba_framework.con_neg_ex_map
        aba_framework: ABAFramework = ABAFramework(
            rules, pos_exs, neg_exs, assumptions, contraries, con_body_map, con_pos_ex_map, con_neg_ex_map
        )
    else: 
        aba_framework: ABAFramework = ABAFramework(
            rules, pos_exs, neg_exs, assumptions, contraries, con_body_map, {}, {}
        )

    return aba_framework
