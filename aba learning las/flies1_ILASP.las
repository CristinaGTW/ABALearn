% Dimopoulos-Kakas 95
% ILASP syntax

%Background:
bird(X) :- penguin(X).
penguin(X) :- superpenguin(X).  %Corrected version
bird(a).
bird(b). 
penguin(c).
penguin(d).
superpenguin(e). 
superpenguin(f).

#modeh(flies(var(t1))).
#modeb(1,bird(var(t1))).
#modeb(1,penguin(var(t1))).
#modeb(1,superpenguin(var(t1))).

#constant(t1, a).
#constant(t1, b).
#constant(t1, c).
#constant(t1, d).
#constant(t1, e).
#constant(t1, f).
#maxv(2).

%E=#pos(E+,E-).
#pos({flies(a),flies(b),flies(e),flies(f)},
     {flies(c),flies(d)}).

% $ ILASP --version=2 flies1_ILASP.las 
% flies(V1) :- superpenguin(V1).
% flies(V1) :- bird(V1); not penguin(V1).

