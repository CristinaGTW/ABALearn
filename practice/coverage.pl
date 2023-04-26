% Assumes that the semantics is sceptical - grounded extensions
:- use_module(library(lists)).
:- use_module(library(sets)).
:- use_module(library(ordsets)).

% Examples are covered if every example is accepted
covered([]).
covered([Ex|RestEx]):-
    accepted(Ex),
        covered(RestEx).



%%%%%%DEDUCTION FROM WHAT HAS BEEN LEARNT ALREADY (THE CURRENT BACKGROUND)
% An example is accepted if there is an argument for the example and the example is grounded
accepted(Ex):-
    argument((Ex,Support)),
    grounded((Ex,Support)).



% (C,[C]) is an argument if C is an assumption
argument((Asm,[Asm])) :-
    myAsm(Asm).

% (C,A) is an argument if there is a rule for C which can be applied,
% i.e. if the body literals are justified (derivable)
argument((Conc,Asm)) :-
    myRule(Conc,Body), % There is a rule for C
    justified(Body,Asm). % The body is justified by the assumptions

% The empty set of literals is always justified (derivable) by the empty set
justified([],[]).

% A literal Body1 is justified (derivable) by a set Asm where (Body1,Asm) is
% an argument
justified([Body1|RestBody],Asm) :-
    argument((Body1,Asm1)),
    justified(RestBody,Asm2),
    union(Asm1,Asm2,Asm). % Asm is the union of all the arguments for the literals in the Body


% An argument is grounded if all arguments that attack it are not defended by any argument
grounded( A) :-
  argument( A),
  forall( attacks( X, A), defendFrom( X, [])). 

% Attacker defends OldAttackers 
defendFrom( Attacker, OldAttackers) :-
  \+ attacks( Defender, Attacker).

defendFrom( Attacker, OldAttackers) :-
  attacks( Defender, Attacker),
  \+ member( Attacker, OldAttackers),
  NewAttackers = [ Attacker| OldAttackers],  
  forall( attacks( X, Defender), defendFrom( X, NewAttackers)).


forall( P, Q) :-
  \+ ( P, \+ Q)
  .


% first is the contrary of an assumption in the second
% An argument A attacks another argument B
% if there is an assumption in B that is the contrary of the conclusion of A
attacks((ConcA,AsmA),(ConcB,AsmB)) :-
    argument((ConcA,AsmA)),
    contrary(OneAsm,ConcA),
    argument((ConcB,AsmB)),
    member(OneAsm,AsmB).
