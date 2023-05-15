% Background Knowledge 
my_rule(r1,quacker(A),[A=a]).
my_rule(r2,republican(A),[A=a]).
my_rule(r3,quacker(A),[A=b]).
my_rule(r4,republican(A),[A=b]).
my_rule(r_4,pacifist(A),[quacker(A),alpha1(A)]).
my_rule(r_9,c_alpha1(A),[republican(A),alpha2(A)]).
my_rule(r_15,c_alpha2(A),[pacifist(A)]).

% Positive Examples 

% Negative Examples 

% Assumptions 

% Contraries 
