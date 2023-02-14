%Background
arc(1,3).
arc(3,7).
arc(2,2).

#modeh(path(var(t1),var(t1))).
#modeb(1,arc(var(t1),var(t1))).
#modeb(1,path(var(t1),var(t1))).

#constant(t1, 1).
#constant(t1, 2).
#constant(t1, 3).
#constant(t1, 7).
#maxv(3).

%E = #pos(E+,E-).
#pos({path(1,1),path(1,3),path(1,7),path(3,7)},
     {path(2,1),path(7,1),path(7,3)}).


% $ ILASP --version=2 path_ILASP.las 
% path(V1,V1) :- arc(V1,V2).
% path(V1,V2) :- arc(V3,V2); path(V1,V3).


