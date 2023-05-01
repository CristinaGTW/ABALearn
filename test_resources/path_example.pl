%Background
my_rule(r1,arc(X,Y),[X=1,Y=3]).
my_rule(r2,arc(X,Y),[X=3,Y=7]).
my_rule(r3,arc(X,Y),[X=Y,Y=2]).

%E+
pos(p1,path(1,1)).
pos(p2,path(1,3)).
pos(p3,path(3,7)).
pos(p4,path(1,7)).

%E-
neg(n1,path(2,1)).
neg(n2,path(7,1)).
neg(n3,path(7,3)).
