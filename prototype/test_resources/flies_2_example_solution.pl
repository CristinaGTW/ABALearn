% Background Knowledge 
my_rule(r1,bird(A),[penguin(A)]).
my_rule(r2,bird(A),[A=a]).
my_rule(r3,bird(A),[A=b]).
my_rule(r4,penguin(A),[superpenguin(A)]).
my_rule(r5,penguin(A),[A=c]).
my_rule(r6,penguin(A),[A=d]).
my_rule(r7,superpenguin(A),[A=e]).
my_rule(r8,superpenguin(A),[A=f]).
my_rule(r9,plane(A),[A=g]).
my_rule(r10,plane(A),[A=h]).
my_rule(r11,plane(A),[A=k]).
my_rule(r12,plane(A),[A=m]).
my_rule(r13,damaged(A),[A=k]).
my_rule(r14,damaged(A),[A=m]).
my_rule(r_26,c_alpha1(A),[penguin(A),alpha2(A)]).
my_rule(r_29,c_alpha2(A),[superpenguin(A)]).
my_rule(r_40,c_alpha3(A),[damaged(A)]).
my_rule(r_19,flies(A),[bird(A),alpha1(A)]).
my_rule(r_37,flies(A),[plane(A),alpha3(A)]).

% Positive Examples 

% Negative Examples 

% Assumptions 
my_asm(alpha1(ZA)).
my_asm(alpha2(ZA)).
my_asm(alpha3(ZA)).

% Contraries 
contrary(alpha1(ZA),c_alpha1(ZA)).
contrary(alpha2(ZA),c_alpha2(ZA)).
contrary(alpha3(ZA),c_alpha3(ZA)).
