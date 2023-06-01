% Example from DK-95

% Background
my_rule(r1,bird(X),[X=a]).
my_rule(r2,feathered(X),[X=a]).
my_rule(r3,bird(X),[X=a1]).
my_rule(r4,feathered(X),[X=a1]).
my_rule(r5,bird(X),[X=b]).
my_rule(r6,light(X),[X=b]).
my_rule(r7,bird(X),[X=b1]).
my_rule(r8,light(X),[X=b1]).
my_rule(r9,bird(X),[X=c]).
my_rule(r10,feathered(X),[X=c]).
my_rule(r11,brokenwings(X),[X=c]).
my_rule(r12,bird(X),[X=c1]).
my_rule(r13,feathered(X),[X=c1]).
my_rule(r14,brokenwings(X),[X=c1]).
my_rule(r15,bird(X),[X=d]).
my_rule(r16,light(X),[X=d]).
my_rule(r17,big(X),[X=d]).
my_rule(r18,bird(X),[X=d1]).
my_rule(r19,light(X),[X=d1]).
my_rule(r20,big(X),[X=d1]).


% E+
pos(p1,flies(a)).
pos(p2,flies(b)).
pos(p3,flies(a1)).
pos(p4,flies(b1)).

% E-
neg(n1,flies(c)).
neg(n2,flies(d)).
neg(n3,flies(c1)).
neg(n4,flies(d1)).
