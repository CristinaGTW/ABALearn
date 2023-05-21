% Background Knowledge 
my_rule(r1,arc(A,B),[A=1,B=3]).
my_rule(r2,arc(A,B),[A=3,B=7]).
my_rule(r3,arc(A,B),[A=B,B=2]).
my_rule(r_5,path(A,B),[A=B]).
my_rule(r_17,path(A,B),[arc(A,B)]).
my_rule(r_29,path(A,B),[path(A,C),path(C,B)]).

% Assumptions 

% Contraries 
