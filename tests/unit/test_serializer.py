import struct
import pytest
from src.serializer import parse_point_set_binary, serialize_triangles_binary


#point 7 : cohérence encodage binaire sortie
def test_serialize_triangles_format_binaire():
    nuage_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles_indices = [(0, 1, 2)]

    binaire_triangles = serialize_triangles_binary(nuage_points, triangles_indices)

    #on vérifiera que le binaire commence par la taille, etc.
    #Pour l'instant, comme la fonction est vide, ce test échouera ou sera incomplet.
    assert isinstance(binaire_triangles, bytes)


#point 11 : gestion des valeurs invalides (NaN)
def test_parse_pointset_avec_nan():
    #création d'un binaire corrompu avec un NaN pour X
    nan_float = float('nan')
    #1 point, X=NaN, Y=0.0
    payload_corrompu = struct.pack('>Lff', 1, nan_float, 0.0)

    with pytest.raises(ValueError):
        parse_point_set_binary(payload_corrompu)


# point 10 :conformité client référence (simulé ici par struct)
def test_format_binaire_compatible_reference():
    #simulation d'un "client de référence" qui lit le binaire
    flux_binaire = serialize_triangles_binary([(0, 0)], [])
    #Si le output est vide (stub), le test échoue, c'est normal pour l'instant
    assert flux_binaire is not None


#Ajout : robustesse binaire - payload tronqué ou taille incohérente
def test_parse_pointset_payload_tronque():
    #il annonce 2 points mais ne fournit qu'un seul couple (x, y)
    payload_incomplet = struct.pack('>Lff', 2, 0.0, 1.0)
    with pytest.raises((ValueError, RuntimeError)):
        parse_point_set_binary(payload_incomplet)


# ajout : indices de triangles hors bornes/doublons -> erreur d'encodage
def test_serialize_triangles_indices_invalides():
    nuage_points = [(0.0, 0.0), (1.0, 0.0)]
    triangles_indices_invalides = [(0, 1, 2)]
    with pytest.raises((ValueError, RuntimeError)):
        serialize_triangles_binary(nuage_points, triangles_indices_invalides)
