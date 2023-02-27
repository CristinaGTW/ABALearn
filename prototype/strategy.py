from coverage.cover_utils import covered, get_covered_solutions
from transformations.learn_utils import get_rules, add_pos_ex, add_neg_ex, rem_pos_ex, rem_neg_ex, undercut, set_up_abalearn, rote_learn_all, fold, get_current_aba_framework, rem_rule
from elements.aba_framework import ABAFramework
from elements.components import Atom, Equality
import sys
import os


# If all positive examples in the given framework are covered, return True
# Otherwise, return False.
def complete(aba_framework, pos_ex):
    aba_framework.create_file("check.pl")
    ret = covered("check.pl", pos_ex)
    os.remove("check.pl")
    return ret

# If all negative examples in the given framework are NOT covered, return True
# Otherwise, return False.
def consistent(aba_framework, neg_ex):
    aba_framework.create_file("check.pl")
    for ex in neg_ex:
        if covered("check.pl", [ex]):
            os.remove("check.pl")
            return False
    os.remove("check.pl")
    return True

def get_solutions(rule, aba_framework):
    if all([arg.islower() for arg in rule.head.arguments]):
        return [tuple(replace_args)]
    replace_args = []
    for eq in rule.body:
        if isinstance(eq, Equality):
            replace_args = [arg if arg != eq.var_1 else eq.var_2 for arg in rule.head.arguments]
    if all([arg.islower() for arg in replace_args]) and len(replace_args) > 0:
        return [tuple(replace_args)]

    
    sols = get_covered_solutions(aba_framework, rule.head)
    return sols

def remove_subsumed(prolog, aba_framework) -> ABAFramework:
    i = 0
    length = len(aba_framework.background_knowledge)
    aba_framework.create_file(f"before_check.pl")  
    while i < length:
        rule = aba_framework.background_knowledge[i]
        sols = get_solutions(rule, aba_framework)
        aba_framework.background_knowledge.remove(rule)
        i -= 1
        length -= 1
        sols_without_rule = get_covered_solutions(aba_framework, rule.head)
        if set(sols).issubset(set(sols_without_rule)) and len(sols) > 0:
            print(f"Removing rule {rule.rule_id} as it is subsumed by some other rule")
            rem_rule(prolog, rule.rule_id)
        else:
            i += 1
            length += 1
            aba_framework.background_knowledge.insert(i, rule)
        i += 1
    aba_framework = get_current_aba_framework(prolog)
    aba_framework.create_file(f"after_check.pl")  
    return aba_framework

def get_constants(aba_framework, target):
    pos_ex_consts = []
    neg_ex_consts = []
    
    for pos_ex in aba_framework.positive_examples:
        if pos_ex.get_predicate() == target:
            pos_ex_consts.append(pos_ex.fact.arguments)
    for neg_ex in aba_framework.negative_examples:
        if neg_ex.get_predicate() == target:
            neg_ex_consts.append(neg_ex.fact.arguments)
    
    return (pos_ex_consts, neg_ex_consts)


# Selects as target the examples whose predicate has most occurrences
def select_target(exs):
    predicates = [ex.get_predicate() for ex in exs]
    most_common = max(set(predicates), key=predicates.count)
    for ex in exs:
        if ex.get_predicate() == most_common:
            print(f"Selected target: {ex.get_predicate()}")
            return ex

def generate_rules(prolog,ex) -> ABAFramework:
    print(f"Applying \"Rote Learning\" to build rules for the predicate {ex.get_predicate()}.")
    rote_learn_all(prolog,ex.get_predicate(), ex.get_arity())
    return get_current_aba_framework(prolog)

# TODO: Change
def foldable(rule_1, rule_2):
    return rule_1.body == rule_2.body

# TODO: Change
def fold_rule(prolog,rules) -> ABAFramework:
    for rule_1 in rules:
        for rule_2 in rules:
            if rule_1 != rule_2:
                if foldable(rule_1, rule_2):
                    print(f"Folding rule {rule_2.rule_id} with rule {rule_1.rule_id}")
                    fold(prolog, rule_2.rule_id, rule_1.rule_id)
                    return get_current_aba_framework(prolog)
   

def assumption_introduction(prolog,rule,atom_pos) -> ABAFramework:
    print(f"Performing assumption introduction on rule {rule.rule_id}")
    undercut(prolog,rule.rule_id,atom_pos)
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
    print(f"Adding as positive examples:")
    for consts in neg_consts:
        ex = Atom(predicate,consts)
        print(ex)
        add_pos_ex(prolog, ex)
    print(f"Adding as negative examples:")
    for consts in pos_consts:
        ex = Atom(predicate,consts)
        print(ex)
        add_neg_ex(prolog, ex)
    return get_current_aba_framework(prolog)


def abalearn(prolog):
    aba_framework = get_current_aba_framework(prolog)
    count = 0
    initial_pos_ex = aba_framework.positive_examples
    initial_neg_ex = aba_framework.negative_examples
    while not(complete(aba_framework, initial_pos_ex) and consistent(aba_framework, initial_neg_ex)):
        # Select target p for current iteration
        target = select_target(aba_framework.positive_examples)
        
        # Generate rules for p via Rote Learning
        aba_framework = generate_rules(prolog, target)

        # Generalise via folding
        aba_framework = fold_rule(prolog,aba_framework.background_knowledge)

        ## Generalise via subsumption
        aba_framework = remove_subsumed(prolog, aba_framework)

        # Learn exceptions
        # Choose a rule that is a top rule in an argument for one of the negative examples
        chosen_rule = aba_framework.background_knowledge[-1] # Currently chooses last rule which should be the one obtained from folding TODO: Properly choose it
        # Choose which variables to consider
        idxs = list(range(1,len(chosen_rule.head.arguments)+1)) # Currently takes in consideration all the arguments present in the head of the rule
        # Construct the two sets of constants consts(A+) and consts(A-)
        (a_plus, a_minus) = get_constants(aba_framework, target.get_predicate())
        # Perform assumption introduction via undercutting
        aba_framework = assumption_introduction(prolog,chosen_rule,idxs) 

        # Add negative and positive examples for the contraries introduced
        (a,c_a) = aba_framework.contraries[-1]
        aba_framework = add_examples(prolog, c_a.predicate, a_plus, a_minus)

        # Remove examples about target
        aba_framework = remove_all_examples(prolog, aba_framework, target.get_predicate())

        aba_framework.create_file(f"progress{count}.pl")    
        count += 1







if __name__=="__main__":
    # input_file_path = sys.argv[1]
    input_file_path = "prototype/resources/input.pl"
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)

