from subprocess import Popen, PIPE

def covered(input_file_path, atoms):
    with Popen(['/bin/bash', '-c', f'sicstus -l prototype/resources/coverage.pl -l {input_file_path}'], stdout=PIPE, stdin=PIPE, stderr=PIPE) as p:
        atoms_str = ""
        for atom in atoms:
            atoms_str += atom +','
        atoms_str = atoms_str[:-1]
        query = f"covered([{atoms_str}])."
        print(query)
        p.stdin.write(str.encode(query))
        (stdout,stderr) = p.communicate()
        p.stdin.close()
        output = stderr.decode("utf-8")
        result = output.splitlines()[-1]
    return result == "yes"
