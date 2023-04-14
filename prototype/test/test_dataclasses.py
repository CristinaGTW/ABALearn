from elements.components import Atom, Rule, Example, Equality

##### ATOM TESTS

def test_parse_atom():
    atom = Atom.parse_atom("bird(a)")
    assert atom.predicate == "bird"
    assert atom.arguments == ["a"]

def test_atom_to_str():
    atom = Atom("bird", ["a"])
    atom_str = str(atom)
    assert atom_str == "bird(a)"

def test_atom_to_prolog_asm():
    atom = Atom("a1", ["X"])
    prolog_asm = atom.to_prolog_asm()
    assert prolog_asm == "my_asm(a1(X))."

def test_atom_to_prolog_contrary():
    atom = Atom("a1", ["X"])
    c_atom = Atom("c_a1", ["X"])
    prolog_contrary = Atom.to_prolog_contrary(atom,c_atom)
    assert prolog_contrary == "contrary(a1(X),c_a1(X))."


##### RULE TESTS

def test_parse_rule():
    rule = Rule.parse_rule("r_1:bird(X)<-penguin(X),X=a")
    assert rule.rule_id == "r_1"
    assert rule.head == Atom("bird", ["X"])
    assert rule.body == [Atom("penguin", ["X"]), Equality("X","a")]

def test_rule_to_str():
    rule = Rule("r_1", Atom("bird", ["X"]), [Atom("penguin", ["X"]), Equality("X","a")])
    rule_str = str(rule)
    assert rule_str == "r_1:bird(X)<-penguin(X),X=a"

def test_rule_to_prolog():
    rule = Rule("r_1", Atom("bird", ["X"]), [Atom("penguin", ["X"])])
    prolog_rule = rule.to_prolog()
    assert prolog_rule == "my_rule(r_1,bird(X),[penguin(X)])."


##### EXAMPLE TESTS

def test_parse_example():
    example = Example.parse_example("e_1:flies(a)")
    assert example.example_id == "e_1"
    assert example.fact == Atom("flies", ["a"])

def test_example_to_str():
    example = Example("e_1", Atom("flies", ["a"]))
    example_str = str(example)
    assert example_str == "e_1:flies(a)"

def test_example_to_prolog_pos():
    example = Example("e_1", Atom("flies", ["a"]))
    prolog_pos_ex = example.to_prolog_pos()
    assert prolog_pos_ex == "pos(e_1,flies(a))."

def test_example_to_prolog_neg():
    example = Example("e_3", Atom("flies", ["c"]))
    prolog_neg_ex = example.to_prolog_neg()
    assert prolog_neg_ex == "neg(e_3,flies(c))."

### EQUALITIES TESTS
def test_equal_equalities():
    eq_1 = Equality("X","a")
    eq_2 = Equality("X","a")
    assert eq_1 == eq_2

def test_unequal_equalities():
    eq_1 = Equality("X","b")
    eq_2 = Equality("X","a")
    assert not eq_1 == eq_2