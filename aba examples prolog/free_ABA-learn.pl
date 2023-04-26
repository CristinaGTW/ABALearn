% Background
step(1,2).
step(1,3).
step(2,4).
step(2,5).
step(4,6).
step(5,2).

busy(3).
busy(6).

% E+
free(1).
free(2).
free(5).

% E-
free(3).
free(4).
free(6).


% 1st Iteration

%-- Rote learning
free(X) :- X=1.

%-- Fold using step(X,Y) :- X=1, Y=2.
free(X) :- step(X,Y), Y=2.

%-- Equality removal 
% (some folds of Y=2 would have been also possible)
free(X) :- step(X,Y).

% Exceptions: +++

free(1) --> step(1,2); step(1,3)
free(2) --> step(2,4); step(2,5)
free(4) --> step(4,6)
free(5) --> step(5,2)

% Assumption Intro (undercutting) + RL
free(X) :- step(X,Y), a(Y).

c_a(Y) :- Y=6.

% Folding
a(Y) :- busy(Y).

% Learnt clauses: 

free(X) :- step(X,Y), a(Y).
c_a(Y) :- busy(Y).

*/
