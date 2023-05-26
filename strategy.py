from prolog.coverage import covered, get_covered_solutions, count_neg_covered, get_top_rule, make_grounded_extension
from prolog.transformation_rules import (
    rote_learn_all,
    undercut,
    fold,
    remove_eq,
    foldable,
    gen_eqs,
)
from prolog.settings import (
    add_pos_ex,
    add_neg_ex,
    rem_pos_ex,
    rem_neg_ex,
    rem_rule,
    set_framework,
    unfold_and_replace,
)
from prolog.info import get_rules, get_current_aba_framework
from prolog.config import set_up_abalearn
from elements.aba_framework import ABAFramework
from elements.components import Atom, Equality, Example, Rule
from exceptions.abalearn import CredulousSemanticsException, InvalidRuleBodyException
import sys
from copy import deepcopy

NO_PROGRESS_COUNT = 0
# If all positive examples in the given framework are covered, return True
# Otherwise, return False.
def complete(prolog, aba_framework,pos_ex: list[Example]) -> bool:
    return covered(prolog, aba_framework,pos_ex)

# If all negative examples in the given framework are NOT covered, return True
# Otherwise, return False.
def consistent(prolog, aba_framework, neg_ex: list[Example]) -> bool:
    return not any([covered(prolog, aba_framework,[ex]) for ex in neg_ex])


def get_solutions(prolog, aba_framework, rule: Rule) -> list[tuple[str, ...]]:
    if all([arg[0].islower() or arg[0].isdigit() for arg in rule.head.arguments]):
        return [tuple(rule.head.arguments)]
    replace_args = []
    for eq in rule.body:
        if isinstance(eq, Equality):
            replace_args = [
                arg if arg != eq.var_1 else eq.var_2 for arg in rule.head.arguments
            ]
    if (
        all([arg[0].islower() or arg[0].isdigit() for arg in replace_args])
        and len(replace_args) > 0
    ):
        return [tuple(replace_args)]

    sols = get_covered_solutions(prolog, aba_framework,rule.head)
    sols = [tuple(sol.values()) for sol in sols]
    return sols


def further_generalisation(
    prolog, aba_framework: ABAFramework, predicate: str
):
    print("Attempting to further generalise...")
    new_vars_allowed = 0
    folded = True
    new_rules = aba_framework.get_new_rules()
    while folded:
        rules = deepcopy(new_rules)
        folded = False
        for rule_1 in rules:
            if folded == True:
                break
            for rule_2 in rules:
                if rule_1.head.predicate == predicate:
                    if foldable(prolog, rule_1.rule_id, rule_2.rule_id) and not check_loop(
                        aba_framework, predicate, rule_2
                    ):
                        prev_framework = deepcopy(aba_framework)
                        new_rule = fold(
                            prolog,
                            aba_framework,
                            rule_1.rule_id,
                            rule_2.rule_id,
                            update=False,
                        )

                        if count_new_vars(new_rule, rule_1, rule_2) > new_vars_allowed:
                            set_framework(prolog, prev_framework)
                            aba_framework = prev_framework
                        else:
                            print(f"Folding rule {rule_1} with rule {rule_2}")
                            new_rules.pop(rule_1.rule_id)
                            new_rules[new_rule.rule_id] = new_rule
                            folded = True
                            break

    return aba_framework


def find_top_rule(prolog, aba_framework: ABAFramework, ex: Example) -> list[Rule]:
    top_rule_ids = get_top_rule(prolog, ex.fact)
    top_rules = []
    for rule_id, rule in aba_framework.background_knowledge.items():
        if rule_id in top_rule_ids:
            top_rules.append(rule)
    return top_rules

