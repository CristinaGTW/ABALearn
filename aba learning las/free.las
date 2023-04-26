%B
% Background
step(1,2).
step(1,3).
step(2,4).
step(2,5).
%step(3,2).
step(4,6).
step(5,2).

busy(3).
busy(6).

#modeh(free(var(node))).
#modeb(1,step(var(node),var(node))).
#modeb(1,busy(var(node))).

#constant(node, 1).
#constant(node, 2).
#constant(node, 3).
#constant(node, 4).
#constant(node, 5).
#constant(node, 6).

node(1..6).

#maxv(5).

% E+: {free(1),free(2),free(5)}
% E-: {free(3),free(4),free(6)}
% #pos(E+,E-).

#pos({free(1),free(2),free(5)},{free(3),free(4),free(6)}).
 
% ILASP --version=2 free.las
% free(V1) :- not busy(V2); step(V1,V2).
%
% If we add step(3,2)
% then UNSATISFIABLE

% If we change mode to
%    #modeb(2,step(var(node),var(node))).
%    #modeb(2,busy(var(node))).
% then (1.3s)
% free(V1) :- step(V1,V2); step(V2,V3).
% 

