% Background Knowledge 
my_rule(r_11,robber(A),[seenAtBank(A),alpha2(A)]).
my_rule(r1,seenAtBank(A),[wasAtWork(A)]).
my_rule(r2,wasAtWork(A),[banker(A)]).
my_rule(r3,banker(A),[A=jane]).
my_rule(r4,banker(A),[A=david]).
my_rule(r5,seenAtBank(A),[A=ann]).
my_rule(r6,seenAtBank(A),[A=taylor]).
my_rule(r7,wasAtWork(A),[A=matt]).
my_rule(r_14,c_alpha1(A),[banker(A)]).
my_rule(r_20,c_alpha2(A),[banker(A)]).

% Positive Examples 

% Negative Examples 

% Assumptions 
my_asm(alpha1(ZA)).
my_asm(alpha2(ZA)).

% Contraries 
contrary(alpha1(ZA),c_alpha1(ZA)).
contrary(alpha2(ZA),c_alpha2(ZA)).
