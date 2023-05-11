from strategy import abalearn
from prolog.config import set_up_abalearn
from datasets import parse_acute
import sys

DATASET_PARSE_MAP = {'acute': parse_acute}


if __name__ == "__main__":
    input = sys.argv[1]
    if input in DATASET_PARSE_MAP:
        prolog = set_up_abalearn(DATASET_PARSE_MAP[input]())
    else:
        prolog = set_up_abalearn(input)
    abalearn(prolog)
