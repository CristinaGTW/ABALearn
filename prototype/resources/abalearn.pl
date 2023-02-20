:- use_module(library(dialect/hprolog),
    [ memberchk_eq/2 ]).

:- dynamic my_rule/3, pos/2, neg/2, contrary/2.
restart :- 
   reset_gensym,
   retractall(my_rule(_,_,_)),
   retractall(pos(_,_)),
   retractall(neg(_,_)),
   retractall(contrary(_,_)).


/*
Rules are represented by facts of the form my_rule(RuleId,H,B)
where RuleId is the rule identifier, H is an atom, and B is a list
of atoms.

Positive and negative examples are represented by facts of the form
pos(ExId,A) and neg(ExId,A), respectively, where ExId is the example
identifier and A is an atom.

Contraries are represented by facts of the form contrary(A,C),
where A and C are atoms.

*/

%%%%% ROTE LEARNING %%%%%%

% rote_learn positive example N

rote_learn(N) :- 
   pos(N,A),  
   A=..[Pred|Ts], 
   eq_zip(Xs,Ts,Eqs),
   Head =..[Pred|Xs], 
   gensym(r_,R),
   assert(my_rule(R,Head,Eqs)),
   nl, write('learnt rule:'), show_rule(R), nl. 

% rote_learn all positive examples

rote_learn_all(Pred/Arity) :- 
   pos(N,A), 
   functor(A,Pred,Arity),
   rote_learn(N),
   fail. 
rote_learn_all(_Pred).

% zip two lists into a list of equalities

eq_zip([],[],[]).
eq_zip([X|Xs],[T|Ts],[X=T|Eqs]) :-
   eq_zip(Xs,Ts,Eqs).

%%%%% REMOVE EQUALITIES %%%%%%

removeq(R,EqPos) :-
   my_rule(R,H,B),
   nth1(EqPos,B,Eq,B1),
   Eq=(_=_),
   gensym(r_,R1),
   replace(my_rule(R,H,B),my_rule(R1,H,B1)),
   nl, write('learnt rule:'), show_rule(R1), nl. 

replace(P1,P2) :-
   retract(P1),
   assert(P2).

%%%%% GENERALISE EQUALITIES %%%%%%

geneqs(R) :-
   my_rule(R,H,B),
   subsumes_chk_conj([X=T,Y=U],B,Subconj,Rest),
   Subconj=[X=T,Y=U],
   T==U,
   B1=[X=Y|Rest], 
   gensym(r_,R1),
   replace(my_rule(R,H,B),my_rule(R1,H,B1)),
   nl, write('learnt rule:'), show_rule(R1), nl. 

/* Tests

my_rule(r_20,p(X,Y,Z),[X=a,Y=b,Z=a]).

?- geneqs(r_20).

learnt rule:
r_1: p(A,B,C) <- A=C, B=b
true .


*/

%%%%% FOLDING (simplfied version: no added eqs.) %%%%%%

/*
fold(R1,R2) :-                    
   my_rule(R1,H1,B1),
   my_rule(R2,H2,B2),
   subsumes_chk_conj(B2,B1,Subconj,Rest),
   B2=Subconj,
   append([H2],Rest,NewB),
   gensym(r,R3),
   replace(my_rule(R1,H1,B1),my_rule(R3,H1,NewB)),
   nl, write('learnt rule:'), show_rule(R3), nl. 
*/
   
% Folding with added equalities
% It's a bit more restrictive than the one on paper (see fold(r11,r12))

fold(R1,R2) :-
   R1\=R2,                    
   my_rule(R1,H,Bd1),
   my_rule(R2,K,Bd2),
   term_variables(K,VK),
   hdequalities(VK,Bd2,Eqs2,Eqs1B1),
   select_sublist(Eqs2,SEqs2,REqs2),
   append(SEqs2,Eqs1B1,SBd2),
   subsumes_chk_conj(SBd2,Bd1,Subconj,Rest),
   SBd2=Subconj,
   append(REqs2,[K],NewB),
   append(NewB,Rest,B3),
   gensym(r_,R3),
   replace(my_rule(R1,H,Bd1),my_rule(R3,H,B3)),
   nl, write('learnt rule:'), show_rule(R3), nl. 

