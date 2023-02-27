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
    my_asm(Asm).
% (C,A) is an argument if there is a rule for C which can be applied,
% i.e. if the body literals are justified (derivable)
argument((Conc,Asm)) :-
    my_rule(RuleId,Conc,Body),
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

defendFrom( Attacker, OldAttackers) :-
  attacks( Defender, Attacker),
  \+ member( Attacker, OldAttackers),
  NewAttackers = [ Attacker| OldAttackers],  
  forall( attacks( X, Defender), defendFrom( X, NewAttackers)).

forall( P, Q) :-
  \+ ( P, \+ Q) .

attacks((ConcA,AsmA),(ConcB,AsmB)) :-
    argument((ConcA,AsmA)),
    contrary(OneAsm,ConcA),
    argument((ConcB,AsmB)),
    member(OneAsm,AsmB).
