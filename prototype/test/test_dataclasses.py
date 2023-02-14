from elements.components import Atom, Rule, Example

def test_parse_atom():
    atom = Atom.parse_atom("bird(a)")
    assert atom.predicate == "bird"
    assert atom.arguments == ["a"]

def test_atom_to_str():
    atom = Atom("bird", ["a"])
    atom_str = str(atom)
    assert atom_str == "bird(a)"

def test_parse_rule():
    rule = Rule.parse_rule("r_1:bird(X)<-penguin(X)")
    assert rule.rule_id == "r_1"
    assert rule.head == Atom("bird", ["X"])
    assert rule.body == [Atom("penguin", ["X"])]

def test_rule_to_str():
    rule = Rule("r_1", Atom("bird", ["X"]), [Atom("penguin", ["X"])])
    rule_str = str(rule)
    assert rule_str == "r_1:bird(X)<-penguin(X)"

def test_parse_example():
    example = Example.parse_example("e_1:flies(a)")
    assert example.example_id == "e_1"
    assert example.fact == Atom("flies", ["a"])

def test_example_to_str():
    example = Example("e_1", Atom("flies", ["a"]))
    example_str = str(example)
    assert example_str == "e_1:flies(a)"