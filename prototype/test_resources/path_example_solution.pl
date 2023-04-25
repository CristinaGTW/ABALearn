% Background Knowledge 
my_rule(r1,arc(A,B),[A=1,B=3]).
my_rule(r2,arc(A,B),[A=3,B=7]).
my_rule(r3,arc(A,B),[A=B,B=2]).
my_rule(r_23,path(A,B),[arc(C,B),arc(A,C)]).
my_rule(r_5,path(A,B),[A=B]).
my_rule(r_7,path(A,B),[arc(A,B)]).

% Positive Examples 

% Negative Examples 

% Assumptions 

% Contraries 
