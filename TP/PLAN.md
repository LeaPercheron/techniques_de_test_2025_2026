# TODO

Test explications :

1) test qui verifie que les calculs de triangulation sont valides
    Pourquoi :
        1.1) valide que la triangulation renvoyee est correcte et correctement formatee sur des cas simples
    Comment :
        1.2) realise via tests unitaires pytest sur le module de triangulation avec jeux de donnees synthetiques

2) test permettant de verifier que le triangulator recupere bien les ensembles de points du PointSetManager et passe PointSetID au PointSetManager
    Pourquoi :
        2.1) garantir que Triangulator consomme l'API du PointSetManager avec les bons parametres et utilise le bon jeu de points
    comment :
        2.2) Execute en test d'integration avec un PointSetManager moque
        2.3) verifie les appels HTTP sortants et la propagation du PointSetID dans les logs

3) test permetant de verifier l'envoie au client de straingles issus de la triangulation
    Pourquoi:
        3.1) confirmer que l'API renvoie les triangles calcules avec des entetes et un corps binaire exploitables par le client
    Comment :
        3.2) realise via tests API pour controler le corps binaire qui est retourner
        3.3) inclut des assertions sur les entetes HTTP et la deserialisation cote client de test

4)test qui permet de verifier que PointSetID envoyer par client est bien valide, ce qui correspodns au format
    pourquoi
        4.1) bloquer les identifiants non conformes et informer clairement le client en cas d'erreur de saisie.
    Comment :
        4.2) couvert par des tests API parametres de pytest injectant diverses valeurs invalides
        4.3) controle la validation cote entree sans invoquer le PointSetManager

5) test permettant de verifier que Triangulator remonte une erreur coherente quand PointSetManager retourne un PointSetID inconnu
    Pourquoi :
        5.1) s'assurer qu'un PointSetID inconnu est signale par un 404 sans lancer de calcul superflu
    Comment :
        5.2) simule via tests d'integration ou le PointSetManager moque renvoie 404

6) test permettant de verifier la gestion d'erreurs lorsque le PointSet recu est mal forme (binaire incomplet ou taille incoherente)
    Pourquoi :
        6.1) rjeter proprement les PointSet corrompus avec le statut 502 tout en journalisant l'incident
    comment :
        6.2) realise avec des fixtures binaires tronquees dans des tests API


7) test qui verifie la coherence de l'encodage binaire des triangles retournes
    pourquoi :
    7.1) assurer que le binaire restitue fidèlement le nombre de points, de triangles et leurs indices
    Comment :
        7.2) compare a un decodeur de reference dans les tests unitaires

8) test qui valide la gestion d'un PointSetID manquant ou mal forme
    Pourquoi :
        8.1) assurer la robustesse de la validation des requetes client avec une absence ou format invalide de PointSetID
    Comment :
        8.2) tests API parametres verifiant le schema des requetes entrantes

9) test de coherence sur l'algorithme de triangulation pour des cas degeneres
    Pourquoi :
        9.1) controler que l'algorithme gere triangles uniques, points colineaires
    Comment :
        9.2) rxecute en tests unitaires avec jeux de donnees dedies

10) test qui atteste de la conformite du format binaire en sortie avec un client de reference
    Pourquoi :
        10.1) garantir l'interoperabilite du flux binaire avec un client de reference et differents endianness
    Comment :
        10.2) realise via tests de compatibilite utilisant un client Python de reference

11) test pour revenir sur un PointSet contenant des valeurs invalides comme nul, (Nan)
    Pourquoi :
        11.1) s'assurer qu'un PointSet avec valeurs aberrantes est refuse proprement en 422 avec un retour explicite
    Comment :
    11.2) mis en oeuvre via tests unitaires sur la couche de parsing binaire

12) test de montee en charge sur plusieurs requetes simultanees
    Pourquoi :
        12.1) verifier la latence, absence d'etat corrompu si une requete en  parallèle 
    Comment :
        12.2 scenarii executes via pytest-xdist avec instrumentation des metriques
        