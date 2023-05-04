from elements.aba_framework import ABAFramework
from elements.components import Example
import subprocess

def covered(aba_framework: ABAFramework, example:Example) -> bool:
    aba_framework.to_asp("covered.txt")
    ex_str = example.get_predicate() + '('
    for arg in example.get_arguments():
        ex_str += arg + ','
    ex_str = ex_str[:-1]
    ex_str += ')'
    if ex_str not in aba_framework.language:
        return False
    return run_asp_for_aba(aba_framework.language[ex_str] + 1)

def run_asp_for_aba(example: str) -> bool:
    proc = subprocess.Popen(f'python aspforaba/aspforaba.py -p DC-CO -f covered.txt -a {example}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = proc.communicate()[0].decode()
    return result =='YES\n'
