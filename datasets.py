import csv
from elements.components import Example
from elements.aba_framework import ABAFramework
from csv_parsing.csv_utils import row_to_rules

def parse_acute():
    all_rules = []
    pos_exs = []
    neg_exs = []
    with open('data/acute/acute.csv') as f:
        reader = csv.reader(f)
        headers = next(reader)
        count = 0
        pos_ex_count = 0
        neg_ex_count = 0
        for row in reader:
            rules, count = row_to_rules(row, headers, count)
            all_rules += rules
            if row[-1] == 'yes':
                ex = Example(f"p{pos_ex_count}", f"acute({row[0]})")
                pos_exs.append(ex)
                pos_ex_count += 1
            else:
                ex = Example(f"n{neg_ex_count}", f"acute({row[0]})")
                neg_exs.append(ex)
                neg_ex_count += 1
    
    aba_framework = ABAFramework(all_rules,pos_exs, neg_exs,[],[],{},{},{})
    filename = 'data/acute/acute.pl'
    aba_framework.create_file(filename)
    return filename