def remove_subsumed(
    prolog, aba_framework: ABAFramework, new_rules: list[Rule], target
) -> ABAFramework:
    rules = deepcopy(aba_framework.background_knowledge)
    for rule_id,rule in rules.items():
        if rule.head.predicate == target:
            sols = get_solutions(prolog,aba_framework, rule)
            rem_rule(prolog, rule.rule_id)
            aba_framework.grounded_extension = make_grounded_extension(prolog, aba_framework)
            sols_without_rule = get_covered_solutions(prolog, aba_framework,rule.head)
            sols_without_rule = [tuple(sol.values()) for sol in sols_without_rule]
            if set(sols).issubset(set(sols_without_rule)) and len(sols) > 0:
                aba_framework.background_knowledge.pop(rule_id)
                print(f"Removing rule {rule} as it is subsumed by some other rule")
            else:
                list(prolog.query(f"assertz({rule.to_prolog()[:-1]})."))
    return get_current_aba_framework(prolog, aba_framework)


def find_justified_groundings(
    prolog,
    aba_framework,
    curr_groundings: dict,
    body: list[Atom | Equality],
    body_copy: list[Atom | Equality],
    result: list[list[Atom]],
) -> list[list[Atom]]:
    for i, b in enumerate(body):
        if isinstance(b, Atom):
            needs_check = False
            for j, arg in enumerate(b.arguments):
                if arg in curr_groundings.keys():
                    body_copy[i].arguments[j] = curr_groundings[arg]
                elif arg[0].isupper():
                    needs_check = True
            if needs_check:
                sols = get_covered_solutions(prolog, aba_framework,body_copy[i])

                for sol in sols:
                    for var in sol:
                        curr_groundings[var] = sol[var]
                    result += find_justified_groundings(
                        prolog,
                        aba_framework,
                        curr_groundings,
                        body_copy[i:],
                        deepcopy(body_copy)[i:],
                        result,
                    )
        if isinstance(b, Equality):
            if b.var_1 in curr_groundings.keys():
                if b.var_2[0].islower() or b.var_2[0].isdigit():
                    assert curr_groundings[b.var_1] == b.var_2
                else:
                    if b.var_2 in curr_groundings.keys():
                        assert curr_groundings[b.var_1] == curr_groundings[b.var_2]
                    else:
                        curr_groundings[b.var_2] = curr_groundings[b.var_1]
            else:
                if b.var_2 in sol.keys():
                    curr_groundings[b.var_1] = curr_groundings[b.var_2]
                elif b.var_2[0].islower() or b.var_2[0].isdigit():
                    curr_groundings[b.var_1] = b.var_2
                else:
                    raise InvalidRuleBodyException(
                        f"Body {body} isn't constructed correctly."
                    )
    for b in body_copy:
        if isinstance(b, Atom):
            if not covered(prolog, aba_framework,[Example("fake_ex", b)]):
                return result
            if any([a[0].isupper() for a in b.arguments]):
                return result
    return result + [body_copy]


def get_constants(
    prolog,
    aba_framework,
    top_rule: Rule,
    cov_pos_ex: list[Example],
    cov_neg_ex: list[Example],
    idxs: list[int],
) -> tuple[list[list[str]], list[list[str]]]:
    pos_ex_consts = []
    neg_ex_consts = []
    head_sol: list[dict] = get_covered_solutions(prolog, aba_framework,top_rule.head)
    pos_ex_sols: list[dict] = []
    neg_ex_sols: list[dict] = []

    for sol in head_sol:
        if (
            list(sol.values()) in [ex.get_arguments() for ex in cov_pos_ex]
            and sol not in pos_ex_sols
        ):
            pos_ex_sols.append(sol)
        if (
            list(sol.values()) in [ex.get_arguments() for ex in cov_neg_ex]
            and sol not in neg_ex_sols
        ):
            neg_ex_sols.append(sol)
    for sol in pos_ex_sols:
        body_copy: list[Atom | Equality] = deepcopy(top_rule.body)
        grounded_bodies = find_justified_groundings(
            prolog, aba_framework,sol, top_rule.body, body_copy, []
        )
        for grounded_body in grounded_bodies:
            curr_sol = []
            for i in idxs:
                for a in grounded_body[i].arguments:
                    curr_sol.append(a)
            if curr_sol not in pos_ex_consts:
                pos_ex_consts.append(curr_sol)
    for sol in neg_ex_sols:
        body_copy: list[Atom | Equality] = deepcopy(top_rule.body)
        grounded_bodies = find_justified_groundings(
            prolog, aba_framework,sol, top_rule.body, body_copy, []
        )
        for grounded_body in grounded_bodies:
            curr_sol = []
            for i in idxs:
                for a in grounded_body[i].arguments:
                    curr_sol.append(a)
            if curr_sol not in neg_ex_consts:
                neg_ex_consts.append(curr_sol)

    return (pos_ex_consts, neg_ex_consts)


