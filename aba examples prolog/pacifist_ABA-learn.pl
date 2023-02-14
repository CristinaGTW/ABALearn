% Background
quacker(X) :- X=a.
quacker(X) :- X=b.

republican(X) :- X=b.
republican(X) :- X=a.

E+:
pacifist(a).

E-:
pacifist(b).

% 1st Iteration

%-- root learn
pacifist(X) :- X=a.

%-- fold using quacker(X) :- X=a.
pacifist(X) :- quacker(X).

% negative example pacifist(b) is covered

%-- Assumption Intro
pacifist(X) :- quacker(X), normal_quacker(X).

%-- where contrary of normal_quacker is abnormal_quacker
% Positive examples:
abnormal_quacker(b).

% Negative examples:
abnormal_quacker(a).

% 2nd Iteration
%-- root learn
abnormal_quacker(X) :- X=b.

% (fold using quacker(X) :- X=b would lead to 
%  abnormal_quacker(X) :- quacker(X).
%  NOT GOOD, why? )

% fold using republican(X) :- X=b.

abnormal_quacker(X) :- republican(X).  

% Negative example abnormal_quacker(a) is covered

%-- Assumption Intro
abnormal_quacker(X) :- republican(X), normal_republican(X).  

%-- where contrary of normal_republican is abnormal_republican
% Positive Examples:
abnormal_republican(a).

% Negative Examples:
abnormal_republican(b).

% 3rd Iteration

%-- root learn
abnormal_republican(X) :- X=a.

%-- fold using quacker(X) :- X=a.
abnormal_republican(X) :- quacker(X).

% Negative example abnormal_republican(b) is covered

%-- Assumption Intro
abnormal_republican(X) :- quacker(X), normal_quacker(X).

% Note: we re-use normal_quacker

%-- Fold
abnormal_republican(X) :- pacifist(X).


%Final:
pacifist(X) :- quacker(X), normal_quacker(X).
abnormal_quacker(X) :- republican(X), normal_republican(X).
abnormal_republican(X) :- pacifist(X).
