% Flies example from DK-95

bird(X) :- penguin(X).
bird(X) :- X=a.
bird(X) :- X=b.
penguin(X) :- superpenguin(X).
penguin(X) :- X=c.
penguin(X) :- X=d.
superpenguin(X) :- X=e.
superpenguin(X) :- X=f.

% E+
flies(a).
flies(b).
flies(e).
flies(f).

% E-
flies(c).
flies(d).

%%%%---- First Iteration ----

%-- Rote learn

flies(A) :- A=a.
flies(A) :- A=b.
flies(A) :- A=e.
flies(A) :- A=f.


%-- fold flies(A) :- A=a. using bird(X) :- X=a.

flies(A) :- bird(A). 

%-- subsume
flies(A) :- A=b.
flies(A) :- A=e.
flies(A) :- A=f.

% covered negative examples:
flies(c).
flies(d).

%-- introduce assumption
flies(A) :- bird(A), a1(A).

% with contrary c_a1 and positive examples E1+:
c_a1(c).
c_a1(d).

% and negative examples E1-:
c_a1(a).
c_a1(b).
c_a1(e).
c_a1(f).

%%%%---- 2nd Iteration ----

%-- Rote learn
c_a1(A) :- A=c.
c_a1(A) :- A=d.

%-- fold c_a1(A) :- A=c. using penguin(X) :- X=c.
c_a1(A) :- penguin(A).

% subsume 
c_a1(A) :- A=d.

% covered negative examples:
c_a1(A) :- A=e.
c_a1(A) :- A=f.

%-- introduce assumption
c_a1(A) :- penguin(A), a2(A).

% with contrary c_a2
% positive examples:
c_a2(e).
c_a2(f).

% negative examples:
c_a2(c).
c_a2(d).

%%%%---- 3rd Iteration ----

%-- Rote learn

c_a2(X) :- X=e.
c_a2(X) :- X=f.

%-- fold c_a2(X) :- X=e. using superpenguin(X) :- X=e.

c_a2(A) :- superpenguin(A).

%-- subsume
c_a2(X) :- X=f.

% Final learned ABA

flies(A) :- bird(A), a1(A).
c_a1(A) :- penguin(A), a2(A).
c_a2(A) :- superpenguin(A).

