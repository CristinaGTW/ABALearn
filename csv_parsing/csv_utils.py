from elements.components import Rule,Atom, Equality


def row_to_rules(row, headers, count) -> tuple[list[Rule],int]:
    rules = []
    target = row[0]
    row = row[1:-1]
    for i,attr in enumerate(headers[1:-1]):
        if i != 0:
            atom = Atom.parse_atom(attr + '_' + row[i] + '(A)')
        else:
            atom = Atom.parse_atom(attr + '_' + row[i].split('.')[0] + '(A)')
        eq = Equality('A',target)
        rules.append(Rule(f'r{count}', atom, [eq]))      
        count += 1  

    return (rules, count)
