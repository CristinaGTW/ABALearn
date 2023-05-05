% Background Knowledge 
my_rule(r1,quacker(A),[A=a]).
my_rule(r2,republican(A),[A=a]).
my_rule(r3,quacker(A),[A=b]).
my_rule(r4,republican(A),[A=b]).
my_rule(r_8,c_alpha1(A),[republican(A),alpha2(A)]).
my_rule(r_14,c_alpha2(A),[pacifist(A),alpha4(A)]).
my_rule(r_16,c_alpha4(A),[quacker(A)]).
my_rule(r_18,pacifist(A),[c_alpha4(A),alpha1(A)]).

% Positive Examples 

% Negative Examples 

% Assumptions 
my_asm(alpha1(A)).
my_asm(alpha2(A)).
my_asm(alpha4(A)).

% Contraries 
contrary(alpha1(A),c_alpha1(A)).
contrary(alpha2(A),c_alpha2(A)).
contrary(alpha4(A),c_alpha4(A)).
