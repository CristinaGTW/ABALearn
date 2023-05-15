import csv
from elements.aba_framework import ABAFramework
from csv_parsing.csv_utils import row_to_learning_problem


def parse_dataset(data_file, label):
    all_rules = []
    pos_exs = []
    neg_exs = []
    with open(data_file) as f:
        reader = csv.reader(f)
        headers = next(reader)
        count = 0
        pos_ex_count = 0
        neg_ex_count = 0
        non_standard_values = {}
        for row in reader:
            rules, pos_flag, ex, count, pos_ex_count, neg_ex_count, non_standard_values = row_to_learning_problem(row, headers, label, count, pos_ex_count, neg_ex_count, non_standard_values)
            all_rules += rules
            if pos_flag:
                pos_exs.append(ex)
            else:
                neg_exs.append(ex)
    
    aba_framework = ABAFramework(all_rules,pos_exs, neg_exs,[],[],{},{},{})
    filename = f'{label}.pl'
    aba_framework.create_file(filename)
    return filename
