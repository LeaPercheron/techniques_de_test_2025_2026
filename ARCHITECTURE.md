# Documentation technique complète (Triangulator)

## Vue d'ensemble

- Microservice Flask stateless : calcule une triangulation à partir d'un PointSet identifié par un UUID et renvoie le résultat en binaire.
- Dépendance externe : PointSetManager (HTTP) qui fournit le PointSet binaire.

1. Client envoie un PointSet binaire au PointSetManager et reçoit un `PointSetID` (UUID).
2. Client appelle le Triangulator `GET /triangulation/<PointSetID>`.
3. Triangulator appelle le PointSetManager `GET /pointset/<PointSetID>` pour récupérer le PointSet binaire.
4. Triangulator décode le PointSet, calcule la triangulation (Bowyer-Watson / Delaunay), encode le résultat Triangles et renvoie un `application/octet-stream`.
5. En cas d'erreur, renvoie du JSON structuré `{code, message}`.

## Modules et fonctions

### `src/app.py` (API Flask)
- Module : description du service et du workflow complet.
- `app` : instance Flask.
- `URL_GESTIONNAIRE_POINTSET` : URL du PointSetManager.
- `_reponse_erreur(statuts, code, message)` : construit une réponse JSON d'erreur uniforme.
- `trianguler(identifiant_pointset)` : endpoint GET. Étapes : validation UUID -> appel HTTP au PointSetManager -> décodage binaire -> triangulation métier -> encodage Triangles -> réponse binaire. Gère les erreurs réseau, codes 404/503, payload corrompu, erreurs internes.

### `src/business.py` (métier triangulation)
- Module : décrit le choix Bowyer-Watson (Delaunay) et les étapes.
- `trianguler_points(liste_points)` : valide l'entrée, traite cas dégénérés (<3 points ou colinéaires) puis exécute Bowyer-Watson avec super-triangle, cavité et reconstruction.
  - Fonctions internes :
    - `produit_vectoriel(point_origine, point_a, point_b)` : aire orientée pour tester colinéarité/sens.
    - `cercle_circonscrit_contient(triangle, point_test)` : test d'inclusion dans le cercle circonscrit (déterminant).
    - `cle_arete(arete)` : clé normalisée pour identifier les arêtes frontières (suppression des doublons internes).

### `src/serializer.py` (sérialisation binaire)
- Module : détaille les formats binaires big-endian.
- `decoder_pointset_binaire(donnees: bytes)` : lit l'en-tête, valide la taille annoncée, refuse NaN/inf, retourne `[(x, y), ...]`.
- `encoder_triangles_binaire(points, triangles)` : valide points (type, valeurs finies) et triangles (3 indices, entiers, bornés, distincts), encode PointSet + nombre de triangles + indices.

### Tests (organisation)
- `tests/unit/test_business.py` : cas simples, colinéarité, 0/1/2 points, doublons, coordonnées infinies.
- `tests/unit/test_serializer.py` : encodage binaire, payload tronqué/taille incohérente, NaN rejeté, indices hors bornes/non entiers, triangles dégénérés.
- `tests/integration/test_api.py` : client Flask + mocks `requests.get`; vérifie l’URL appelée, content-type binaire, propagation des 404/400/503/500, payload corrompu, timeout réseau, 405 sur méthode non autorisée.
- `tests/performance/test_perf.py` : temps d'exécution sur 10k et 1k points colinéaires (marqueur `performance`).
- `tests/conftest.py` : fixture `client` (client Flask de test).

## Formats binaires (big-endian)

- PointSet : `uint32` (nb points) + pour chaque point `float32 X`, `float32 Y`.
- Triangles : PointSet complet + `uint32` (nb triangles) + pour chaque triangle trois `uint32` indices vers le PointSet.

## Algorithme Bowyer-Watson (Delaunay)

1. Validation entrée : liste/tuple, deux coordonnées finies, pas de doublons.
2. Cas non triangulables : <3 points ou colinéarité globale → `[]`.
3. Construction d'un super-triangle englobant tous les points.
4. Insertion incrémentale de chaque point :
   - Identifier les triangles dont le cercle circonscrit contient le point (cavité).
   - Supprimer ces triangles et collecter leurs arêtes.
   - Garder uniquement les arêtes frontières (non dupliquées).
   - Créer de nouveaux triangles en reliant le point aux arêtes frontières.
5. Filtrer les triangles qui utilisent un sommet du super-triangle.
6. Retourner les triangles par indices relatifs à la liste d'origine.

## Codes d'erreur API (réponses JSON)

- `INVALID_ID` : UUID manquant ou invalide.
- `POINTSET_NOT_FOUND` : le PointSetManager renvoie 404.
- `POINTSET_MANAGER_TIMEOUT` / `POINTSET_MANAGER_UNAVAILABLE` : indisponibilité réseau.
- `POINTSET_MANAGER_ERROR` : code inattendu du PointSetManager.
- `TRIANGULATION_INPUT_ERROR` : payload binaire corrompu/non conforme.
- `TRIANGULATION_FAILED` : erreur interne lors du calcul.

## Mocks (tests d'intégration)

- `unittest.mock.patch('src.app.requests.get')` remplace l'appel HTTP réel.
- Configuration possible : `status_code`, `content`, ou `side_effect` (ex. `requests.Timeout`).
- Validation : `assert_called_with` pour l'URL, vérification des réponses HTTP produites par l'API.

## Commandes Makefile

- `make test` : tous les tests.
- `make unit_test` : sans les tests de perf (`-m "not performance"`).
- `make perf_test` : seulement les tests de perf (`-m performance`).
- `make coverage` : exécution + rapport coverage.
- `make lint` : ruff.
- `make doc` : génération de la doc HTML (pdoc) dans `docs/src/`.