from prolog.coverage import covered, get_covered_solutions, count_covered, get_top_rule
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
from prolog.info import set_up_aba_framework, get_rules
from prolog.config import set_up_abalearn
from elements.aba_framework import ABAFramework
from elements.components import Atom, Equality, Example, Rule
from exceptions.abalearn import TopRuleNotFoundException, InvalidRuleBodyException
import sys
from copy import deepcopy


# If all positive examples in the given framework are covered, return True
# Otherwise, return False.
def complete(prolog, pos_ex: list[Example]) -> bool:
    return covered(prolog, pos_ex)

# If all negative examples in the given framework are NOT covered, return True
# Otherwise, return False.


def consistent(prolog, neg_ex: list[Example]) -> bool:
    return not any([covered(prolog, [ex]) for ex in neg_ex])


def get_solutions(prolog, rule: Rule) -> list[tuple[str, ...]]:
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

    sols = get_covered_solutions(prolog, rule.head)
    sols = [tuple(sol.values()) for sol in sols]
    return sols


def further_generalisation(
    prolog, aba_framework: ABAFramework, predicate: str, initial_pos_ex, initial_neg_ex
):
    print("Attempting to further generalise...")
    rules = deepcopy(aba_framework.background_knowledge)
    new_vars_allowed = 0
    undone = False
    new_rules = [""]
    while new_rules != []:
        new_rules = []
        for rule_1_id in rules:
            rule_1_folded = False
            for rule_2_id in rules:
                if rule_1_folded:
                    break
                rule_1 = rules[rule_1_id]
                if rule_1.head.predicate == predicate:
                    rule_2 = rules[rule_2_id]
                    undone = False
                    if foldable(
                        prolog, rule_1_id, rule_2_id
                    ) and not check_loop(aba_framework, predicate, rule_2):
                        prev_framework = deepcopy(aba_framework)
                        print(f"Folding rule {rule_1} with rule {rule_2}")
                        new_rule = fold(prolog, aba_framework, rule_1.rule_id, rule_2.rule_id)
                        
                        if new_rule.has_constants():
                            new_rule = unfold_and_replace(prolog, new_rule)

                        while len(new_rule.get_equalities()) > 0:
                            for i, b in enumerate(new_rule.body):
                                if isinstance(b, Equality) and (
                                    b.var_2[0].islower(
                                    ) or b.var_2[0].isdigit()
                                ):
                                    print(
                                        f"Removing equality at position {i+1} from rule {new_rule}"
                                    )
                                    new_rule = remove_eq(prolog, aba_framework, new_rule.rule_id, i + 1)
                                    break

                        if (
                            count_new_vars(new_rule, rule_1,
                                           rule_2) > new_vars_allowed
                            and not undone
                        ):
                            print(
                                "Undoing previous fold as it introduced too many new variables."
                            )
                            set_framework(prolog, prev_framework)
                            aba_framework = prev_framework
                            undone = True
                        if not undone:
                            new_rules += [new_rule]
                            rule_1_folded = True

        rules = deepcopy(aba_framework.background_knowledge)

    return aba_framework


def find_top_rule(prolog, aba_framework: ABAFramework, ex: Example) -> list[Rule]:
    top_rule_ids = get_top_rule(prolog, ex.fact)
    top_rules = []
    for rule in aba_framework.background_knowledge:
        if rule in top_rule_ids:
            top_rules.append(aba_framework.background_knowledge[rule])
    return top_rules


