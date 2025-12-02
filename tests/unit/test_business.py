import pytest
from src.business import triangulate_points


#point 1 : vérifier que les calculs de triangulation sont valides (cas simple)
def test_triangulation_cas_simple():
    nuage_points = [(0, 0), (1, 0), (0, 1)]
    triangulation = triangulate_points(nuage_points)
    # On s'attend à une liste de triangles pour l'instant ça échouera ou renverra vide
    # une fois implémenté, on vérifiera : assert len(result) == 1
    assert isinstance(triangulation, list)


# point 9 : cas dégénérés (colinéaires, uniques)
def test_triangulation_cas_degenere_colineaire():
    nuage_points_colineaires = [(0, 0), (1, 1), (2, 2)]  # colinéaires -> pas de triangle
    triangulation = triangulate_points(nuage_points_colineaires)
    assert len(triangulation) == 0


def test_triangulation_point_unique():
    nuage_point_unique = [(0, 0)]
    triangulation = triangulate_points(nuage_point_unique)
    assert len(triangulation) == 0


#ajout : points dupliqués -> pas de triangulation ou erreur
def test_triangulation_points_dupliques():
    nuage_points_dupliques = [(0, 0), (0, 0), (1, 0)]
    with pytest.raises(Exception):
        triangulate_points(nuage_points_dupliques)


#ajout : coordonnées infinies -> erreur attendue
def test_triangulation_coordonnees_infinies():
    nuage_points_infinis = [(float('inf'), 0.0), (0.0, 1.0), (1.0, 0.0)]
    with pytest.raises(Exception):
        triangulate_points(nuage_points_infinis)


# Ajout hors plan : cas limites 0, 1, 2 points -> pas de triangles
def test_triangulation_points_insuffisants():
    assert triangulate_points([]) == []        # 0 point
    assert triangulate_points([(1, 1)]) == []  # 1 point
    assert triangulate_points([(0, 0), (1, 1)]) == []  # 2 points
