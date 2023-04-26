
:-dynamic(p/1).
:-dynamic(q/1).
:-dynamic(r/2).

q(a).
q(c).
r(a,b).
r(b,c).
r(c,d).

p(X):-q(X),r(X,Y).

holds(true).
holds((A,B)):-holds(A),holds(B).
holds(Goal):-Goal \= true, Goal \= (_,_), clause(Goal, Body), holds(Body).