def remove_subsumed(
    prolog, aba_framework: ABAFramework, new_rules: list[Rule]
) -> ABAFramework:
    rules = deepcopy(aba_framework.background_knowledge)
    for rule_id in rules:
        if not aba_framework.background_knowledge[rule_id] in new_rules:
            rule = aba_framework.background_knowledge[rule_id]
            sols = get_solutions(prolog, rule)
            rem_rule(prolog, rule_id)
            sols_without_rule = get_covered_solutions(prolog, rule.head)
            sols_without_rule = [tuple(sol.values())
                                 for sol in sols_without_rule]
            if set(sols).issubset(set(sols_without_rule)) and len(sols) > 0:
                aba_framework.background_knowledge.pop(rule_id)
                print(
                    f"Removing rule {rule} as it is subsumed by some other rule")
            else:
                list(prolog.query(f"assertz({rule.to_prolog()[:-1]})."))



def find_justified_groundings(
    prolog,
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
                sols = get_covered_solutions(prolog, body_copy[i])

                for sol in sols:
                    for var in sol:
                        curr_groundings[var] = sol[var]
                    result += find_justified_groundings(
                        prolog,
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
            if not covered(prolog, [Example("fake_ex", b)]):
                return result
            if any([a[0].isupper() for a in b.arguments]):
                return result
    return result + [body_copy]


def get_constants(
    prolog,
    top_rule: Rule,
    cov_pos_ex: list[Example],
    cov_neg_ex: list[Example],
    idxs: list[int],
) -> tuple[list[list[str]], list[list[str]]]:
    pos_ex_consts = []
    neg_ex_consts = []
    head_sol: list[dict] = get_covered_solutions(prolog, top_rule.head)
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
            prolog, sol, top_rule.body, body_copy, []
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
            prolog, sol, top_rule.body, body_copy, []
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
    new_rules = rote_learn_all(prolog, aba_framework, ex.get_predicate(), ex.get_arity())
    keep_unique_rules(prolog, aba_framework, new_rules)
    # Generalise equalities if possible
    for rule in new_rules:
        gen_eqs(prolog, aba_framework, rule.rule_id)


def keep_unique_rules(prolog, aba_framework, rules):
    length = len(rules)
    i = 0
    while i < length - 1:
        j = i + 1
        while j < length:
            if rules[i].head == rules[j].head and rules[i].body == rules[j].body:
                rules.remove(rules[i])
                rem_rule(prolog, rules[i].rule_id)
                aba_framework.background_knowledge.pop(rules[i].rule_id)
                i -= 1
                j -= 1
                length -= 1
                break
            j += 1
        i += 1
    return rules


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

def fold_rules(prolog, aba_framework: ABAFramework, predicate: str, arity: int) -> ABAFramework:
    new_rules = []
    rules = deepcopy(aba_framework.background_knowledge)
    introduced_neg = False
    new_vars_allowed = 0
    undone = False
    while new_rules == [] and new_vars_allowed < 10:
        for rule_1_id in rules:
            rule_1_folded = False
            for rule_2_id in rules:
                if rule_1_folded:
                    break
                rule_1 = rules[rule_1_id]
                if rule_1.head.predicate == predicate:
                    rule_2 = rules[rule_2_id]
                    undone = False
                    if foldable(
                        prolog, rule_1_id, rule_2_id
                    ) and not check_loop(aba_framework, predicate, rule_2):
                        prev_framework = deepcopy(aba_framework)
                        (_, prev_neg) = count_covered(
                            prolog, aba_framework, predicate, arity)
                        print(f"Folding rule {rule_1} with rule {rule_2}")
                        new_rule = fold(prolog, aba_framework, rule_1_id, rule_2_id)
                        if new_rule.has_constants():
                            new_rule = unfold_and_replace(prolog, new_rule)
                        eqs_count = len(new_rule.get_equalities())
                        if eqs_count > 0:
                            for rule_3_id in rules:
                                rule_3 = rules[rule_3_id]
                                if (
                                    rule_3 != rule_1
                                    and rule_3 != rule_2
                                    and new_rule.head.predicate != rule_3.head.predicate
                                ):
                                    if foldable(
                                        prolog, new_rule.rule_id, rule_3_id
                                    ) and not check_loop(
                                        aba_framework, predicate, rule_3
                                    ):
                                        temp_framework = deepcopy(
                                            aba_framework)
                                        print(
                                            f"Folding rule {new_rule} with rule {rule_3}"
                                        )
                                        new_rule_2 = fold(prolog, aba_framework, new_rule.rule_id,
                                             rule_3_id)
                                        if len(new_rule_2.get_equalities()) > 0:
                                            print(
                                                "Undoing previous fold as it wasn't optimal."
                                            )
                                            set_framework(
                                                prolog, temp_framework)
                                            aba_framework = temp_framework
                                        else:
                                            new_rule = new_rule_2
                                            new_vars_allowed += eqs_count
                                            break

                        while len(new_rule.get_equalities()) > 0:
                            for i, b in enumerate(new_rule.body):
                                if isinstance(b, Equality) and (
                                    b.var_2[0].islower(
                                    ) or b.var_2[0].isdigit()
                                ):
                                    print(
                                        f"Removing equality at position {i+1} from rule {new_rule}"
                                    )
                                    new_rule = remove_eq(prolog, aba_framework, new_rule.rule_id, i + 1)
                                    break
                        (_, curr_neg) = count_covered(
                            prolog, aba_framework, predicate, arity)
                        if curr_neg > prev_neg:
                            if introduced_neg:
                                print(
                                    "Undoing previous fold as it covered additional negative examples."
                                )
                                set_framework(prolog, prev_framework)
                                aba_framework = prev_framework
                                undone = True
                            else:
                                introduced_neg = True
                        if (
                            count_new_vars(new_rule, rule_1,
                                           rule_2) > new_vars_allowed
                            and not undone
                        ):
                            print(
                                "Undoing previous fold as it introduced too many new variables."
                            )
                            set_framework(prolog, prev_framework)
                            aba_framework = prev_framework
                            undone = True
                        if not undone:
                            new_rules += [new_rule]
                            rule_1_folded = True
                            
    
        rules = deepcopy(aba_framework.background_knowledge)
        new_vars_allowed += 1
        
    new_rules = keep_unique_rules(prolog, aba_framework, new_rules)

    return aba_framework,new_rules


def assumption_introduction(prolog, aba_framework, rule, atom_pos) -> ABAFramework:
    print(f"Performing assumption introduction on rule {rule}")
    undercut(prolog, aba_framework, rule.rule_id, [pos + 1 for pos in atom_pos])


def remove_examples(prolog, aba_framework, pos_exs, neg_exs) -> ABAFramework:
    pos_exs_copy = deepcopy(list(pos_exs))
    neg_exs_copy = deepcopy(list(neg_exs))
    for pos_ex in pos_exs_copy:
        print(f"Removing example {pos_ex}")
        rem_pos_ex(prolog, aba_framework, pos_ex.example_id)
    for neg_ex in neg_exs_copy:
        print(f"Removing example {neg_ex}")
        rem_neg_ex(prolog, aba_framework, neg_ex.example_id)


def add_examples(
    prolog, aba_framework, predicate, pos_consts, neg_consts
) -> ABAFramework:
    for consts in neg_consts:
        ex: Atom = Atom(predicate, consts)
        add_pos_ex(prolog, aba_framework,ex)
    con_pos_ex = aba_framework.con_pos_ex_map.get(predicate, [])
    con_pos_ex += neg_consts
    con_pos_ex.sort()
    aba_framework.con_pos_ex_map[predicate] = con_pos_ex

    for consts in pos_consts:
        ex: Atom = Atom(predicate, consts)
        add_neg_ex(prolog, aba_framework, ex)
    con_neg_ex = aba_framework.con_neg_ex_map.get(predicate, [])
    con_neg_ex += pos_consts
    con_neg_ex.sort()
    aba_framework.con_neg_ex_map[predicate] = con_neg_ex


def find_covered_ex(prolog, aba_framework, target):
    cov_pos_ex = []
    cov_neg_ex = []
    for ex in aba_framework.positive_examples.values():
        if ex.get_predicate() == target.get_predicate() and covered(prolog, [ex]):
            cov_pos_ex.append(ex)

    for ex in aba_framework.negative_examples.values():
        if ex.get_predicate() == target.get_predicate() and covered(prolog, [ex]):
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
    for rule_id in aba_framework.background_knowledge:
        rule = aba_framework.background_knowledge[rule_id]
        if rule.head.predicate == c_a:
            aba_framework.background_knowledge[rule_id].head.predicate = eq_c
        elif rule.head.predicate == a:
            aba_framework.background_knowledge[rule_id].head.predicate = eq_a
        else:
            for i, b in enumerate(rule.body):
                if isinstance(b, Atom):
                    if b.predicate == c_a:
                        aba_framework.background_knowledge[rule_id].body[i].predicate = eq_c
                    if b.predicate == a:
                        aba_framework.background_knowledge[rule_id].body[i].predicate = eq_a

    aba_framework.contraries = filter(
        lambda c: c[1].predicate != c_a, aba_framework.contraries
    )
    aba_framework.assumptions = filter(
        lambda x: x.predicate != a, aba_framework.assumptions
    )
    set_framework(prolog, aba_framework)


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
) -> list[str]:
    reintroduced = []
    for neg_ex in initial_neg_ex:
        if covered(prolog, [neg_ex]):
            if neg_ex.fact not in [ex.fact for ex in list(aba_framework.negative_examples.values())]:
                print(f"Reintroducing negative example {neg_ex}.")
                add_neg_ex(prolog, aba_framework, neg_ex.fact)
                reintroduced.append(neg_ex.get_predicate())

    return reintroduced


def ensure_has_initial_pos_ex(
    prolog, aba_framework: ABAFramework, initial_pos_ex: list[Example]
) -> list[Example]:
    reintroduced = []
    for pos_ex in initial_pos_ex:
        if not covered(prolog, [pos_ex]):
            if pos_ex.fact not in [ex.fact for ex in aba_framework.positive_examples.values()]:
                print(f"Reintroducing positive example {pos_ex}.")
                add_pos_ex(prolog, aba_framework, pos_ex.fact)
                reintroduced.append(pos_ex)
    return reintroduced


def abalearn(prolog) -> ABAFramework:
    aba_framework: ABAFramework = set_up_aba_framework(prolog)
    initial_pos_ex: list[Example] = list(aba_framework.positive_examples.values())
    initial_neg_ex: list[Example] = list(aba_framework.negative_examples.values())
    learned = []
    count = 0
    prev_removed = []
    curr_complete = complete(prolog, initial_pos_ex)
    curr_consistent = consistent(prolog, initial_neg_ex)
    can_fold = {}
    initial_goal = ""
    no_progress_count = 0
    while not (curr_complete and curr_consistent) or can_still_learn(
        prolog, aba_framework, initial_pos_ex
    ):
        if not curr_consistent:
            reintroduced = ensure_has_initial_neg_ex(
                prolog, aba_framework, initial_neg_ex
            )
            for ex in reintroduced:
                can_fold[ex] = False

        if not curr_complete:
            reintroduced = ensure_has_initial_pos_ex(
                prolog, aba_framework, initial_pos_ex
            )
            reintroduced = [ex.fact for ex in reintroduced]
            credulous = True
            if len(reintroduced) == 0 and len(prev_removed) == 0:
                no_progress_count += 1
            else:
                no_progress_count = 0

            if no_progress_count > len(learned) and len(learned) > 0:
                print("Goal achieved under credulous reasoning!")
                break
            for ex in prev_removed:
                if ex not in reintroduced:
                    credulous = False
                    break
            if credulous and len(prev_removed) > 0:
                print("Goal achieved under credulous reasoning!")
                break
            prev_removed = []
        else:
            no_progress_count = 0
        # Select target p for current iteration
        target: Example = select_target(
            list(aba_framework.positive_examples.values()), learned)
        if target is not None:
            learned.append(target)
            can_fold[target.get_predicate()] = True
            # Generate rules for p via Rote Learning
            generate_rules(prolog, aba_framework, target)
        else:
            target = learned[len(learned) - 1 - count]
            count += 1
            if count == len(learned):
                count = 0

        if initial_goal == "":
            initial_goal = target

        if can_fold[target.get_predicate()]:
            # Generalise via folding
            aba_framework, new_rules = fold_rules(
                prolog, aba_framework, target.get_predicate(), target.get_arity()
            )
        # Generalise via subsumption
        remove_subsumed(prolog, aba_framework, new_rules)
        # Find examples of the target predicate that are covered (both positive and negative)
        (cov_pos_ex, cov_neg_ex) = find_covered_ex(
            prolog, aba_framework, target)
        neg_top_rules = []
        for ex in cov_neg_ex:
            top_rules = find_top_rule(prolog, aba_framework, ex)
            for rule in top_rules:
                neg_top_rules.append(rule)
        neg_top_rules = set(neg_top_rules)
        # Learn exceptions for each top rule of an argument for covered negative examples
        for rule in neg_top_rules:
            if rule.head.predicate == target.get_predicate():
                # Choose which variables to consider
                idxs = [
                    0
                ]  # Currently takes in consideration first atom in the body of the rule
                # Construct the two sets of constants consts(A+) and consts(A-)
                (cov_pos_ex, cov_neg_ex) = find_covered_ex(
                    prolog, aba_framework, target
                )

                (a_plus, a_minus) = get_constants(
                    prolog, rule, cov_pos_ex, cov_neg_ex, idxs
                )
                if a_plus != [] or a_minus != []:
                    # Perform assumption introduction via undercutting
                    assumption_introduction(
                        prolog, aba_framework, rule, idxs
                    )
                    # Add negative and positive examples for the contraries introduced
                    (a, c_a) = aba_framework.contraries[-1]

                    (eq_a, eq_c) = find_equiv_contrary(
                        aba_framework, c_a, a_plus, a_minus
                    )

                    if eq_a is None:
                        add_examples(
                            prolog, aba_framework, c_a.predicate, a_plus, a_minus
                        )
                    else:
                        replace_equiv_contrary(
                            prolog,
                            aba_framework,
                            a.predicate,
                            c_a.predicate,
                            eq_a,
                            eq_c,
                        )
        (cov_pos_ex, cov_neg_ex) = find_covered_ex(
            prolog, aba_framework, target)
        true_cov_pos_ex = []
        for pos_ex in aba_framework.positive_examples.values():
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
            if safe:
                true_cov_pos_ex.append(pos_ex)
        prev_removed = [ex.fact for ex in true_cov_pos_ex]

        not_cov_neg_ex = []
        for neg_ex in aba_framework.negative_examples.values():
            if not covered(prolog, [neg_ex]):
                if any(
                    [
                        r.head.predicate == neg_ex.get_predicate()
                        for r in aba_framework.background_knowledge.values()
                    ]
                ):
                    not_cov_neg_ex.append(neg_ex)

        # Remove examples about target
        remove_examples(
            prolog, aba_framework, true_cov_pos_ex, not_cov_neg_ex
        )
        curr_complete = complete(prolog, initial_pos_ex)
        curr_consistent = consistent(prolog, initial_neg_ex)

    # Remove all remaining examples
    remove_examples(
        prolog,
        aba_framework,
        aba_framework.positive_examples.values(),
        aba_framework.negative_examples.values(),
    )

    print("Successfuly completed learning process!")
    further_generalisation(
        prolog,
        aba_framework,
        initial_goal.get_predicate(),
        initial_pos_ex,
        initial_neg_ex,
    )
    aba_framework.create_file("solution.pl")
    print("Finished.")
    return aba_framework


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)
