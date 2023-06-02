from elements.components import Rule, Atom, Equality, Example


TRUE_VALUES = ["YES", "T", "TRUE", "1", 1, "WON", "POSITIVE"]
FALSE_VALUES = ["NO", "F", "FALSE", "0", 0, "NOWIN", "NEGATIVE"]


def row_to_learning_problem(
    row, headers, label, count, pos_ex_count, neg_ex_count, non_standard_values
) -> tuple[list[Rule], int]:
    rules = {}
    target = row[0]
    for val, attr in zip(row[1:-1], headers[1:-1]):
        val_str = val.upper()
        if val_str in TRUE_VALUES:
            rule_id = f"r{count}"
            rules[rule_id] = Rule(rule_id, Atom(attr, ["X"]), [Equality("X", target)])
            count += 1
        elif val_str not in FALSE_VALUES and val_str != "?":
            non_standard_values[attr] = val_str
            rule_id = f"r{count}"
            rules[rule_id] = Rule(
                rule_id, Atom(f"{attr}_{val_str}", ["X"]), [Equality("X", target)]
            )
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
