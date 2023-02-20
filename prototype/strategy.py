from coverage.cover_utils import covered
from transformations.learn_utils import set_up_abalearn, rote_learn_all, fold
import sys

# Generalise the set of rules through Subsumption, Equality Removal or Folding
def generalise(rules):
    ...


# If ALL atoms in the given list are covered by the framework, return True
# Otherwise, return False.
def all_covered(atoms):
    return covered(atoms)

# If ALL atoms in the given list are NOT covered by the framework, return True
# Otherwise, return False.
def none_covered(atoms):
    return not covered(atoms)


#  If we can construct an argument for atom p, then return the identifier of the top rule of that argument;
#  Otherwise, return null.
def get_argument(atom):
    ...

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

def fold_rule(prolog,rules):
    for rule_1 in rules:
        for rule_2 in rules:
            if foldable(rule_1, rule_2):
                print(f"Folding rule {rule_1.rule_id} with rule {rule_2.rule_id}")
                fold(prolog, rule_1.rule_id, rule_2.rule_id)

def assumption_introduction(prolog,rule,atom_pos):
    print(f"Performing assumption introduction on rule {rule.rule_id}")
    assumption_introduction(prolog,rule,atom_pos)



def abalearn(prolog,rules, pos_exs, neg_exs):
    aba_framework = get_current_aba_framework()
    rules = aba_framework.rules
    pos_exs = aba_framework.positive_examples
    neg_exs = aba_framework.negative_examples

    while not(all_covered(pos_exs) and none_covered(neg_exs)):
        target = select_target(pos_exs)
        generate_rules(prolog, target)

        fold_rule(prolog,rules)
        





if __name__=="__main__":
    input_file_path = sys.argv[1]
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)

