from subprocess import Popen, PIPE
import os

SAFETY_FACTOR = 5

def covered(input_file_path, exs):
    with Popen(['/bin/bash', '-c', f'sicstus -l prototype/resources/coverage.pl -l {input_file_path}'], stdout=PIPE, stdin=PIPE, stderr=PIPE) as p:
        exs_str = ""
        for ex in exs:
            exs_str += str(ex.fact) +','
        exs_str = exs_str[:-1]
        query = f"covered([{exs_str}])."
        p.stdin.write(str.encode(query))
        (stdout,stderr) = p.communicate()
        p.stdin.close()
        output = stderr.decode("utf-8")
        result = output.splitlines()[-1]
    return result == "yes"



def get_covered_solutions(aba_framework, atom):
    aba_framework.create_file("check.pl")
    sols = []
    size = aba_framework.get_language_size() * SAFETY_FACTOR
    with Popen(['/bin/bash', '-c', f'sicstus -l prototype/resources/coverage.pl -l check.pl'], stdout=PIPE, stdin=PIPE, stderr=PIPE) as p:
        query = f"covered([{atom}])."
        for _ in range(size):
            query += "\n;"
        p.stdin.write(str.encode(query))
        (stdout,stderr) = p.communicate()
        output = stderr.decode("utf-8")
        while output.find(" = ") != -1:
            (output, sol) = get_sol(output, atom.arguments)
            sols.append(sol)
    os.remove("check.pl") 
    return sols


def get_sol(output, variables):
    sol = []
    for var in variables:
        idx = output.find(f"{var} = ")
        idx_2 = output[idx:].find("?")
        sol.append(output[(idx+4):(idx + idx_2-1)])
        output = output[(idx + idx_2):]
    return (output, tuple(sol))


