% Dimopoulos-Kakas 95
% ILASP syntax

%Background:
bird(X) :- penguin(X).
penguin(X) :- superpenguin(X).
bird(a).
bird(b).
penguin(c).
penguin(d).
superpenguin(e).
superpenguin(f).

#modeh(flies(var(t))).
#modeb(1,bird(var(t))).
#modeb(1,penguin(var(t))).
#modeb(1,superpenguin(var(t))).

#constant(t, a).
#constant(t, b).
#constant(t, c).
#constant(t, d).
#constant(t, e).
#constant(t, f).
#maxv(2).

%E=#pos(E+,E-).
#pos({flies(a), flies(b), flies(e), flies(f)},
     {flies(c), flies(d)}).