# Selects as target the examples whose predicate has most occurrences
def select_target(exs: list[Example], learned: list[Example]) -> Example | None:
    counter_dict: dict[str, int] = {}
    max_count = -1
    if len(exs) > 0:
        most_common_pred: Example = exs[0]
        learned_predicates = [ex.get_predicate() for ex in learned]
        for ex in exs:
            counter_dict[ex.get_predicate()] = (
                counter_dict.get(ex.get_predicate(), 0) + 1
            )
            if (
                counter_dict[ex.get_predicate()] > max_count
                and ex.get_predicate() not in learned_predicates
            ):
                max_count = counter_dict[ex.get_predicate()]
                most_common_pred = ex
    if max_count == -1:
        return None
    return most_common_pred


def generate_rules(prolog, aba_framework, ex: Example) -> ABAFramework:
    print(
        f'Applying "Rote Learning" to build rules for the predicate {ex.get_predicate()}.'
    )
    rote_learn_all(prolog, ex.get_predicate(), ex.get_arity())
    aba_framework = get_current_aba_framework(prolog, aba_framework)
    # Generalise equalities if possible
    for rule_id in aba_framework.background_knowledge:
        gen_eqs(prolog, rule_id)
    aba_framework = get_current_aba_framework(prolog, aba_framework)
    aba_framework.grounded_extension = make_grounded_extension(prolog, aba_framework)
    return aba_framework


def same_bodies(body_1, body_2):
    if len(body_1) != len(body_2):
        return False
    for b1, b2 in zip(body_1, body_2):
        if isinstance(b1, Atom) and isinstance(b2, Atom):
            if b1.predicate != b2.predicate:
                return False
        elif isinstance(b1, Equality) and isinstance(b2, Equality):
            if b1 != b2:
                return False
        else:
            return False
    return True

def keep_unique_rules(prolog, aba_framework, rules):
    removed_rules = []
    length = len(rules)
    i = 0
    while i < length - 1:
        j = i + 1
        while j < length:
            if rules[i].head == rules[j].head and same_bodies(
                rules[i].body, rules[j].body
            ):
                rem_rule(prolog, rules[j].rule_id)
                removed_rules.append(rules[j].rule_id)
                aba_framework.background_knowledge.pop(rules[j].rule_id)
                rules.remove(rules[j])
                i -= 1
                j -= 1
                length -= 1
                break
            j += 1
        i += 1
    return rules, removed_rules


def check_loop(aba_framework: ABAFramework, predicate: str, rule: Rule):
    for con in aba_framework.con_body_map:
        if con == predicate and rule.head.predicate in aba_framework.con_body_map[con]:
            return True
    return False


def count_new_vars(new_rule: Rule, rule_1: Rule, rule_2: Rule) -> int:
    new_vars = new_rule.get_vars()
    vars_1 = rule_1.get_vars()
    vars_2 = rule_2.get_vars()
    diff_1 = new_vars.difference(vars_1)
    diff_2 = new_vars.difference(vars_2)
    return min(len(diff_1), len(diff_2))


