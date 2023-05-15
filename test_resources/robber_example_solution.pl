% Background Knowledge 
my_rule(r1,seenAtBank(A),[wasAtWork(A)]).
my_rule(r2,wasAtWork(A),[banker(A)]).
my_rule(r3,banker(A),[A=jane]).
my_rule(r4,banker(A),[A=david]).
my_rule(r5,seenAtBank(A),[A=ann]).
my_rule(r6,seenAtBank(A),[A=taylor]).
my_rule(r7,wasAtWork(A),[A=matt]).
my_rule(r_11,robber(A),[seenAtBank(A),alpha2(A)]).
my_rule(r_16,c_alpha1(A),[banker(A)]).
my_rule(r_24,c_alpha2(A),[banker(A)]).

% Positive Examples 

% Negative Examples 

% Assumptions 
my_asm(alpha1(A)).
my_asm(alpha2(A)).

% Contraries 
contrary(alpha1(A),c_alpha1(A)).
contrary(alpha2(A),c_alpha2(A)).
