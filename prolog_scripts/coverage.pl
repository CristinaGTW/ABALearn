%assumes that the semantics is sceptical - grounded extensions

:- use_module(library(lists)).
:- use_module(library(ordsets)).

:- dynamic my_asm/1, contrary/2.


%%%%%%DEDUCTION FROM WHAT HAS BEEN LEARNT ALREADY (THE CURRENT BACKGROUND)
accepted(Ex, Rules, Support):-
	argument((Ex,Support), Rules),
	grounded((Ex,Support)),
	numbervars((Ex,Support)).

% (C,[C]) is an argument if C is an assumption 
argument((Asm,[Asm]),[]) :-
	my_asm(Asm).
% (C,A) is an argument if there is a rule for C which can be applied,
% i.e. if the body literals are justified (derivable)
argument((Conc,Asm), [RuleId|Rules]) :-
	my_rule(RuleId,Conc,Body),
	justified(Body,Asm,Rules).

% the empty	set of literals is always justified (derivable) by the empty set
justified([],[],[]).

justified([X=X|RestBody], Asm, Rules) :-
	justified(RestBody,Asm,Rules).

% a literal Body1 is justified (derivable) by a set Asm where (Body1,Asm) is
% an argument
justified([Body1|RestBody],Asm, Rules) :-
	argument((Body1,Asm1),Rules1),
	justified(RestBody,Asm2,Rules2),
	append(Rules1,Rules2,Rules),
	ord_union(Asm1,Asm2,Asm).

grounded( A) :-
  argument( A,_),
  forall( attacks( X, A), defendFrom( X, [])).  
  
defendFrom( Attacker, OldAttackers) :-
  attacks( Defender, Attacker),
  \+ member( Attacker, OldAttackers),
  NewAttackers = [ Attacker| OldAttackers],  
  forall( attacks( X, Defender), defendFrom( X, NewAttackers)).
forall( P, Q) :-
  \+ ( P, \+ Q)
  .
% first is the contrary of an assumption in the second
attacks((ConcA,AsmA),(ConcB,AsmB)) :-
	argument((ConcA,AsmA),_),
	contrary(OneAsm,ConcA),
	argument((ConcB,AsmB),_),
	member(OneAsm,AsmB).

