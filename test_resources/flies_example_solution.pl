% Background Knowledge 
my_rule(r1,bird(A),[penguin(A)]).
my_rule(r2,penguin(A),[superpenguin(A)]).
my_rule(r3,bird(A),[A=a]).
my_rule(r4,bird(A),[A=b]).
my_rule(r5,penguin(A),[A=c]).
my_rule(r6,penguin(A),[A=d]).
my_rule(r7,superpenguin(A),[A=e]).
my_rule(r8,superpenguin(A),[A=f]).
my_rule(r_13,flies(A),[bird(A),alpha1(A)]).
my_rule(r_22,c_alpha1(A),[penguin(A),alpha2(A)]).
my_rule(r_29,c_alpha2(A),[superpenguin(A)]).

% Positive Examples 

% Negative Examples 

% Assumptions 
my_asm(alpha1(A)).
my_asm(alpha2(A)).

% Contraries 
contrary(alpha1(A),c_alpha1(A)).
contrary(alpha2(A),c_alpha2(A)).
