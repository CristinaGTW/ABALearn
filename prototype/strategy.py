from coverage.cover_utils import covered

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

def select_target(exs):
    ...

def generate_rules(predicate):
    ...

def get_all_ex_of(predicate, exs):
    ...

def remove_exs_of(predicate):
    ...

def assumption_introduction(rule, set_A):
    ...

def construct_basis(atom, rule):
    ...


def abalearn(rules, pos_exs, neg_exs):
    while all_covered(pos_exs) and none_covered(neg_exs):
        target = select_target(pos_exs)

        generate_rules(get_all_ex_of(target, pos_exs))

        generalise(rules)

        target_neg_exs = get_all_ex_of(target, neg_exs)

        while not none_covered(target_neg_exs):
            current = target_neg_exs[0]
            rule = get_argument(current)
            set_A = construct_basis(current,rule)
            assumption_introduction(rule, set_A)

        remove_exs_of(target)







if __name__=="__main__":
    print(all_covered(["flies(a)"]))
    # abalearn()