def fold_rules(prolog, aba_framework: ABAFramework, predicate: str, arity:int) -> ABAFramework:
    new_rules = []
    rules = aba_framework.background_knowledge.values()
    aba_framework = get_current_aba_framework(prolog, aba_framework)
    introduced_neg = False
    new_vars_allowed = 0
    undone = False
    while new_rules == [] and new_vars_allowed < 10:
        for rule_1 in rules:
            for rule_2 in rules:
                if rule_1.head.predicate == predicate:
                    two_folds = False
                    undone = False
                    if foldable(
                        prolog, rule_1.rule_id, rule_2.rule_id
                    ) and not check_loop(aba_framework, predicate, rule_2):
                        prev_framework = deepcopy(aba_framework)
                        prev_neg = count_neg_covered(prolog, aba_framework, predicate)
                        new_rule = fold(prolog, rule_1.rule_id, rule_2.rule_id)
                        aba_framework = get_current_aba_framework(prolog, aba_framework)
                        if new_rule.has_constants():
                            new_rule = unfold_and_replace(prolog, new_rule)
                        eqs_count = len(new_rule.get_equalities())
                        if eqs_count > 0:
                            for rule_3 in rules:
                                if (
                                    rule_3 != rule_1
                                    and rule_3 != rule_2
                                    and new_rule.head.predicate != rule_3.head.predicate
                                ):
                                    if foldable(
                                        prolog, new_rule.rule_id, rule_3.rule_id
                                    ) and not check_loop(
                                        aba_framework, predicate, rule_3
                                    ):
                                        temp_framework = deepcopy(aba_framework)
                                        new_rule_2 = fold(prolog, new_rule.rule_id, rule_3.rule_id)
                                        aba_framework = get_current_aba_framework(
                                            prolog, aba_framework
                                        )
                                        if len(new_rule_2.get_equalities()) > 0:
                                            set_framework(prolog, temp_framework)
                                            aba_framework = get_current_aba_framework(
                                                prolog, aba_framework
                                            )
                                        else:
                                            print(
                                                f"Folding rule {rule_1} with rule {rule_2}"
                                            )
                                            print(
                                                f"Folding rule {new_rule} with rule {rule_3}"
                                            )
                                            two_folds = True
                                            new_rule = new_rule_2
                                            new_vars_allowed += eqs_count
                                            break

                        while len(new_rule.get_equalities()) > 0:
                            for i, b in enumerate(new_rule.body):
                                if isinstance(b, Equality) and (
                                    b.var_2[0].islower() or b.var_2[0].isdigit()
                                ):
                                    new_rule = remove_eq(prolog, new_rule.rule_id, i + 1)
                                    break
                            aba_framework = get_current_aba_framework(
                                prolog, aba_framework
                            )
                        curr_neg = count_neg_covered(prolog, aba_framework, predicate)
                        if curr_neg > prev_neg:
                            if introduced_neg:
                                set_framework(prolog, prev_framework)
                                aba_framework = get_current_aba_framework(
                                    prolog, aba_framework
                                )
                                undone = True
                            else:
                                introduced_neg = True
                        if (
                            count_new_vars(new_rule, rule_1, rule_2) > new_vars_allowed
                            and not undone
                        ):
                            set_framework(prolog, prev_framework)
                            aba_framework = get_current_aba_framework(
                                prolog, aba_framework
                            )
                            undone = True
                        if not undone:
                            if not two_folds:
                                print(
                                    f"Folding rule {rule_1} with rule {rule_2}"
                                )
                            new_rules += [new_rule]
        new_vars_allowed += 1

    new_rules = keep_unique_rules(prolog, aba_framework, new_rules)
    aba_framework = get_current_aba_framework(prolog, aba_framework)
    aba_framework.grounded_extension = make_grounded_extension(prolog, aba_framework)
    return (aba_framework, new_rules)


def assumption_introduction(prolog, aba_framework, rule, atom_pos) -> ABAFramework:
    print(f"Performing assumption introduction on rule {rule}")
    undercut(prolog, rule.rule_id, [pos + 1 for pos in atom_pos])
    return get_current_aba_framework(prolog, aba_framework)


