% Background Knowledge
my_rule(r1,step(A,B),[A=1,B=2]).
my_rule(r2,step(A,B),[A=1,B=3]).
my_rule(r3,step(A,B),[A=2,B=4]).
my_rule(r4,step(A,B),[A=2,B=5]).
my_rule(r5,step(A,B),[A=4,B=6]).
my_rule(r6,step(A,B),[A=5,B=2]).
my_rule(r7,busy(A),[A=3]).
my_rule(r8,busy(A),[A=6]).
my_rule(r_12,free(A),[step(A,B)]).
my_rule(r_17,free(A),[step(B,A)]).

% Positive Examples
pos(p1,free(1)).
pos(p2,free(2)).
pos(p3,free(5)).

% Negative Examples
neg(n1,free(3)).
neg(n2,free(4)).
neg(n3,free(6)).

% Assumptions

% Contraries