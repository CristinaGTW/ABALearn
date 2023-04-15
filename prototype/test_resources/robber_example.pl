% Rules:
my_rule(r1,seenAtBank(X),[wasAtWork(X)]).
my_rule(r2,wasAtWork(X),[banker(X)]).
my_rule(r3,banker(X),[X=jane]).
my_rule(r4,banker(X),[X=david]).
my_rule(r5,seenAtBank(X),[X=ann]).
my_rule(r6,seenAtBank(X),[X=taylor]).
my_rule(r7,wasAtWork(X),[X=matt]).

% Positive examples:
pos(p1, robber(matt)).
pos(p2, robber(ann)).
pos(p3, robber(taylor)).

% Negative examples:
neg(n1, robber(jane)).
neg(n2, robber(david)).