from subprocess import Popen, PIPE

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



def get_pos_args(aba_framework, atom):
    aba_framework.create_file("done.pl")
    with Popen(['/bin/bash', '-c', f'sicstus -l prototype/resources/coverage.pl -l done.pl'], stdout=PIPE, stdin=PIPE, stderr=PIPE) as p:
        query = f"covered([{atom.predicate}(X)])."
        print(query)
        p.stdin.write(str.encode(query))
        (stdout,stderr) = p.communicate()
        p.stdin.close()
        output = stderr.decode("utf-8")
        result = output.splitlines()[-1]
    print(result)
    return result