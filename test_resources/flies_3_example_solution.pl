% Background Knowledge 
my_rule(r1,bird(A),[A=a]).
my_rule(r2,feathered(A),[A=a]).
my_rule(r3,bird(A),[A=a1]).
my_rule(r4,feathered(A),[A=a1]).
my_rule(r5,bird(A),[A=b]).
my_rule(r6,light(A),[A=b]).
my_rule(r7,bird(A),[A=b1]).
my_rule(r8,light(A),[A=b1]).
my_rule(r9,bird(A),[A=c]).
my_rule(r10,feathered(A),[A=c]).
my_rule(r11,brokenwings(A),[A=c]).
my_rule(r12,bird(A),[A=c1]).
my_rule(r13,feathered(A),[A=c1]).
my_rule(r14,brokenwings(A),[A=c1]).
my_rule(r15,bird(A),[A=d]).
my_rule(r16,light(A),[A=d]).
my_rule(r17,big(A),[A=d]).
my_rule(r18,bird(A),[A=d1]).
my_rule(r19,light(A),[A=d1]).
my_rule(r20,big(A),[A=d1]).
my_rule(r_29,flies(A),[bird(A),alpha1(A)]).
my_rule(r_54,c_alpha1(A),[big(A)]).
my_rule(r_62,c_alpha1(A),[feathered(A),alpha2(A)]).
my_rule(r_75,c_alpha2(A),[bird(A),alpha3(A)]).
my_rule(r_84,c_alpha3(A),[brokenwings(A)]).

% Assumptions 
my_asm(alpha1(A)).
my_asm(alpha2(A)).
my_asm(alpha3(A)).

% Contraries 
contrary(alpha1(A),c_alpha1(A)).
contrary(alpha2(A),c_alpha2(A)).
contrary(alpha3(A),c_alpha3(A)).