def remove_examples(prolog, aba_framework, pos_exs, neg_exs) -> ABAFramework:
    for pos_ex in pos_exs:
        print(f"Removing example {pos_ex}")
        rem_pos_ex(prolog, pos_ex.example_id)
    for neg_ex in neg_exs:
        print(f"Removing example {neg_ex}")
        rem_neg_ex(prolog, neg_ex.example_id)
    return get_current_aba_framework(prolog, aba_framework)


def add_examples(
    prolog, aba_framework, predicate, pos_consts, neg_consts
) -> ABAFramework:
    for consts in neg_consts:
        ex: Atom = Atom(predicate, consts)
        add_pos_ex(prolog, ex)
    con_pos_ex = aba_framework.con_pos_ex_map.get(predicate, [])
    con_pos_ex += neg_consts
    con_pos_ex.sort()
    aba_framework.con_pos_ex_map[predicate] = con_pos_ex

    for consts in pos_consts:
        ex: Atom = Atom(predicate, consts)
        add_neg_ex(prolog, ex)
    con_neg_ex = aba_framework.con_neg_ex_map.get(predicate, [])
    con_neg_ex += pos_consts
    con_neg_ex.sort()
    aba_framework.con_neg_ex_map[predicate] = con_neg_ex
    return get_current_aba_framework(prolog, aba_framework)


def find_covered_ex(prolog, aba_framework, target):
    cov_pos_ex = []
    cov_neg_ex = []
    for ex in aba_framework.positive_examples.values():
        if ex.get_predicate() == target.get_predicate() and covered(prolog, aba_framework,[ex]):
            cov_pos_ex.append(ex)

    for ex in aba_framework.negative_examples.values():
        if ex.get_predicate() == target.get_predicate() and covered(prolog, aba_framework, [ex]):
            cov_neg_ex.append(ex)

    return (cov_pos_ex, cov_neg_ex)


def find_equiv_contrary(
    aba_framework: ABAFramework, c_a, pos_consts, neg_consts
) -> tuple[str, str]:
    pos_consts.sort()
    neg_consts.sort()
    for a, c in aba_framework.contraries:
        if c_a != c:
            if (
                pos_consts == aba_framework.con_neg_ex_map[c.predicate]
                and neg_consts == aba_framework.con_pos_ex_map[c.predicate]
            ):
                return (a.predicate, c.predicate)
    return (None, None)


def replace_equiv_contrary(
    prolog, aba_framework: ABAFramework, a: str, c_a: str, eq_a: str, eq_c: str
):
    print(f"Replacing {c_a} with {eq_c} as they are equivalent")
    rule_id = list(aba_framework.background_knowledge.keys())[-1]
    rule = aba_framework.background_knowledge[rule_id]
    new_atom = rule.body[-1]
    new_atom.predicate = eq_a
    rule.body = rule.body[:-1] + [new_atom]
    aba_framework.background_knowledge[rule_id] = rule
    aba_framework.assumptions = aba_framework.assumptions[:-1]
    aba_framework.contraries = aba_framework.contraries[:-1]
    set_framework(prolog, aba_framework)
    return aba_framework


def can_still_learn(prolog, aba_framework: ABAFramework, initial_pos_ex) -> bool:
    for pos_ex in initial_pos_ex:
        top_rules = find_top_rule(prolog, aba_framework, pos_ex)
        safe = False
        for r in top_rules:
            if len(r.body) == len(r.get_equalities()):
                if all(
                    [
                        eq.var_1[0].isupper() and eq.var_2[0].isupper()
                        for eq in r.get_equalities()
                    ]
                ):
                    safe = True
            else:
                safe = True
        if not safe:
            return True
    return False


def ensure_has_initial_neg_ex(
    prolog, aba_framework: ABAFramework, initial_neg_ex: list[Example]
) -> tuple[ABAFramework, list[str]]:
    reintroduced = []
    for neg_ex in initial_neg_ex:
        if covered(prolog, aba_framework, [neg_ex]):
            if neg_ex.fact not in [ex.fact for ex in aba_framework.negative_examples.values()]:
                print(f"Reintroducing negative example {neg_ex}.")
                add_neg_ex(prolog, neg_ex.fact)
                reintroduced.append(neg_ex.get_predicate())

    return (get_current_aba_framework(prolog, aba_framework), reintroduced)


