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
pos(p_1,c_alpha1(c)).
pos(p_2,c_alpha1(d)).

% Negative Examples 
neg(n_1,c_alpha1(a)).
neg(n_2,c_alpha1(b)).
neg(n_3,c_alpha1(e)).
neg(n_4,c_alpha1(f)).

% Assumptions 
my_asm(alpha1(ZA)).

% Contraries 
contrary(alpha1(ZA),c_alpha1(ZA)).
