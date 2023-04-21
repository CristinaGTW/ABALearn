% Background Knowledge 
my_rule(r1,step(A,B),[A=1,B=2]).
my_rule(r2,step(A,B),[A=1,B=3]).
my_rule(r3,step(A,B),[A=2,B=4]).
my_rule(r4,step(A,B),[A=2,B=5]).
my_rule(r5,step(A,B),[A=4,B=6]).
my_rule(r6,step(A,B),[A=5,B=2]).
my_rule(r7,busy(A),[A=3]).
my_rule(r8,busy(A),[A=6]).
my_rule(r_19,free(A),[step(A,B),alpha1(A,B)]).
my_rule(r_23,c_alpha1(A,B),[busy(B)]).

% Positive Examples 

% Negative Examples 

% Assumptions 
my_asm(alpha1(ZA,_5232)).

% Contraries 
contrary(alpha1(ZA,_5246),c_alpha1(ZA,_5246)).
