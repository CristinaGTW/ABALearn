from prolog.coverage import covered, get_covered_solutions
from prolog.transformation_rules import rote_learn_all, undercut, fold
from prolog.settings import add_pos_ex, add_neg_ex, rem_pos_ex, rem_neg_ex, rem_rule
from prolog.info import get_rules, get_current_aba_framework
from prolog.config import set_up_abalearn
from elements.aba_framework import ABAFramework
from elements.components import Atom, Equality, Example, Rule
from exceptions.abalearn import TopRuleNotFoundException
import sys


# If all positive examples in the given framework are covered, return True
# Otherwise, return False.
def complete(prolog, pos_ex):
    return covered(prolog, pos_ex)

# If all negative examples in the given framework are NOT covered, return True
# Otherwise, return False.
def consistent(prolog, neg_ex):
    return not any([covered(prolog, [ex]) for ex in neg_ex])

def get_solutions(prolog, rule):
    if all([arg.islower() for arg in rule.head.arguments]):
        return [tuple(rule.head.arguments)]
    replace_args = []
    for eq in rule.body:
        if isinstance(eq, Equality):
            replace_args = [arg if arg != eq.var_1 else eq.var_2 for arg in rule.head.arguments]
    if all([arg.islower() for arg in replace_args]) and len(replace_args) > 0:
        return [tuple(replace_args)]

    sols = get_covered_solutions(prolog, rule.head)
    return sols

def find_top_rule(prolog, aba_framework, ex):
    i = 0
    length = len(aba_framework.background_knowledge)
    while i < length:
        rule = aba_framework.background_knowledge[i]
        aba_framework.background_knowledge.remove(rule)
        if not covered(prolog,[ex]):
            aba_framework.background_knowledge.insert(i, rule)
            return rule
            
        aba_framework.background_knowledge.insert(i, rule)
        i += 1
    raise TopRuleNotFoundException(f"Could not find top rule for covered example {ex}")


def remove_subsumed(prolog, aba_framework, new_rules) -> ABAFramework:
    i = 0
    length = len(aba_framework.background_knowledge)
    while i < length:
        rule = aba_framework.background_knowledge[i]
        if not rule in new_rules:
            sols = get_solutions(prolog, rule)
            rem_rule(prolog, rule.rule_id)
            i -= 1
            length -= 1
            sols_without_rule = get_covered_solutions(prolog, rule.head)
            if set(sols).issubset(set(sols_without_rule)) and len(sols) > 0:
                aba_framework.background_knowledge.remove(rule)
                print(f"Removing rule {rule} as it is subsumed by some other rule")
            else:
                i += 1
                length += 1
                list(prolog.query(f"assert({rule.to_prolog()[:-1]})."))
        i += 1
    return get_current_aba_framework(prolog)

def get_constants(prolog, aba_framework, ex, top_rule, idxs):
    for atom in top_rule.body:
        if isinstance(atom, Atom):
            sols = get_covered_solutions(prolog, atom)

    for pos_ex in aba_framework.positive_examples:
        if pos_ex.get_predicate() == target:
            pos_ex_consts.append(pos_ex.fact.arguments)
    for neg_ex in aba_framework.negative_examples:
        if neg_ex.get_predicate() == target:
            neg_ex_consts.append(neg_ex.fact.arguments)
    
    return (pos_ex_consts, neg_ex_consts)


# Selects as target the examples whose predicate has most occurrences
def select_target(exs:list[Example]) -> Example:
    counter_dict:dict[str,int] = {}
    max_count = -1
    most_common_pred:Example = exs[0]
    for ex in exs:
        counter_dict[ex.get_predicate()] = counter_dict.get(ex.get_predicate(), 0) + 1
        if counter_dict[ex.get_predicate()] > max_count:
            max_count = counter_dict[ex.get_predicate()]
            most_common_pred = ex
    return most_common_pred
    
def generate_rules(prolog, ex:Example) -> ABAFramework:
    print(f"Applying \"Rote Learning\" to build rules for the predicate {ex.get_predicate()}.")
    rote_learn_all(prolog,ex.get_predicate(), ex.get_arity())
    return get_current_aba_framework(prolog)

