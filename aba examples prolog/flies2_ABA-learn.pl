% Example from DK-95

% Background

bird(X) :- penguin(X).
bird(a).
bird(b).
penguin(X) :- superpenguin(X).
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

% E+
flies(a).
flies(b).
flies(e).
flies(f).
flies(g).
flies(h).

% E-
flies(c).
flies(d).
flies(k).
flies(m).

% 1s Iteration

%------ Rote learn
flies(X) :- X=a.
flies(X) :- X=b.
flies(X) :- X=e.
flies(X) :- X=f.
flies(X) :- X=g.
flies(X) :- X=h.

%------ Fold using bird(X) :- X=a.

flies(X) :- bird(X).

%------ Subsumes
flies(X) :- X=b.
flies(X) :- X=e.
flies(X) :- X=f.

%------ Fold using plane(X) :- X=g.

flies(X) :- plane(X).

%------ Subsumes
flies(X) :- X=h.

% Currently learnt rules:

flies(X) :- bird(X).
flies(X) :- plane(X).

% negative examples covered
% by first rule
flies(c).
flies(d).
% by second rule
flies(k).
flies(m).


%------ Assumption Intro

flies(X) :- bird(X), a1(X).  
flies(X) :- plane(X), a2(X).

% where contrary of a1 is c_a1 and contrary of a2 is c_a2.

% E1+:
c_a1(c).
c_a1(d).
c_a2(k).
c_a2(m).

% E1-:
c_a1(a).
c_a1(b).
c_a1(e).
c_a1(f).
c_a2(g).
c_a2(h).

% 2nd iteration

%------ Rote learning
c_a1(X) :- X=c.
c_a1(X) :- X=d.
c_a2(X) :- X=k.
c_a2(M) :- X=m.


%------ Fold using penguin(X) :- X=c. and damaged(X) :- X=k. followed by Subsumption

c_a1(X) :- penguin(X).   % c,d / e,f
c_a2(X) :- damaged(X).   % k,m 

% negative examples covered
c_a1(e).
c_a1(f).

%------ Assumption intro
c_a1(X) :- penguin(X), a3(X). 

% contrary of a3 is c_a3 

%E2+
c_a3(e).
c_a3(f).

%E2-
c_a3(c).
c_a3(d).


% 3rd iteration

%------ Rote learn
c_a3(X) :- X=e.
c_a3(X) :- X=f.

%------  Fold and subsumption
c_a3(X) :- superpenguin(X).

% Final learnt rules
flies(X) :- bird(X), a1(X).  
flies(X) :- plane(X), a2(X).
c_a1(X) :- penguin(X), a3(X). 
c_a2(X) :- damaged(X). 
c_a3(X) :- superpenguin(X).
