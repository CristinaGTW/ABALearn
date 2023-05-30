from strategy import abalearn
from prolog.config import set_up_abalearn
from datasets import parse_dataset
import sys
import time

DATASETS_FILE_MAP = {'acute': 'data/acute/acute.csv', 'autism': 'data/autism/autism.csv', 'krkp': 'data/krkp/krkp.csv','tictactoe': 'data/tictactoe/tictactoe.csv'}


if __name__ == "__main__":
    input = sys.argv[1]
    if input in DATASETS_FILE_MAP:
        prolog = set_up_abalearn(parse_dataset(DATASETS_FILE_MAP[input], input))
    else:
        prolog = set_up_abalearn(input)
    start_time = time.time()
    aba_framework = abalearn(prolog)
    print(aba_framework.get_learned_rules())
    print("--- Learning time: %s seconds ---" % (time.time() - start_time))
