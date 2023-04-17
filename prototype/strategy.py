from prolog.coverage import covered, get_covered_solutions
from prolog.transformation_rules import rote_learn_all, undercut, fold, remove_eq
from prolog.settings import add_pos_ex, add_neg_ex, rem_pos_ex, rem_neg_ex, rem_rule
from prolog.info import get_rules, get_current_aba_framework
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


def top_rule_helper(
    prolog,
    ex: Example,
    background_knowledge: list[Rule],
    removed_rules: list[Rule],
    curr_top_rules: list[Rule],
) -> list[Rule]:
    for i, rule in enumerate(background_knowledge):
        if rule.head.predicate == ex.get_predicate():
            rem_rule(prolog, rule.rule_id)
            cov = covered(prolog, [ex])
            if not cov:
                for r_rule in removed_rules:
                    list(prolog.query(f"assert({r_rule.to_prolog()[:-1]})."))
                    cov = covered(prolog, [ex])
                    if cov:
                        curr_top_rules.append(r_rule)
                list(prolog.query(f"assert({rule.to_prolog()[:-1]})."))
                curr_top_rules.append(rule)
            else:
                removed_rules.append(rule)
                curr_top_rules += top_rule_helper(
                    prolog,
                    ex,
                    background_knowledge[i + 1 :],
                    removed_rules,
                    curr_top_rules,
                )

    for rule in removed_rules:
        if rule not in get_rules(prolog):
            list(prolog.query(f"assert({rule.to_prolog()[:-1]})."))

    return curr_top_rules


def find_top_rule(prolog, aba_framework: ABAFramework, ex: Example) -> list[Rule]:
    return top_rule_helper(prolog, ex, aba_framework.background_knowledge, [], [])


def remove_subsumed(
    prolog, aba_framework: ABAFramework, new_rules: list[Rule]
) -> ABAFramework:
    for rule in aba_framework.background_knowledge:
        if not rule in new_rules:
            sols = get_solutions(prolog, rule)
            rem_rule(prolog, rule.rule_id)
            sols_without_rule = get_covered_solutions(prolog, rule.head)
            sols_without_rule = [tuple(sol.values()) for sol in sols_without_rule]
            if set(sols).issubset(set(sols_without_rule)) and len(sols) > 0:
                aba_framework.background_knowledge.remove(rule)
                print(f"Removing rule {rule} as it is subsumed by some other rule")
            else:
                list(prolog.query(f"assert({rule.to_prolog()[:-1]})."))
    return get_current_aba_framework(prolog)


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
            if b.var_1 in sol.keys():
                if b.var_2[0].islower() or b.var_2[0].isdigit():
                    assert sol[b.var_1] == b.var_2
                else:
                    if b.var_2 in sol.keys():
                        assert sol[b.var_1] == sol[b.var_2]
                    else:
                        sol[b.var_2] = sol[b.var_1]
            else:
                if b.var_2 in sol.keys():
                    sol[b.var_1] = sol[b.var_2]
                elif b.var_2[0].islower() or b.var_2[0].isdigit():
                    sol[b.var_1] = b.var_2
                else:
                    raise InvalidRuleBodyException(
                        f"Body {body} isn't constructed correctly."
                    )
    for b in body_copy:
        if isinstance(b, Atom):
            if not covered(prolog, [Example("fake_ex", b)]):
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
def select_target(exs: list[Example]) -> Example:
    counter_dict: dict[str, int] = {}
    max_count = -1
    most_common_pred: Example = exs[0]
    for ex in exs:
        counter_dict[ex.get_predicate()] = counter_dict.get(ex.get_predicate(), 0) + 1
        if counter_dict[ex.get_predicate()] > max_count:
            max_count = counter_dict[ex.get_predicate()]
            most_common_pred = ex
    return most_common_pred


def generate_rules(prolog, ex: Example) -> ABAFramework:
    print(
        f'Applying "Rote Learning" to build rules for the predicate {ex.get_predicate()}.'
    )
    rote_learn_all(prolog, ex.get_predicate(), ex.get_arity())
    return get_current_aba_framework(prolog)


# rule_1 is considered foldable wrt rule_2
# if the equalities in rule_1 are a subset of the equalities in rule_2
# if the atoms in rule_2 are a subset of the atoms in rule_1
def foldable(rule_1: Rule, rule_2: Rule) -> bool:
    equalities_1: list[Equality] = rule_1.get_equalities()
    equalities_2: list[Equality] = rule_2.get_equalities()
    atoms_1: list[Atom] = rule_1.get_atoms()
    atoms_2: list[Atom] = rule_2.get_atoms()

    if len(equalities_2) > 0 and len(equalities_1) == 0:
        return False
    if len(atoms_1) > 0 and len(atoms_2) == 0:
        return False
    for eq_1 in equalities_1:
        if eq_1 not in equalities_2:
            return False
    for a_2 in atoms_2:
        if a_2 not in atoms_1:
            return False
    return True


