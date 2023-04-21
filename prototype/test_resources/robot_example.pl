% Rules:
my_rule(r1,step(X,Y),[X=1, Y=2]).
my_rule(r2,step(X,Y),[X=1, Y=3]).
my_rule(r3,step(X,Y),[X=2, Y=4]).
my_rule(r4,step(X,Y),[X=2, Y=5]).
my_rule(r5,step(X,Y),[X=4, Y=6]).
my_rule(r6,step(X,Y),[X=5, Y=2]).
my_rule(r7,busy(X), [X=3]).
my_rule(r8,busy(X), [X=6]).

% Positive examples:
pos(p1, free(1)).
pos(p2, free(2)).
pos(p3, free(5)).

% Negative examples:
neg(n1, free(3)).
neg(n2, free(4)).
neg(n3, free(6)).