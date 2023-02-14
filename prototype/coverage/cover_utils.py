from subprocess import Popen, PIPE


def covered(atom):
    with Popen(['/bin/bash', '-c', 'sicstus -l prototype/resources/coverage.pl'], stdout=PIPE, stdin=PIPE, stderr=PIPE) as p:
        query = f"covered([{atom}])."
        p.stdin.write(str.encode(query))
        (stdout,stderr) = p.communicate()
        p.stdin.close()
        output = stderr.decode("utf-8")
        result = output.splitlines()[-1]
    return result == "yes"