def ensure_has_initial_pos_ex(
    prolog, aba_framework: ABAFramework, initial_pos_ex: list[Example]
) -> tuple[ABAFramework, list[Example]]:
    reintroduced = []
    for pos_ex in initial_pos_ex:
        if not covered(prolog, aba_framework, [pos_ex]):
            if pos_ex.fact not in [ex.fact for ex in aba_framework.positive_examples.values()]:
                print(f"Reintroducing positive example {pos_ex}.")
                add_pos_ex(prolog, pos_ex.fact)
                reintroduced.append(pos_ex)
    return (get_current_aba_framework(prolog, aba_framework), reintroduced)

def set_up_iteration(prolog, aba_framework, initial_pos_ex, initial_neg_ex, curr_complete, curr_consistent, learned, prev_removed):
    global NO_PROGRESS_COUNT
    if not curr_consistent:
        (aba_framework, reintroduced) = ensure_has_initial_neg_ex(
            prolog, aba_framework, initial_neg_ex
        )
    if curr_complete:
        NO_PROGRESS_COUNT = 0
    else:
        (aba_framework, reintroduced) = ensure_has_initial_pos_ex(
            prolog, aba_framework, initial_pos_ex
        )
        reintroduced = [ex.fact for ex in reintroduced]
        if len(reintroduced) == 0 and len(prev_removed) == 0:
            NO_PROGRESS_COUNT += 1
        else:
            NO_PROGRESS_COUNT = 0

        if NO_PROGRESS_COUNT > len(learned) and len(learned) > 0:
            raise CredulousSemanticsException()
        if (
            all([ex.fact in reintroduced for ex in prev_removed])
            and len(prev_removed) > 0
        ):
            raise CredulousSemanticsException()

def select_target_and_generate_rules(prolog, aba_framework, learned, count):
    # Select target p for current iteration
    target: Example = select_target(list(aba_framework.positive_examples.values()), learned)
    if target is not None:
        learned.append(target)
        # Generate rules for p via Rote Learning
        aba_framework = generate_rules(prolog, aba_framework, target)
    else:
        target = learned[len(learned) - 1 - count]
        count += 1
        if count == len(learned):
            count = 0
    return aba_framework,target, count

def generalise(prolog, aba_framework, target):
    # Generalise via folding
    (aba_framework, new_rules) = fold_rules(
        prolog, aba_framework, target.get_predicate(), target.get_arity()
    )
    remove_subsumed(prolog, aba_framework, new_rules, target.get_predicate())
    aba_framework.grounded_extension = make_grounded_extension(prolog, aba_framework)
    return aba_framework


def learn_exceptions(prolog, aba_framework,target):
    # Find examples of the target predicate that are covered (both positive and negative)
    (cov_pos_ex, cov_neg_ex) = find_covered_ex(prolog, aba_framework, target)
    neg_top_rules = []
    for ex in cov_neg_ex:
        top_rules = find_top_rule(prolog, aba_framework, ex)
        for rule in top_rules:
            neg_top_rules.append(rule)
    neg_top_rules = set(neg_top_rules)
    # Learn exceptions for each top rule of an argument for covered negative examples
    for rule in neg_top_rules:
        # Choose which variables to consider
        # Currently takes in consideration first atom in the body of the rule
        idxs = [0]
        # Construct the two sets of constants consts(A+) and consts(A-)
        (a_plus, a_minus) = get_constants(
            prolog, aba_framework, rule, cov_pos_ex, cov_neg_ex, idxs
        )
        # Perform assumption introduction via undercutting
        aba_framework = assumption_introduction(prolog, aba_framework, rule, idxs)
        # Add negative and positive examples for the contraries introduced
        (a, c_a) = aba_framework.contraries[-1]
        (eq_a, eq_c) = find_equiv_contrary(aba_framework, c_a, a_plus, a_minus)

        if eq_a is None:
            add_examples(prolog, aba_framework, c_a.predicate, a_plus, a_minus)
        else:
            aba_framework = replace_equiv_contrary(
                prolog,
                aba_framework,
                a.predicate,
                c_a.predicate,
                eq_a,
                eq_c,
                )
    aba_framework = get_current_aba_framework(prolog, aba_framework)
    aba_framework.grounded_extension = make_grounded_extension(prolog,aba_framework)
    return aba_framework

