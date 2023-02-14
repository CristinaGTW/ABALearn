%assumes that the semantics is sceptical - grounded extensions

:- use_module(library(lists)).
:- use_module(library(sets)).
:- use_module(library(ordsets)).


covered([]).
covered([Ex|RestEx]):-
    accepted(Ex),
        covered(RestEx).

%%%%%%DEDUCTION FROM WHAT HAS BEEN LEARNT ALREADY (THE CURRENT BACKGROUND)
accepted(Ex):-
    argument((Ex,Support)),
    grounded((Ex,Support)).

% (C,[C]) is an argument if C is an assumption
argument((Asm,[Asm])) :-
    myAsm(Asm).
% (C,A) is an argument if there is a rule for C which can be applied,
% i.e. if the body literals are justified (derivable)
argument((Conc,Asm)) :-
    myRule(Conc,Body),
    justified(Body,Asm).
% the empty    set of literals is always justified (derivable) by the empty set
justified([],[]).
% a literal Body1 is justified (derivable) by a set Asm where (Body1,Asm) is
% an argument
justified([Body1|RestBody],Asm) :-
    argument((Body1,Asm1)),
    justified(RestBody,Asm2),
    union(Asm1,Asm2,Asm).

%checking whether A is an argument belonging to the grounded extension
grounded( A) :-
  argument( A),
  forall( attacks( X, A), defendFrom( X, [])).  

% argument(a). argument(b). argument(c). attacks(b,a). attacks(c,b). 
% :-? grounded(c). Yes
% :-? grounded(b). 
% :-? defendFrom(c,[]). No
% :-? grounded(a).
% :-? defendFrom(b,[]). Yes

defendFrom( Attacker, OldAttackers) :-
  attacks( Defender, Attacker),
  \+ member( Attacker, OldAttackers),
  NewAttackers = [ Attacker| OldAttackers],  
  forall( attacks( X, Defender), defendFrom( X, NewAttackers)).

forall( P, Q) :-
  \+ ( P, \+ Q) .

% first is the contrary of an assumption in the second
attacks((ConcA,AsmA),(ConcB,AsmB)) :-
    argument((ConcA,AsmA)),
    contrary(OneAsm,ConcA),
    argument((ConcB,AsmB)),
    member(OneAsm,AsmB).




/*

Input syntax example:

% an example of syntax



myAsm(normal_bird(X)). % this is how we write assumptions
contrary(normal_bird(X), abnormal_bird(X)).  % this is how we write contraries of assumptions: the assumption is the first argument, the contrary the second



myRule(bird(a),[]). % this is how we write facts, the empty body is an empty list
myRule(flies(X),[bird(X)]).  % this is how we write rules, bodies are lists



posEx(flies(a)). %this is how we write positive examples, one-by-one
negEx(flies(b)). %this is how we write negative examples, one-by-one

*/


/* Flies Example */
myRule(bird(X), [penguin(X)]).
myRule(bird(a), []).
myRule(bird(b), []).
myRule(penguin(X), [superpenguin(X)]).
myRule(penguin(c), []).
myRule(penguin(d), []).
myRule(superpenguin(e), []).
myRule(superpenguin(f), []).
myRule(flies(X), [bird(X), a1(X)]).
myRule(c_a1(X), [penguin(X), a2(X)]).
myRule(c_a2(X), [superpenguin(X)]).

posEx(flies(a)).
posEx(flies(b)).
posEx(flies(e)).
posEx(flies(f)).
posEx(c_a1(c)).
posEx(c_a1(d)).
posEx(c_a2(e)).
posEx(c_a2(f)).


negEx(flies(c)).
negEx(flies(d)).
negEx(c_a1(a)).
negEx(c_a1(b)).
negEx(c_a1(e)).
negEx(c_a1(f)).
negEx(c_a2(c)).
negEx(c_a2(d)).

myAsm(a1(X)).
myAsm(a2(X)).

contrary(a1(X),c_a1(X)).
contrary(a2(X),c_a2(X)).