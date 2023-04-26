% Mark Law 26/05/2022

    #pos({pacifist(p1)}, {n_pacifist(p1)}, {
    quaker(p1).
    }).

    #pos({n_pacifist(p2)}, {pacifist(p2)}, {
    republican(p2).
    }).


    #pos({n_pacifist(p3)}, {pacifist(p3)}, {
    quaker(p3).
    republican(p3).
    }).

    #pos({pacifist(p3)}, {n_pacifist(p3)}, {
    quaker(p3).
    republican(p3).
    }).

    #neg({pacifist(p1)}, {n_pacifist(p1)}, {
    republican(p1).
    }).

    #neg({n_pacifist(p2)}, {pacifist(p2)}, {
    quaker(p2).
    }).

    :- n_pacifist(X), pacifist(X).

    #modeh(pacifist(var(person))).
    #modeh(n_pacifist(var(person))).
    #modeb(pacifist(var(person))).
    #modeb(n_pacifist(var(person))).
    #modeb(republican(var(person))).
    #modeb(quaker(var(person))).
 
% $ ILASP --version=2 pacifist.las 
% n_pacifist(V1) :- not pacifist(V1); republican(V1).
% pacifist(V1) :- not n_pacifist(V1); quaker(V1). 
     
% Note that I’m using n_pacifist here to represent -pacifist. 
% ILASP does support strong negation, but I’ve just noticed 
% that the most recent version of the parser does not allow 
% strong negation in mode declarations. I’ll try to remember 
% to fix this in the next release.