def remove_iteration_examples(prolog, aba_framework, target):
    rem_pos_ex = []
    rem_neg_ex = []
    for ex in aba_framework.positive_examples.values():
        if ex.get_predicate() == target:
            rem_pos_ex.append(ex)
    for ex in aba_framework.negative_examples.values():
        if ex.get_predicate() == target:
            rem_neg_ex.append(ex)
    remove_examples(prolog, aba_framework, rem_pos_ex, rem_neg_ex)
    return rem_pos_ex, get_current_aba_framework(prolog, aba_framework)

def remove_redundant_assumptions(prolog, aba_framework: ABAFramework):
    to_remove = []
    rules = aba_framework.get_new_rules()
    for a, c_a in aba_framework.contraries:
        req = False
        for rule in rules:
            if (rule.head.predicate == c_a.predicate):
                req = True
                break
        if not req:
            to_remove.append(a.predicate)
    for rule in rules:
        initial_body = rule.body
        new_body = list(
            filter(
                lambda b: isinstance(b, Equality)
                or (isinstance(b, Atom) and b.predicate not in to_remove),
                initial_body,
            )
        )
        rule.body = new_body
        aba_framework.background_knowledge[rule.rule_id] = rule
    aba_framework.assumptions = list(
        filter(lambda a: a.predicate not in to_remove, aba_framework.assumptions)
    )
    aba_framework.contraries = list(
        filter(lambda a: a[0].predicate not in to_remove, aba_framework.contraries)
    )

    (prolog, aba_framework)


def abalearn(prolog) -> ABAFramework:
    aba_framework: ABAFramework = get_current_aba_framework(prolog, None)
    initial_pos_ex: list[Example] = aba_framework.positive_examples.values()
    initial_neg_ex: list[Example] = aba_framework.negative_examples.values()
    learned = []
    count = 0
    prev_removed = []
    curr_complete = complete(prolog, aba_framework, initial_pos_ex)
    curr_consistent = consistent(prolog, aba_framework,initial_neg_ex)
    initial_goal = ""
    while not (curr_complete and curr_consistent) or can_still_learn(
        prolog, aba_framework, initial_pos_ex
    ):  
        try:
            set_up_iteration(prolog, aba_framework, initial_pos_ex,initial_neg_ex,curr_complete, curr_consistent, learned, prev_removed)
        except CredulousSemanticsException:
            print("Goal achieved under credulous semantics!")
            break
            
        aba_framework, target, count = select_target_and_generate_rules(
            prolog, aba_framework, learned, count
        )

        if initial_goal == "":
            initial_goal = target
        aba_framework = generalise(prolog, aba_framework, target)
        aba_framework = learn_exceptions(prolog, aba_framework, target)
        prev_removed, aba_framework = remove_iteration_examples(prolog, aba_framework, target.get_predicate())
        breakpoint()
        curr_complete = complete(prolog, aba_framework,initial_pos_ex)
        curr_consistent = consistent(prolog, aba_framework,initial_neg_ex)

    # Remove all remaining examples
    aba_framework = remove_examples(
        prolog,
        aba_framework,
        aba_framework.positive_examples.values(),
        aba_framework.negative_examples.values(),
    )
    remove_redundant_assumptions(prolog, aba_framework)
    print("Successfuly completed learning process!")
    aba_framework = further_generalisation(
        prolog,
        aba_framework,
        initial_goal.get_predicate()
    )
    aba_framework.create_file("solution.pl")
    print("Finished.")
    return aba_framework


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)
