from strategy import abalearn
from prolog.config import set_up_abalearn
from datasets import parse_acute
import sys
if __name__ == "__main__":
    input = sys.argv[1]
    if input == 'acute':
        prolog = set_up_abalearn(parse_acute())
    else:
        prolog = set_up_abalearn(input)
    abalearn(prolog)
