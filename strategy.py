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
)
from prolog.info import set_up_aba_framework
from prolog.config import set_up_abalearn
from prolog.coverage import (
    count_covered,
    get_covered_solutions,
    get_top_rule,
    get_covered_groundings,
    update_covered,
    covered,
)
from elements.aba_framework import ABAFramework
from elements.components import Atom, Equality, Example, Rule
from exceptions.abalearn import InvalidRuleBodyException, CredulousSemanticsException
import sys
from copy import deepcopy


NO_PROGRESS_COUNT = 0


# If all positive examples in the given framework are covered, return True
# Otherwise, return False.
def complete(aba_framework, pos_exs: list[Example]) -> bool:
    return all([covered(aba_framework, pos_ex.fact) for pos_ex in pos_exs])


# If all negative examples in the given framework are NOT covered, return True
# Otherwise, return False.


def consistent(aba_framework, neg_exs: list[Example]) -> bool:
    return not any([covered(aba_framework, neg_ex.fact) for neg_ex in neg_exs])


def remove_redundant_assumptions(prolog, aba_framework: ABAFramework):
    to_remove = []
    for a, c_a in aba_framework.contraries:
        req = False
        for rule_id in aba_framework.background_knowledge:
            if (
                aba_framework.background_knowledge[rule_id].head.predicate
                == c_a.predicate
            ):
                req = True
                break
        if not req:
            to_remove.append(a.predicate)
    for rule_id in aba_framework.background_knowledge:
        rule = aba_framework.background_knowledge[rule_id]
        initial_body = rule.body
        new_body = list(
            filter(
                lambda b: isinstance(b, Equality)
                or (isinstance(b, Atom) and b.predicate not in to_remove),
                initial_body,
            )
        )
        rule.body = new_body
        aba_framework.background_knowledge[rule_id] = rule
    aba_framework.assumptions = list(
        filter(lambda a: a.predicate not in to_remove, aba_framework.assumptions)
    )
    aba_framework.contraries = list(
        filter(lambda a: a[0].predicate not in to_remove, aba_framework.contraries)
    )

    set_framework(prolog, aba_framework)


def get_stats(aba_framework, pos_exs: list[Example], neg_exs: list[Example]):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for pos_ex in pos_exs:
        if covered(aba_framework, pos_ex.fact):
            tp += 1
        else:
            fn += 1
    for neg_ex in neg_exs:
        if covered(aba_framework, neg_ex.fact):
            fp += 1
        else:
            tn += 1

    accuracy = (tp + tn) / (tp + tn + fp + fn)
    print(f"Accuracy: {accuracy}")
    if tp + fp > 0:
        precision = tp / (tp + fp)
        print(f"Precision: {precision}")
    if tp + fn > 0:
        recall = tp / (tp + fn)
        print(f"Recall: {recall}")


def get_solutions(aba_framework, rule: Rule) -> list[tuple[str, ...]]:
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

    sols = get_covered_solutions(aba_framework, rule.head)
    sols = [tuple(sol.values()) for sol in sols]
    return sols


