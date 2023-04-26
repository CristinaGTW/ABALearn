% Rules:
my_rule(r1,quacker(X),[X=a]).
my_rule(r2,republican(X),[X=a]).
my_rule(r3,quacker(X),[X=b]).
my_rule(r4,republican(X),[X=b]).

% Positive examples:
pos(p1, pacifist(a)).

% Negative examples:
neg(n1, pacifist(b)).