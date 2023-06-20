from strategy import abalearn
from prolog.config import set_up_abalearn
from datasets import parse_dataset
import sys
import time

DATASETS_FILE_MAP = {
    "acute": "data/acute/acute.csv",
    "autism": "data/autism/autism.csv",
    "krkp": "data/krkp/krkp.csv",
    "tictactoe": "data/tictactoe/tictactoe.csv",
}


if __name__ == "__main__":
    input = sys.argv[1]
    if input[-4:] == '.csv':
        prolog = set_up_abalearn(parse_dataset(input))
    else:
        prolog = set_up_abalearn(input)
    start_time = time.time()
    aba_framework = abalearn(prolog)
    end_time = time.time()
    print(aba_framework.get_learned_rules())
    print("--- Learning time: %s seconds ---" % (end_time - start_time))
