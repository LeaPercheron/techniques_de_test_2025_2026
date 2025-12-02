import pytest
import requests
from unittest.mock import patch, MagicMock


# point 2 : verifier que Triangulator appelle PointSetManager avec le bon ID
@patch('src.app.requests.get')
def test_appel_manager_avec_bon_id(mock_get, client):
    #setup du mock pour simuler une réponse valide du Manager
    reponse_manager_simulee = MagicMock()
    reponse_manager_simulee.status_code = 200
    reponse_manager_simulee.content = b'\x00\x00\x00\x00'  # binaire vide valide (0 points)
    mock_get.return_value = reponse_manager_simulee

    #appel au Triangulator
    client.post('/triangulate?id=12345')

    # vérification (assert)
    mock_get.assert_called_with("http://point_set_manager:8000/point_sets/12345")


#Point 3 : vérifier l'envoi de la réponse au client
@patch('src.app.requests.get')
def test_api_retourne_binaire(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'\x00\x00\x00\x00'  # dummy pointset

    reponse_api = client.post('/triangulate?id=12345')

    assert reponse_api.status_code == 200
    assert reponse_api.data is not None
    # assert response.headers['Content-Type'] == 'application/octet-stream'


#ajout: vérifie le Content-Type de la réponse binaire
@patch('src.app.requests.get')
def test_api_content_type_octet_stream(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'\x00\x00\x00\x00'

    reponse_api = client.post('/triangulate?id=42')

    assert reponse_api.status_code == 200
    assert reponse_api.headers.get('Content-Type') in ('application/octet-stream', 'application/octet-stream; charset=utf-8')


# point 4 et 8 : pointSetID invalide ou manquant
def test_missing_pointset_id(client):
    reponse_sans_id = client.post('/triangulate')  # pas d'ID
    assert reponse_sans_id.status_code == 400


# point 5: PointSetManager retourne 404 (ID inconnu)
@patch('src.app.requests.get')
def test_api_manager_retourne_404(mock_get, client):
    mock_get.return_value.status_code = 404

    reponse_api = client.post('/triangulate?id=unknown_id')

    assert reponse_api.status_code == 404


#point 6 : pointSet mal formé reçu du Manager
@patch('src.app.requests.get')
@patch('src.app.parse_point_set_binary')
def test_api_manager_payload_corrompu(mock_parse, mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'garbage'

    # on simule que le parseur lève une erreur car les données sont pourries
    mock_parse.side_effect = ValueError("Corrupted binary")

    reponse_api = client.post('/triangulate?id=123')

    # le Triangulator doit gérer l'erreur proprement (ex: 502 Bad Gateway)
    assert reponse_api.status_code in [500, 502]


#ajout: timeout/erreur réseau côté PointSetManager -> 502/503
@patch('src.app.requests.get')
def test_api_timeout_manager_gateway_error(mock_get, client):
    mock_get.side_effect = requests.Timeout()

    reponse_api = client.post('/triangulate?id=777')

    assert reponse_api.status_code in [502, 503]


##ajout hors plan : méthodes http non autorisées -> 405 attendu
def test_method_not_allowed(client):
    reponse_api = client.get('/triangulate')  # get au lieu de post
    assert reponse_api.status_code == 405
