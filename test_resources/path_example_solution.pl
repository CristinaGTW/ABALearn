% Background Knowledge 
my_rule(r1,arc(A,B),[A=1,B=3]).
my_rule(r2,arc(A,B),[A=3,B=7]).
my_rule(r3,arc(A,B),[A=B,B=2]).
my_rule(r_49,path(A,B),[arc(C,B),arc(A,C)]).
my_rule(r_54,path(A,B),[A=1,B=1]).
my_rule(r_55,path(A,B),[A=1,B=7]).

% Assumptions 
my_asm(alpha1(A,B)).

% Contraries 
contrary(alpha1(A,B),c_alpha1(A,B)).
