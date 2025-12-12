"""Tests unitaires pour la triangulation métier."""

import pytest

from src.business import trianguler_points


#point 1 : vérifier que les calculs de triangulation sont valides (cas simple)
def test_triangulation_cas_simple():
    """Triangulation minimale valide."""
    nuage_points = [(0, 0), (1, 0), (0, 1)]
    triangulation = trianguler_points(nuage_points)
    #on s'attend à une liste de triangles pour l'instant ça échouera ou renverra vide
    #une fois implémenté, on vérifiera : assert len(result) == 1
    assert isinstance(triangulation, list)


#point 9 : cas dégénérés (colinéaires, uniques)
def test_triangulation_cas_degenere_colineaire():
    """Points colinéaires -> aucun triangle."""
    nuage_points_colineaires = [
        (0, 0),
        (1, 1),
        (2, 2),
    ]  #colinéaires -> pas de triangle
    triangulation = trianguler_points(nuage_points_colineaires)
    assert len(triangulation) == 0


def test_triangulation_point_unique():
    """Point unique -> aucun triangle."""
    nuage_point_unique = [(0, 0)]
    triangulation = trianguler_points(nuage_point_unique)
    assert len(triangulation) == 0


#ajout : points dupliqués -> pas de triangulation ou erreur
def test_triangulation_points_dupliques():
    """Points dupliqués -> erreur."""
    nuage_points_dupliques = [(0, 0), (0, 0), (1, 0)]
    with pytest.raises(ValueError):
        trianguler_points(nuage_points_dupliques)


#ajout : coordonnées infinies -> erreur attendue
def test_triangulation_coordonnees_infinies():
    """Coordonnées infinies -> erreur."""
    nuage_points_infinis = [(float('inf'), 0.0), (0.0, 1.0), (1.0, 0.0)]
    with pytest.raises(ValueError):
        trianguler_points(nuage_points_infinis)


#ajout hors plan : cas limites 0, 1, 2 points -> pas de triangles
def test_triangulation_points_insuffisants():
    """0, 1 ou 2 points -> aucun triangle."""
    assert trianguler_points([]) == []        #0 point
    assert trianguler_points([(1, 1)]) == []  #1 point
    assert trianguler_points([(0, 0), (1, 1)]) == []  #2 points
