% Rules:
my_rule(r1,bird(X),[penguin(X)]).
my_rule(r2,penguin(X),[superpenguin(X)]).
my_rule(r3,bird(X),[X=a]).
my_rule(r4,bird(X),[X=b]).
my_rule(r5,penguin(X),[X=c]).
my_rule(r6,penguin(X),[X=d]).
my_rule(r7,superpenguin(X),[X=e]).
my_rule(r8,superpenguin(X),[X=f]).

% Positive examples:
pos(p1, flies(a)).
pos(p2, flies(b)).
pos(p3, flies(e)).
pos(p4, flies(f)).

% Negative examples:
neg(n1, flies(c)).
neg(n2, flies(d)).