hdequalities(VK,Bd2,Eqs2,Eqs1B1) :- hdequalities_acc(VK,Bd2,[],Eqs2,[],Eqs1B1).
   
hdequalities_acc(_VK,[],Eqs,Eqs,R,R).
hdequalities_acc(VK,[A|As],AccEqs,Eqs,AccR,R) :-
   A=(_=_), 
   term_variables(A,VA), 
   term_variables((As,AccEqs,AccR),VAs), 
   del_eq(VK,VAs,Kvars),
   subset_chk(VA,Kvars), !,
   hdequalities_acc(VK,As,[A|AccEqs],Eqs,AccR,R).
hdequalities_acc(VK,[A|As],AccEqs,Eqs,AccR,R) :-
   hdequalities_acc(VK,As,AccEqs,Eqs,[A|AccR],R).

/* Tests

my_rule(r9,p(X,Y),[X=a,Y=b,s(X)]).
my_rule(r10,p(X,Y),[X=a,r(Y),s(X)]).
my_rule(r11,h,[Y=Z,p(Z)]).
my_rule(r12,k,[X=Y,Z=a]).
my_rule(r13,k(Z),[X=Y,Z=a]).
my_rule(r14,k(Z),[X=Z,Z=a]).

?- fold(r10,r9).

learnt rule:
r_3: p(A,B) <- C=b, p(A,C), r(B)
true .

?- fold(r11,r12).
false.

?- fold(r11,r13).

learnt rule:
r_4: h <- A=a, k(A), p(B)
true .

?- fold(r11,r14).
false.

*/

%%%% SUBSUMPTION %%%%%%
% To be automated: Based on unfolding?

rem_rule(R) :-
   retract(my_rule(R,_H,_B)).
add_rule(H,B) :-
   gensym(r_,R),
   assert(my_rule(R,H,B)).



%%%% ASSUMPTION INTRODUCTION via undercutting %%%%%

undercut(R,AtomPos) :-
   my_rule(R,H,B),
   atoms(AtomPos,B,As),
   term_variables(As,Vs),
   gensym(alpha,Alpha),
   gensym(c_alpha,CAlpha),
   Asm=..[Alpha|Vs],
   CAsm=..[CAlpha|Vs],
   assert(contrary(Asm,CAsm)),
   append(B,[Asm],B1),
   gensym(r_,R1),
   replace(my_rule(R,H,B),my_rule(R1,H,B1)),
   nl, write('learnt rule:'), show_rule(R1), nl,
   write('where '), numbervars((Asm,CAsm)), write(contrary(Asm,CAsm)), nl. 


atoms([],_B,[]).
atoms([N|Ns],B,[A|As]) :-
   nth1(N,B,A),
   atoms(Ns,B,As).


% Add/Remove examples
% To be automated

add_pos(A) :- gensym(p_,N), assert(pos(N,A)).
add_neg(A) :- gensym(n_,N), assert(neg(N,A)).
rem_pos(N) :- retract(pos(N,_A)).
rem_neg(N) :- retract(neg(N,_A)).


% show current rules in the database

show_rules(N,H,B) :-
   \+ my_rule(N,H,B), !, 
   write('no rules').
show_rules(N,H,B) :-
   show_rule(N,H,B),
   fail.
?\show_rules(N,H,B).


% show rule with identifier N 

show_rule(N,H,B) :-
   my_rule(N,H,B),
   numbervars((H,B)),
   nl, write(N), write(': '), write(H), write(' <- '), write_conj(B).

get_rules(N,H,B) :-
   my_rule(N,H,B),
   numbervars((H,B)).


% output a conjunction of atoms

write_conj([]) :- write(true).
write_conj([A]) :- write(A).
write_conj([H1,H2|T]) :- write(H1), write(', '), write_conj([H2|T]).


% show examples

show_ex :-
   \+ pos(_,_),
   \+ neg(_,_),
   write('no examples').
show_ex :-
   show_pos,
   fail.
show_ex :-
   nl,
   show_neg,
   fail.
show_ex.

show_pos :-
   pos(N,A),
   numbervars(A),
   nl, write(N), write(': '), write(pos(A)).

show_neg :-
   neg(N,A),
   numbervars(A),
   nl, write(N), write(': '), write(neg(A)).


