from coverage.cover_utils import covered
from transformations.learn_utils import get_rules, set_up_abalearn, rote_learn_all, fold, get_current_aba_framework
import sys


# If ALL atoms in the given list are covered by the framework, return True
# Otherwise, return False.
def all_covered(aba_framework,atoms):
    aba_framework.create_file("check.pl")
    return covered("check.pl",atoms)

# If ALL atoms in the given list are NOT covered by the framework, return True
# Otherwise, return False.
def none_covered(aba_framework,atoms):
    aba_framework.create_file("check.pl")
    return not covered("check.pl",atoms)


# Selects as target the examples whose predicate has most occurrences
def select_target(exs):
    predicates = [ex.get_predicate() for ex in exs]
    most_common = max(set(predicates), key=predicates.count)
    for ex in exs:
        if ex.get_predicate() == most_common:
            print(f"Selected target: {ex.get_predicate()}")
            return ex

def generate_rules(prolog,ex):
    print(f"Applying \"Rote Learning\" to build rules for the predicate {ex.get_predicate()}.")
    rote_learn_all(prolog,ex.get_predicate(), ex.get_arity())

# TODO: Change
def foldable(rule_1, rule_2):
    return rule_1.body == rule_2.body

# TODO: Change
def fold_rule(prolog,rules):
    # for rule_1 in rules:
    #     for rule_2 in rules:
    #         if foldable(rule_1, rule_2):
    #             print(f"Folding rule {rule_1.rule_id} with rule {rule_2.rule_id}")
    #             fold(prolog, rule_1.rule_id, rule_2.rule_id)

    for rule in rules[:-1]:
        if foldable(rule, rules[-1]):
            print(f"Folding rule {rules[-1].rule_id} with rule {rule.rule_id}")
            fold(prolog, rules[-1].rule_id, rule.rule_id)            

def assumption_introduction(prolog,rule,atom_pos):
    print(f"Performing assumption introduction on rule {rule.rule_id}")
    assumption_introduction(prolog,rule.rule_id,atom_pos)



def abalearn(prolog):
    aba_framework = get_current_aba_framework(prolog)

    # while not(all_covered(aba_framework.positive_examples) and none_covered(aba_framework.negative_examples)):
    target = select_target(aba_framework.positive_examples)
    generate_rules(prolog, target)
    
    aba_framework = get_current_aba_framework(prolog)
    fold_rule(prolog,aba_framework.background_knowledge)

    for rule in get_rules(prolog):
        print(str(rule))
    assert all_covered(aba_framework,aba_framework.positive_examples)

    aba_framework = get_current_aba_framework(prolog)
    idx = 1
    chosen_rule = aba_framework.background_knowledge[-1]
    assumption_introduction(prolog,chosen_rule,idx) # TODO: Choose the proper arguments

    assert none_covered(aba_framework,aba_framework.negative_examples)

    (a,c_a) = aba_framework.contraries[-1]


    aba_framework.create_file("progress.pl")
        ######
        #   1. Add negative and positive examples for the contrary
        #   2. Remove examples about target
        ######
    







if __name__=="__main__":
    # input_file_path = sys.argv[1]
    input_file_path = "prototype/resources/input.pl"
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)

