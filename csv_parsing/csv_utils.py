from elements.components import Rule, Atom, Equality, Example


def row_to_learning_problem(row, headers, label, count, pos_ex_count, neg_ex_count) -> tuple[list[Rule], int]:
    rules = []
    target = row[0]
    for val, attr in zip(row[1:-1], headers[1:-1]):
        if val == 'yes' or val == '1':
            rules.append(Rule(f'r{count}', Atom(
                attr, ['X']), [Equality('X', target)]))
            count += 1

    if row[-1] == 'yes':
        pos_flag = True
        ex = Example(f"p{pos_ex_count}", Atom(label, [target]))
        pos_ex_count += 1
    else:
        pos_flag = False
        ex = Example(f"n{neg_ex_count}", Atom(label, [target]))
        neg_ex_count += 1

    return rules, pos_flag, ex, count, pos_ex_count, neg_ex_count