def keep_unique_rules(prolog, rules):
    length = len(rules)
    i = 0
    while i < length - 1:
        j = i + 1
        while j < length:
            if rules[i].head == rules[j].head and rules[i].body == rules[j].body:
                rules.remove(rules[i])
                rem_rule(prolog, rules[i].rule_id)
                i -= 1
                j -= 1
                length -= 1
                break
            j += 1
        i += 1
    return rules


def fold_rules(prolog, rules: list[Rule], predicate: str) -> ABAFramework:
    new_rules = []
    for i in range(len(rules)):
        for j in range(len(rules)):
            if (
                rules[i].head != rules[j].head or rules[i].body != rules[j].body
            ) and rules[i].head.predicate == predicate:
                if foldable(rules[i], rules[j]):
                    print(f"Folding rule {rules[i]} with rule {rules[j]}")
                    fold(prolog, rules[i].rule_id, rules[j].rule_id)
                    aba_framework = get_current_aba_framework(prolog)
                    new_rule = aba_framework.background_knowledge[-1]
                    while len(new_rule.get_equalities()) > 0:
                        for i, b in enumerate(new_rule.body):
                            if isinstance(b, Equality):
                                print(
                                    f"Removing equality at position {i+1} from rule {new_rule}"
                                )
                                remove_eq(prolog, new_rule.rule_id, i + 1)
                        aba_framework = get_current_aba_framework(prolog)
                        new_rule = aba_framework.background_knowledge[-1]
                    new_rules += [new_rule]

    new_rules = keep_unique_rules(prolog, new_rules)
    aba_framework = get_current_aba_framework(prolog)

    return (aba_framework, new_rules)


def assumption_introduction(prolog, rule, atom_pos) -> ABAFramework:
    print(f"Performing assumption introduction on rule {rule}")
    undercut(prolog, rule.rule_id, [pos + 1 for pos in atom_pos])
    return get_current_aba_framework(prolog)


def remove_all_examples(prolog, aba_framework, predicate) -> ABAFramework:
    print(f"Removing all examples about {predicate}")
    for pos_ex in aba_framework.positive_examples:
        if pos_ex.get_predicate() == predicate:
            rem_pos_ex(prolog, pos_ex.example_id)
    for neg_ex in aba_framework.negative_examples:
        if neg_ex.get_predicate() == predicate:
            rem_neg_ex(prolog, neg_ex.example_id)
    return get_current_aba_framework(prolog)


def add_examples(prolog, predicate, pos_consts, neg_consts) -> ABAFramework:
    for consts in neg_consts:
        ex: Atom = Atom(predicate, consts)
        add_pos_ex(prolog, ex)
    for consts in pos_consts:
        ex: Atom = Atom(predicate, consts)
        add_neg_ex(prolog, ex)
    return get_current_aba_framework(prolog)


def find_covered_ex(prolog, aba_framework, target):
    cov_pos_ex = []
    cov_neg_ex = []
    for ex in aba_framework.positive_examples:
        if ex.get_predicate() == target.get_predicate() and covered(prolog, [ex]):
            cov_pos_ex.append(ex)

    for ex in aba_framework.negative_examples:
        if ex.get_predicate() == target.get_predicate() and covered(prolog, [ex]):
            cov_neg_ex.append(ex)

    return (cov_pos_ex, cov_neg_ex)


def abalearn(prolog) -> ABAFramework:
    aba_framework: ABAFramework = get_current_aba_framework(prolog)
    initial_pos_ex: list[Example] = aba_framework.positive_examples
    initial_neg_ex: list[Example] = aba_framework.negative_examples
    while not (complete(prolog, initial_pos_ex) and consistent(prolog, initial_neg_ex)):
        # Select target p for current iteration
        target: Example = select_target(aba_framework.positive_examples)

        # Generate rules for p via Rote Learning
        aba_framework = generate_rules(prolog, target)

        # Generalise via folding
        (aba_framework, new_rules) = fold_rules(
            prolog, aba_framework.background_knowledge, target.get_predicate()
        )

        ## Generalise via subsumption
        aba_framework = remove_subsumed(prolog, aba_framework, new_rules)

        # Find examples of the target predicate that are covered (both positive and negative)
        (cov_pos_ex, cov_neg_ex) = find_covered_ex(prolog, aba_framework, target)
        neg_top_rules = []
        for ex in cov_neg_ex:
            top_rules = find_top_rule(prolog, aba_framework, ex)
            for rule in top_rules:
                neg_top_rules.append(rule)
        aba_framework = get_current_aba_framework(prolog)
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
                # Perform assumption introduction via undercutting
                aba_framework = assumption_introduction(prolog, rule, idxs)

                # Add negative and positive examples for the contraries introduced
                (_, c_a) = aba_framework.contraries[-1]

                aba_framework = add_examples(prolog, c_a.predicate, a_plus, a_minus)

        # Remove examples about target
        aba_framework = remove_all_examples(
            prolog, aba_framework, target.get_predicate()
        )

    print("Successfuly completed learning process!")
    aba_framework.create_file("solution.pl")
    return aba_framework


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)
