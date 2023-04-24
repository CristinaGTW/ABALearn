% Background Knowledge 
my_rule(r_27,arc(A,B),[A=B]).
my_rule(r1,arc(A,B),[A=1,B=3]).
my_rule(r2,arc(A,B),[A=3,B=7]).
my_rule(r_7,path(A,B),[arc(A,B)]).
my_rule(r_23,path(A,B),[arc(C,B),arc(A,C)]).

% Positive Examples 

% Negative Examples 

% Assumptions 

% Contraries 
