% DK-95
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
plane(g).
plane(h).
plane(k).
plane(m).
damaged(k).
damaged(m).

#modeh(flies(var(t1))).
#modeb(1,bird(var(t1))).
#modeb(1,penguin(var(t1))).
#modeb(1,superpenguin(var(t1))).
#modeb(1,plane(var(t1))).
#modeb(1,damaged(var(t1))).

#constant(t1, a).
#constant(t1, b).
#constant(t1, c).
#constant(t1, d).
#constant(t1, e).
#constant(t1, f).
#constant(t1, g).
#constant(t1, h).
#constant(t1, k).
#constant(t1, m).
#maxv(2).

%E=#pos(E+,E-).
#pos({flies(a),flies(b),flies(e),flies(f),flies(g),flies(h)},
     {flies(c),flies(d),flies(k), flies(m)}).
     
% $ ILASP --version=2 flies2.las
% flies(V1) :- superpenguin(V1).
% flies(V1) :- not damaged(V1); plane(V1).
% flies(V1) :- bird(V1); not penguin(V1).

% Nontermination after minutes if 1 --> 100 and 2 --> 100

