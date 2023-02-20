/* Flies Example */
my_rule(r_1,bird(X), [penguin(X)]).
my_rule(r_2,bird(a), []).
my_rule(r_3,bird(b), []).
my_rule(r_4,penguin(X), [superpenguin(X)]).
my_rule(r_5,penguin(c), []).
my_rule(r_6,penguin(d), []).
my_rule(r_7,superpenguin(e), []).
my_rule(r_8,superpenguin(f), []).
my_rule(r_9,flies(X), [bird(X), a1(X)]).
my_rule(r_10,c_a1(X), [penguin(X), a2(X)]).
my_rule(r_11,c_a2(X), [superpenguin(X)]).

% pos(e_1,flies(a)).
% pos(e_2,flies(b)).
% pos(e_3,flies(e)).
% pos(e_4,flies(f)).
% pos(e_5,c_a1(c)).
% pos(e_6,c_a1(d)).
% pos(e_7,c_a2(e)).
% pos(e_8,c_a2(f)).


% neg(e_9,flies(c)).
% neg(e_10,flies(d)).
% neg(e_11,c_a1(a)).
% neg(e_12,c_a1(b)).
% neg(e_13,c_a1(e)).
% neg(e_14,c_a1(f)).
% neg(e_15,c_a2(c)).
% neg(e_16,c_a2(d)).

my_asm(a1(X)).
my_asm(a2(X)).

contrary(a1(X),c_a1(X)).
contrary(a2(X),c_a2(X)).