def further_generalisation(prolog, aba_framework: ABAFramework, predicate: str):
    print("Attempting to further generalise...")
    new_vars_allowed = 0
    folded = True
    new_rules = aba_framework.get_new_rules()
    while folded:
        rules = deepcopy(new_rules)
        folded = False
        for rule_1_id in rules:
            if folded == True:
                break
            for rule_2_id in rules:
                rule_1 = rules[rule_1_id]
                if rule_1.head.predicate == predicate:
                    rule_2 = rules[rule_2_id]
                    if foldable(prolog, rule_1, rule_2, safe=False) and not check_loop(
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
                            new_rules.pop(rule_1_id)
                            new_rules[new_rule.rule_id] = new_rule
                            folded = True
                            break

    return aba_framework


def find_top_rule(aba_framework: ABAFramework, ex: Example) -> list[Rule]:
    top_rule_ids = get_top_rule(aba_framework, ex.fact)
    top_rules = []
    for rule in aba_framework.background_knowledge:
        if rule in top_rule_ids:
            top_rules.append(aba_framework.background_knowledge[rule])
    return top_rules


def remove_subsumed(prolog, aba_framework: ABAFramework, target) -> ABAFramework:
    rules = deepcopy(aba_framework.get_new_rules())
    for rule_id, rule in rules.items():
        if rule.head.predicate == target:
            sols = get_solutions(aba_framework, rule)
            aba_framework.background_knowledge.pop(rule_id)
            removed_arguments = aba_framework.adjust_arguments(rule_id)
            sols_without_rule = get_covered_solutions(aba_framework, rule.head)
            sols_without_rule = [tuple(sol.values()) for sol in sols_without_rule]
            if set(sols).issubset(set(sols_without_rule)) and len(sols) > 0:
                rem_rule(prolog, rule_id)
                print(f"Removing rule {rule} as it is subsumed by some other rule")
            else:
                aba_framework.background_knowledge[rule_id] = rule
                for accepted in removed_arguments:
                    if accepted not in aba_framework.arguments:
                        aba_framework.arguments[accepted] = []
                    aba_framework.arguments[accepted].extend(
                        removed_arguments[accepted]
                    )


def find_justified_groundings(
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
                sols = get_covered_solutions(aba_framework, body_copy[i])

                for sol in sols:
                    for var in sol:
                        curr_groundings[var] = sol[var]
                    result += find_justified_groundings(
                        aba_framework,
                        curr_groundings,
                        body_copy[i:],
                        deepcopy(body_copy)[i:],
                        result,
                    )
        if isinstance(b, Equality):
            if b.var_1 in curr_groundings.keys():
                if not b.var_2[0].isupper():
                    assert curr_groundings[b.var_1] == b.var_2
                else:
                    if b.var_2 in curr_groundings.keys():
                        assert curr_groundings[b.var_1] == curr_groundings[b.var_2]
                    else:
                        curr_groundings[b.var_2] = curr_groundings[b.var_1]
            else:
                if b.var_2 in curr_groundings.keys():
                    curr_groundings[b.var_1] = curr_groundings[b.var_2]
                elif not b.var_2[0].isupper():
                    curr_groundings[b.var_1] = b.var_2
                else:
                    raise InvalidRuleBodyException(
                        f"Body {body} isn't constructed correctly."
                    )
    for b in body_copy:
        if isinstance(b, Atom):
            if not covered(aba_framework, b):
                return result
            if any([a[0].isupper() for a in b.arguments]):
                return result
    return result + [body_copy]


def get_constants(
    aba_framework,
    top_rule: Rule,
    cov_pos_ex: list[Example],
    cov_neg_ex: list[Example],
    idxs: list[int],
) -> tuple[list[list[str]], list[list[str]]]:
    pos_ex_consts = []
    neg_ex_consts = []
    head_sol: list[tuple(Atom, dict)] = get_covered_groundings(
        aba_framework, top_rule.head
    )
    pos_ex_sols: list[dict] = []
    neg_ex_sols: list[dict] = []

    for sol_atom, sol in head_sol:
        if (
            any([ex.fact.correct_grounding(str(sol_atom))[0] for ex in cov_pos_ex])
            and sol not in pos_ex_sols
        ):
            pos_ex_sols.append(sol)
        if (
            any([ex.fact.correct_grounding(str(sol_atom))[0] for ex in cov_neg_ex])
            and sol not in neg_ex_sols
        ):
            neg_ex_sols.append(sol)
    for sol in pos_ex_sols:
        body_copy: list[Atom | Equality] = deepcopy(top_rule.body)
        grounded_bodies = find_justified_groundings(
            aba_framework, sol, top_rule.body, body_copy, []
        )
        for grounded_body in grounded_bodies:
            curr_sol = []
            for i in idxs:
                if isinstance(grounded_body[i], Atom):
                    for a in grounded_body[i].arguments:
                        curr_sol.append(a)
            if curr_sol not in pos_ex_consts:
                pos_ex_consts.append(curr_sol)
    for sol in neg_ex_sols:
        body_copy: list[Atom | Equality] = deepcopy(top_rule.body)
        grounded_bodies = find_justified_groundings(
            aba_framework, sol, top_rule.body, body_copy, []
        )
        for grounded_body in grounded_bodies:
            curr_sol = []
            for i in idxs:
                if isinstance(grounded_body[i], Atom):
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
    new_rules = rote_learn_all(
        prolog, aba_framework, ex.get_predicate(), ex.get_arity()
    )
    new_rules, _ = keep_unique_rules(prolog, aba_framework, new_rules)
    # Generalise equalities if possible
    for rule in new_rules:
        new_rule = gen_eqs(prolog, aba_framework, rule.rule_id)
        if new_rule is not None:
            rule = new_rule
        update_covered(prolog, aba_framework, rule.rule_id)


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


def fold_rules(prolog, aba_framework: ABAFramework, predicate: str) -> ABAFramework:
    new_rules = []
    rules = deepcopy(aba_framework.background_knowledge)
    new_vars_allowed = 0
    undone = False
    fold_stats = {}
    folded = {}
    performed_fold = False
    while not performed_fold and new_vars_allowed < 10:
        for rule_1_id in rules:
            rule_1 = rules[rule_1_id]
            if rule_1.head.predicate == predicate:
                fold_stats = {}
                least_neg_ex = len(aba_framework.negative_examples)
                most_pos_ex = 0
                for rule_2_id in rules:
                    rule_2 = rules[rule_2_id]
                    undone = False
                    two_folds = False
                    if foldable(prolog, rule_1, rule_2) and not check_loop(
                        aba_framework, predicate, rule_2
                    ):
                        prev_framework = deepcopy(aba_framework)
                        new_rule = fold(prolog, aba_framework, rule_1_id, rule_2_id)
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
                                        prolog, new_rule, rule_3
                                    ) and not check_loop(
                                        aba_framework, predicate, rule_3
                                    ):
                                        temp_framework = deepcopy(aba_framework)
                                        new_rule_2 = fold(
                                            prolog,
                                            aba_framework,
                                            new_rule.rule_id,
                                            rule_3_id,
                                        )
                                        if len(new_rule_2.get_equalities()) > 0:
                                            set_framework(prolog, temp_framework)
                                            aba_framework = temp_framework
                                        else:
                                            two_folds = True
                                            second_fold = rule_3_id
                                            new_rule = new_rule_2
                                            new_vars_allowed += eqs_count

                        while len(new_rule.get_equalities()) > 0:
                            for i, b in enumerate(new_rule.body):
                                if isinstance(b, Equality) and (
                                    b.var_2[0].islower() or b.var_2[0].isdigit()
                                ):
                                    new_rule = remove_eq(
                                        prolog, aba_framework, new_rule.rule_id, i + 1
                                    )
                                    break
                        if count_new_vars(new_rule, rule_1, rule_2) > new_vars_allowed:
                            undone = True
                        if not undone:
                            cov_pos_ex, cov_neg_ex = count_covered(aba_framework)
                            if cov_neg_ex <= least_neg_ex and cov_pos_ex >= most_pos_ex:
                                if cov_neg_ex > 1:
                                    least_neg_ex = cov_neg_ex
                                most_pos_ex = cov_pos_ex
                                if two_folds:
                                    fold_stats[rule_2_id] = (
                                        second_fold,
                                        cov_pos_ex,
                                        cov_neg_ex,
                                    )
                                else:
                                    fold_stats[rule_2_id] = (
                                        None,
                                        cov_pos_ex,
                                        cov_neg_ex,
                                    )
                        set_framework(prolog, prev_framework)
                        aba_framework = prev_framework

                for rule_2_id, stats in fold_stats.items():
                    if stats[1] >= most_pos_ex and stats[2] <= least_neg_ex:
                        if rule_2_id not in folded or not stats[0] is None:
                            folded[rule_2_id] = True
                            new_rule = fold(
                                prolog,
                                aba_framework,
                                rule_1_id,
                                rule_2_id,
                                update=False,
                            )
                            performed_fold = True
                            aba_framework.adjust_arguments(rule_1_id)
                            print(f"Folding rule {rule_1_id} with rule {rule_2_id}")
                            if not stats[0] is None:
                                print(
                                    f"Folding rule {new_rule.rule_id} with rule {stats[0]}"
                                )
                                aba_framework.adjust_arguments(new_rule.rule_id)
                                new_rule = fold(
                                    prolog,
                                    aba_framework,
                                    new_rule.rule_id,
                                    stats[0],
                                    update=False,
                                )
                            while len(new_rule.get_equalities()) > 0:
                                for i, b in enumerate(new_rule.body):
                                    if isinstance(b, Equality) and (
                                        b.var_2[0].islower() or b.var_2[0].isdigit()
                                    ):
                                        new_rule = remove_eq(
                                            prolog,
                                            aba_framework,
                                            new_rule.rule_id,
                                            i + 1,
                                            update=False,
                                        )
                                        break
                            new_rules.append(new_rule)
                            break
        new_vars_allowed += 1

    if len(new_rules) > 0:
        update_covered(prolog, aba_framework, new_rule.rule_id)
        _, removed_rules = keep_unique_rules(prolog, aba_framework, new_rules)
        for rule in removed_rules:
            aba_framework.adjust_arguments(rule)

    return aba_framework


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
        add_pos_ex(prolog, aba_framework, ex)
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


def find_covered_ex(aba_framework, target):
    cov_pos_ex = []
    cov_neg_ex = []
    for ex in aba_framework.positive_examples.values():
        if ex.get_predicate() == target.get_predicate() and covered(
            aba_framework, ex.fact
        ):
            cov_pos_ex.append(ex)

    for ex in aba_framework.negative_examples.values():
        if ex.get_predicate() == target.get_predicate() and covered(
            aba_framework, ex.fact
        ):
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


def replace_equiv_contrary(prolog, aba_framework: ABAFramework, eq_a: str):
    print(
        f"Replacing the last introduced assumption with {eq_a} as they are equivalent"
    )
    rule_id = list(aba_framework.background_knowledge.keys())[-1]
    rule = aba_framework.background_knowledge[rule_id]
    new_atom = rule.body[-1]
    new_atom.predicate = eq_a
    rule.body = rule.body[:-1] + [new_atom]
    aba_framework.background_knowledge[rule_id] = rule
    aba_framework.assumptions = aba_framework.assumptions[:-1]
    aba_framework.contraries = aba_framework.contraries[:-1]
    set_framework(prolog, aba_framework)


def ensure_has_initial_neg_ex(
    prolog, aba_framework: ABAFramework, initial_neg_ex: list[Example]
) -> list[str]:
    reintroduced = []
    for neg_ex in initial_neg_ex:
        if covered(aba_framework, neg_ex.fact):
            if neg_ex.fact not in [
                ex.fact for ex in list(aba_framework.negative_examples.values())
            ]:
                print(f"Reintroducing:")
                add_neg_ex(prolog, aba_framework, neg_ex.fact)
                reintroduced.append(neg_ex.get_predicate())

    return reintroduced


def ensure_has_initial_pos_ex(
    prolog, aba_framework: ABAFramework, initial_pos_ex: list[Example]
) -> list[Example]:
    reintroduced = []
    for pos_ex in initial_pos_ex:
        if not covered(aba_framework, pos_ex.fact):
            if pos_ex.fact not in [
                ex.fact for ex in aba_framework.positive_examples.values()
            ]:
                print(f"Reintroducing:")
                add_pos_ex(prolog, aba_framework, pos_ex.fact)
                reintroduced.append(pos_ex)
    return reintroduced


def set_up_iteration(
    prolog,
    aba_framework,
    initial_pos_ex,
    initial_neg_ex,
    curr_complete,
    curr_consistent,
    learned,
    prev_removed,
):
    global NO_PROGRESS_COUNT
    if not curr_consistent:
        reintroduced = ensure_has_initial_neg_ex(prolog, aba_framework, initial_neg_ex)

    if curr_complete:
        NO_PROGRESS_COUNT = 0
    else:
        reintroduced = ensure_has_initial_pos_ex(prolog, aba_framework, initial_pos_ex)
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
        prev_removed = []


def select_target_and_generate_rules(prolog, aba_framework, learned, count):
    # Select target p for current iteration
    target: Example = select_target(
        list(aba_framework.positive_examples.values()), learned
    )
    if target is not None:
        learned.append(target)
        # Generate rules for p via Rote Learning
        generate_rules(prolog, aba_framework, target)
    else:
        target = learned[len(learned) - 1 - count]
        count += 1
        if count == len(learned):
            count = 0
    return target, count


def generalise(prolog, aba_framework, target):
    # Generalise via folding
    aba_framework = fold_rules(prolog, aba_framework, target.get_predicate())
    # Generalise via subsumption
    remove_subsumed(prolog, aba_framework, target.get_predicate())

    return aba_framework


def learn_exceptions(prolog, aba_framework, target):
    # Find examples of the target predicate that are covered (both positive and negative)
    (cov_pos_ex, cov_neg_ex) = find_covered_ex(aba_framework, target)
    neg_top_rules = []
    for ex in cov_neg_ex:
        top_rules = find_top_rule(aba_framework, ex)
        for rule in top_rules:
            neg_top_rules.append(rule)
    neg_top_rules = set(neg_top_rules)
    # Learn exceptions for each top rule of an argument for covered negative examples
    for rule in neg_top_rules:
        # Choose the variables of which atoms in the body to consider
        idxs = list(
            range(len(rule.body))
        )  # Currently considers the variables of all atoms in the body
        # Construct the two sets of constants consts(A+) and consts(A-)
        (a_plus, a_minus) = get_constants(
            aba_framework, rule, cov_pos_ex, cov_neg_ex, idxs
        )
        # Perform assumption introduction via undercutting
        assumption_introduction(prolog, aba_framework, rule, idxs)
        # Add negative and positive examples for the contraries introduced
        (a, c_a) = aba_framework.contraries[-1]
        (eq_a, eq_c) = find_equiv_contrary(aba_framework, c_a, a_plus, a_minus)

        if eq_a is None:
            add_examples(prolog, aba_framework, c_a.predicate, a_plus, a_minus)
        else:
            replace_equiv_contrary(prolog, aba_framework, eq_a)


def remove_iteration_examples(prolog, aba_framework: ABAFramework, target: str):
    rem_pos_ex = []
    rem_neg_ex = []
    for ex in aba_framework.positive_examples:
        if aba_framework.positive_examples[ex].get_predicate() == target:
            rem_pos_ex.append(aba_framework.positive_examples[ex])
    for ex in aba_framework.negative_examples:
        if aba_framework.negative_examples[ex].get_predicate() == target:
            rem_neg_ex.append(aba_framework.negative_examples[ex])
    remove_examples(prolog, aba_framework, rem_pos_ex, rem_neg_ex)
    return rem_pos_ex


def abalearn(prolog) -> ABAFramework:
    aba_framework: ABAFramework = set_up_aba_framework(prolog)
    initial_pos_ex: list[Example] = list(aba_framework.positive_examples.values())
    initial_neg_ex: list[Example] = list(aba_framework.negative_examples.values())
    learned = []
    count = 0
    prev_rem_pos_ex = []
    curr_complete = complete(aba_framework, initial_pos_ex)
    curr_consistent = consistent(aba_framework, initial_neg_ex)
    initial_goal = ""
    while not (curr_complete and curr_consistent):
        try:
            set_up_iteration(
                prolog,
                aba_framework,
                initial_pos_ex,
                initial_neg_ex,
                curr_complete,
                curr_consistent,
                learned,
                prev_rem_pos_ex,
            )
        except CredulousSemanticsException:
            print("Goal achieved under credulous semantics!")
            break
        target, count = select_target_and_generate_rules(
            prolog, aba_framework, learned, count
        )
        if initial_goal == "":
            initial_goal = target
        aba_framework = generalise(prolog, aba_framework, target)
        learn_exceptions(prolog, aba_framework, target)
        prev_rem_pos_ex = remove_iteration_examples(
            prolog, aba_framework, target.get_predicate()
        )

        curr_complete = complete(aba_framework, initial_pos_ex)
        curr_consistent = consistent(aba_framework, initial_neg_ex)

    print("Successfuly completed learning process!")

    remove_redundant_assumptions(prolog, aba_framework)
    further_generalisation(prolog, aba_framework, initial_goal.get_predicate())
    aba_framework.create_file("solution.pl")
    print("Finished.")
    get_stats(aba_framework, initial_pos_ex, initial_neg_ex)
    return aba_framework


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)
