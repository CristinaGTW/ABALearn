from elements.components import Rule, Atom, Equality, Example


TRUE_VALUES = ['YES', 'T', 'TRUE', '1', 1, 'WON']
FALSE_VALUES = ['NO', 'F', 'FALSE', '0', 0, 'NOWIN']

def row_to_learning_problem(row, headers, label, count, pos_ex_count, neg_ex_count, non_standard_values) -> tuple[list[Rule], int]:
    rules = []
    target = row[0]
    for val, attr in zip(row[1:-1], headers[1:-1]):
        val_str = val.upper()
        if attr.upper() == 'GENDER':
            if val_str == 'M' or val_str == 'MALE':
                rules.append(Rule(f'r{count}', Atom(
                'male', ['X']), [Equality('X', target)]))
                count += 1
        else:
            if val_str in TRUE_VALUES:
                rules.append(Rule(f'r{count}', Atom(
                    attr, ['X']), [Equality('X', target)]))
                count += 1
            elif val_str not in FALSE_VALUES:
                if attr not in non_standard_values:
                    non_standard_values[attr] = val_str
                    rules.append(Rule(f'r{count}', Atom(
                    f'{attr}_{val_str}', ['X']), [Equality('X', target)]))
                    count += 1
                elif val_str == non_standard_values[attr]:
                    rules.append(Rule(f'r{count}', Atom(
                    f'{attr}_{val_str}', ['X']), [Equality('X', target)]))
                    count += 1

    if row[-1].upper() in TRUE_VALUES:
        pos_flag = True
        ex = Example(f"p{pos_ex_count}", Atom(label, [target]))
        pos_ex_count += 1
    else:
        pos_flag = False
        ex = Example(f"n{neg_ex_count}", Atom(label, [target]))
        neg_ex_count += 1

    return rules, pos_flag, ex, count, pos_ex_count, neg_ex_count, non_standard_values