% MODE: subsumes_chk_conj(+T1,+T2, -T3,-T4)
% TYPE: subsumes_chk_conj(list(term),list(term),list(term),list(term))
% SEMANTICS: T1 and T2 are two list of atoms which encode conjunction of atoms
% T1 subsumes T2, i.e., there exists a sublist T3 consisting of elements
% in T2 which is subsumed by T1, T4 is the list of elements T2\T3.
% It does not unify T1 with T3.

subsumes_chk_conj(A,B,SL,RL) :-
  subsumes_list(A,B,SL,RL),
  subsumes_term(A,SL).

% MODE: subsumes_list(+T1,+T2, -T3,-T4)
% TYPE: subsumes_list(list(term),list(term),list(term),list(term))
% SEMANTICS: T3 is a list consisting of elements in T2 each of which
% is subsumed by an element in T1. T4 is T2\T3.

subsumes_list([],B,[],B).
subsumes_list([G|T],B,SL,RL) :-
  select_subsumed(G,B,S,R),
  subsumes_list(T,R,SL1,RL),
  SL=[S|SL1].

select_subsumed(G,[S|T],S,T) :-
  subsumes_term(G,S).
select_subsumed(G,[H|T],S,[H|T1]) :-
  select_subsumed(G,T,S,T1).

% MODE: subset_chk(?Ts1,?Ts2)
% TYPE: subset_chk(list(term),list(term))
% SEMANTICS: each term in Ts1 occurs in Ts2

subset_chk([],_).
subset_chk([T1|Ts1],Ts2) :-
  memberchk_eq(T1,Ts2),
  subset_chk(Ts1,Ts2).

subset_chk([],_).
subset_chk([T1|Ts1],Ts2) :-
  memberchk_eq(T1,Ts2),
  subset_chk(Ts1,Ts2).

% del_eq(V1,V2,V3): Delete from V1 all terms that are
% identical (==) to an element of V2 and collect the result in V3

del_eq(V1,[],V1).  
del_eq(V1,[W|V2],V3) :-
   del_1(V1,W,V4),
   del_eq(V4,V2,V3).
    
del_1([],_W,[]).  
del_1([V|V1],W,V3) :-
   V==W, !,
   del_1(V1,W,V3).
del_1([V|V1],W,[V|V3]) :-
   del_1(V1,W,V3).

% select_sublist(Xs,Ys,Zs): Ys is a list obtained
% by selecting some elements from Xs (preserving the order)
% and Zs is the list of the remaining elements 

select_sublist([],[],[]).
select_sublist([X|Xs],[X|Ys],Zs) :- 
   select_sublist(Xs,Ys,Zs).
select_sublist([X|Xs],Ys,[X|Zs]) :- 
   select_sublist(Xs,Ys,Zs).


man :-
   nl, write('Available transformation rules:'), nl,
   write('- rote_learn(RuleId): learn positive example RuleId;'), nl,
   write('- rote_learn_all(P/A): learn all positive examples for predicate P of arity A;'), nl, 
   write('- removeq(RuleId,P): remove from rule RuleId the equality at position P;'), nl,
   write('- geneqs(RuleId): in rule RuleId generalise equalities (X=t, Y=t) to X=Y;'), nl,
   write('- fold(RuleId1,RuleId2): fold rule RuleId1 using rule RuleId2;'), nl,
   write('- rem_rule(RuleId): remove rule RuleId;'), nl,
   write('- add_rule(H,B): add rule H <- B, where A is an atom and B is a list of atoms;'), nl,
   write('- undercut(RuleId,AtomPos): introduce an assumption atom in the body of rule RuleId whose variables are those of the atoms at position AtomPos, and introduce a corresponding contrary to the assumption;'), nl,
   write('- add_pos(A): add positive example A;'), nl,
   write('- add_neg(A): add negative example A;'), nl,
   write('- rem_pos(ExId): remove positive example ExId;'), nl,
   write('- rem_neg(ExId): remove negative example ExId;'), nl,
   write('- show_rules: print current set of rules;'), nl,
   write('- show_rule(RuleId): print rule RuleId;'), nl,
   write('- show_ex: print current set of examples;'), nl,
   write('- restart: restart system.').

:- man.
