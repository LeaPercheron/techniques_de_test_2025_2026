"""Tests d'intégration de l'API Triangulator."""

from unittest.mock import MagicMock, patch

import requests

TRIANGULATION_URL = "/triangulation/123e4567-e89b-12d3-a456-426614174000"


#point 2 : verifier que triangulator appelle pointsetmanager avec le bon id
@patch('src.app.requests.get')
def test_appel_manager_avec_bon_id(mock_get, client):
    """Vérifie l'appel au PointSetManager avec le bon ID."""
    reponse_manager_simulee = MagicMock()
    reponse_manager_simulee.status_code = 200
    reponse_manager_simulee.content = (
        b'\x00\x00\x00\x00'  #binaire vide valide (0 points)
    )
    mock_get.return_value = reponse_manager_simulee

    client.get(TRIANGULATION_URL)

    mock_get.assert_called_with(
        "http://point_set_manager:8000/pointset/123e4567-e89b-12d3-a456-426614174000"
    )


#point 3 : vérifier l'envoi de la réponse au client
@patch('src.app.requests.get')
def test_api_retourne_binaire(mock_get, client):
    """Retourne bien du binaire en cas de succès."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'\x00\x00\x00\x00'  #dummy pointset

    reponse_api = client.get(TRIANGULATION_URL)

    assert reponse_api.status_code == 200
    assert reponse_api.data is not None
    assert reponse_api.headers.get('Content-Type').startswith(
        'application/octet-stream'
    )


#ajout: vérifie le content-type de la réponse binaire
@patch('src.app.requests.get')
def test_api_content_type_octet_stream(mock_get, client):
    """Vérifie le Content-Type binaire."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'\x00\x00\x00\x00'

    reponse_api = client.get(TRIANGULATION_URL)

    assert reponse_api.status_code == 200
    assert reponse_api.headers.get('Content-Type').startswith(
        'application/octet-stream'
    )


#point 4 et 8 : pointsetid invalide ou manquant
def test_pointset_id_invalide(client):
    """ID non UUID -> 400."""
    reponse_invalide = client.get('/triangulation/not-a-uuid')
    assert reponse_invalide.status_code == 400
    body = reponse_invalide.get_json()
    assert body["code"] == "INVALID_ID"


#point 5: pointsetmanager retourne 404 (id inconnu)
@patch('src.app.requests.get')
def test_api_manager_retourne_404(mock_get, client):
    """PointSetManager retourne 404 -> 404 propagé."""
    mock_get.return_value.status_code = 404

    reponse_api = client.get(TRIANGULATION_URL)

    assert reponse_api.status_code == 404
    assert reponse_api.get_json()["code"] == "POINTSET_NOT_FOUND"


#point 6 : pointset mal formé reçu du manager
@patch('src.app.requests.get')
@patch('src.app.decoder_pointset_binaire')
def test_api_manager_payload_corrompu(mock_parse, mock_get, client):
    """Payload corrompu -> 500 interne côté triangulator."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'garbage'

    mock_parse.side_effect = ValueError("Corrupted binary")

    reponse_api = client.get(TRIANGULATION_URL)

    assert reponse_api.status_code == 500
    assert reponse_api.get_json()["code"] == "TRIANGULATION_INPUT_ERROR"


#ajout: timeout/erreur réseau côté pointsetmanager -> 503
@patch('src.app.requests.get')
def test_api_timeout_manager_gateway_error(mock_get, client):
    """Timeout vers PointSetManager -> 503."""
    mock_get.side_effect = requests.Timeout()

    reponse_api = client.get(TRIANGULATION_URL)

    assert reponse_api.status_code == 503
    assert reponse_api.get_json()["code"] == "POINTSET_MANAGER_TIMEOUT"


##ajout hors plan : méthodes http non autorisées -> 405 attendu
def test_method_not_allowed(client):
    """Méthode non autorisée -> 405."""
    reponse_api = client.post(TRIANGULATION_URL)  #post au lieu de get
    assert reponse_api.status_code == 405
