%Background
arc(X,Y) <- X=1,Y=3.
arc(X,Y) <- X=3,Y=7.
arc(X,Y) <- X=Y,Y=2.

%E+
path(1,1).
path(1,3).
path(3,7).
path(1,7).

%E-
path(2,1).
path(7,1).
path(7,3).

%----------- 

%Rote learning (four times)
path(X,Y) <- X=Y,Y=1.
path(X,Y) <- X=1,Y=3.
path(X,Y) <- X=3,Y=7.
path(X,Y) <- X=1,Y=7.


%-- Fold twice using
% arc(X,Y) <- X=1,Y=3.
% arc(X,Y) <- X=3,Y=7.

path(X,Y) <- X=Y,Y=1.
path(X,Y) <- arc(X,Y).
path(X,Y) <- arc(X,Y).   % Delete by subsumption
path(X,Y) <- X=1,Y=7.

%-- Remove equality Y=1
path(X,Y) <- X=Y.
path(X,Y) <- arc(X,Y).
path(X,Y) <- X=1,Y=7.

%%%% LOOK HERE %%%%  
%-- Fold using arc(X,V) <- X=1,V=3.  (after variable renaming)
path(X,Y) <- X=Y.
path(X,Y) <- arc(X,Y).
path(X,Y) <- arc(X,V), V=3, Y=7.

%-- Fold using  arc(V,Y) <- V=3, Y=7.  (after variable renaming)

path(X,Y) <- X=Y.
path(X,Y) <- arc(X,Y).
path(X,Y) <- arc(X,V), arc(V,Y).

%-- Fold using path(X,Y) <- arc(X,Y).  (after variable renaming)
path(X,Y) <- X=Y.
path(X,Y) <- arc(X,Y).
path(X,Y) <- arc(X,V), path(V,Y).

% The second rule could be removed by subsumption (to be checked)
% The final set of rules is the reflexive-transitive closure 
% of the arc relation.
