% Example from DK-95

% Background

my_rule(r1,bird(X),[penguin(X)]).
my_rule(r2,bird(X),[X=a]).
my_rule(r3,bird(X),[X=b]).
my_rule(r4,penguin(X),[superpenguin(X)]).
my_rule(r5,penguin(X),[X=c]).
my_rule(r6,penguin(X),[X=d]).
my_rule(r7,superpenguin(X),[X=e]).
my_rule(r8,superpenguin(X),[X=f]).
my_rule(r9,plane(X),[X=g]).
my_rule(r10,plane(X),[X=h]).
my_rule(r11,plane(X),[X=k]).
my_rule(r12,plane(X),[X=m]).
my_rule(r13,damaged(X),[X=k]).
my_rule(r14,damaged(X),[X=m]).

% E+
pos(p1,flies(a)).
pos(p2,flies(b)).
pos(p3,flies(e)).
pos(p4,flies(f)).
pos(p5,flies(g)).
pos(p6,flies(h)).

% E-
neg(n1,flies(c)).
neg(n2,flies(d)).
neg(n3,flies(k)).
neg(n4,flies(m)).