# rule_1 is considered foldable wrt rule_2
# if the equalities in rule_1 are a subset of the equalities in rule_2
# if the atoms in rule_2 are a subset of the atoms in rule_1
def foldable(rule_1:Rule, rule_2:Rule) -> bool:
    equalities_1:list[Equality] = rule_1.get_equalities()
    equalities_2:list[Equality] = rule_2.get_equalities()
    atoms_1:list[Atom] = rule_1.get_atoms()
    atoms_2:list[Atom] = rule_2.get_atoms()

    if len(equalities_2)>0 and len(equalities_1)==0:
        return False
    if len(atoms_1)>0 and len(atoms_2)==0:
        return False
    for eq_1 in equalities_1:
        if eq_1 not in equalities_2:
            return False
    for a_2 in atoms_2:
        if a_2 not in atoms_1:
            return False
    return True

def keep_unique_rules(prolog,rules):
    length = len(rules)
    i = 0
    while i < length-1:
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

def fold_rules(prolog,rules) -> ABAFramework:
    new_rules = []
    for i in range(len(rules)-1):
        for j in range(i+1,len(rules)):
            if foldable(rules[i], rules[j]):
                print(f"Folding rule {rules[j]} with rule {rules[i]}")
                fold(prolog, rules[j].rule_id, rules[i].rule_id)
                aba_framework = get_current_aba_framework(prolog)
                new_rules += [aba_framework.background_knowledge[-1]]
    new_rules = keep_unique_rules(prolog,new_rules)
    aba_framework = get_current_aba_framework(prolog)
    return (aba_framework, new_rules)

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
        ex:Atom = Atom(predicate,consts)
        add_pos_ex(prolog, ex)
    print(f"Adding as negative examples:")
    for consts in pos_consts:
        ex:Atom = Atom(predicate,consts)
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


def abalearn(prolog) -> None:
    aba_framework: ABAFramework = get_current_aba_framework(prolog)
    count = 0
    initial_pos_ex:list[Example] = aba_framework.positive_examples
    initial_neg_ex:list[Example] = aba_framework.negative_examples
    while not(complete(prolog, initial_pos_ex) and consistent(prolog, initial_neg_ex)):
        # Select target p for current iteration
        target:Example = select_target(aba_framework.positive_examples)
        
        # Generate rules for p via Rote Learning
        aba_framework = generate_rules(prolog, target)

        # Generalise via folding
        (aba_framework, new_rules) = fold_rules(prolog,aba_framework.background_knowledge)

        ## Generalise via subsumption
        aba_framework = remove_subsumed(prolog, aba_framework, new_rules)


        # Find examples of the target predicate that are covered (both positive and negative)

        (cov_pos_ex, cov_neg_ex) = find_covered_ex(prolog, aba_framework, target)


        breakpoint()

        neg_top_rules = [(ex,find_top_rule(prolog, aba_framework, ex)) for ex in cov_neg_ex]

        # Learn exceptions for each top rule of an argument for covered negative examples
        for (cov_ex, rule) in neg_top_rules:
            if rule.head.predicate == target.get_predicate():    
                # Choose which variables to consider
                idxs = [1] # Currently takes in consideration first atom in the body of the rule
                
                # Construct the two sets of constants consts(A+) and consts(A-)
                (a_plus, a_minus) = get_constants(prolog, aba_framework, cov_ex, rule, idxs)
                
                # Perform assumption introduction via undercutting
                aba_framework = assumption_introduction(prolog,rule,idxs) 

                # Add negative and positive examples for the contraries introduced
                (a,c_a) = aba_framework.contraries[-1]
                aba_framework = add_examples(prolog, c_a.predicate, a_plus, a_minus)

        # Remove examples about target
        aba_framework = remove_all_examples(prolog, aba_framework, target.get_predicate())

        aba_framework.create_file(f"progress{count}.pl")    
        count += 1


if __name__=="__main__":
    input_file_path = sys.argv[1]
    prolog = set_up_abalearn(input_file_path)
    abalearn(prolog)

