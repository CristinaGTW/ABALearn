% Background Knowledge 
my_rule(r1,bird(A),[penguin(A)]).
my_rule(r2,penguin(A),[superpenguin(A)]).
my_rule(r3,bird(a),[]).
my_rule(r4,bird(b),[]).
my_rule(r5,penguin(c),[]).
my_rule(r6,penguin(d),[]).
my_rule(r7,superpenguin(e),[]).
my_rule(r8,superpenguin(f),[]).
my_rule(r_2,flies(b),[]).
my_rule(r_3,flies(e),[]).
my_rule(r_4,flies(f),[]).
my_rule(r_7,flies(A),[bird(A),alpha1(A)]).

% Positive Examples 
pos(p1,flies(a)).
pos(p2,flies(b)).
pos(p3,flies(e)).
pos(p4,flies(f)).

% Negative Examples 
neg(n1,flies(c)).
neg(n2,flies(d)).

% Assumptions 
my_asm(alpha1(ZA)).

% Contraries 
contrary(alpha1(ZA),c_alpha1(ZA)).
