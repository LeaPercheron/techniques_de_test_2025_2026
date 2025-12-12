"""Serveur Flask du Triangulator (API HTTP)."""

import json
import uuid

import requests
from flask import Flask, Response

from src.business import trianguler_points
from src.serializer import decoder_pointset_binaire, encoder_triangles_binaire

app = Flask(__name__)

URL_GESTIONNAIRE_POINTSET = "http://point_set_manager:8000"


def _reponse_erreur(statuts, code, message):
    corps = {"code": code, "message": message}
    return Response(
        response=json.dumps(corps),
        status=statuts,
        content_type="application/json",
    )


@app.route('/triangulation/<identifiant_pointset>', methods=['GET'])
def trianguler(identifiant_pointset):
    """Compute triangulation for a PointSet identified by a UUID."""
    if not identifiant_pointset:
        return _reponse_erreur(400, "INVALID_ID", "PointSetID manquant")

    try:
        uuid.UUID(identifiant_pointset)
    except (ValueError, AttributeError):
        return _reponse_erreur(
            400, "INVALID_ID", "PointSetID invalide (UUID attendu)"
        )

    #recupere le pointset auprès du pointsetmanager
    try:
        reponse_gestionnaire = requests.get(
            f"{URL_GESTIONNAIRE_POINTSET}/pointset/{identifiant_pointset}"
        )
    except requests.Timeout:
        return _reponse_erreur(
            503,
            "POINTSET_MANAGER_TIMEOUT",
            "PointSetManager indisponible (timeout)",
        )
    except requests.RequestException:
        return _reponse_erreur(
            503,
            "POINTSET_MANAGER_UNAVAILABLE",
            "Erreur lors de l'appel au PointSetManager",
        )

    if reponse_gestionnaire.status_code == 404:
        return _reponse_erreur(404, "POINTSET_NOT_FOUND", "PointSet introuvable")

    if reponse_gestionnaire.status_code != 200:
        return _reponse_erreur(
            503,
            "POINTSET_MANAGER_ERROR",
            "Erreur du PointSetManager",
        )

    try:
        #parse -> triangule -> sérialise
        points = decoder_pointset_binaire(reponse_gestionnaire.content)
        triangles = trianguler_points(points)
        charge_utile = encoder_triangles_binaire(points, triangles)
    except ValueError:
        return _reponse_erreur(
            500,
            "TRIANGULATION_INPUT_ERROR",
            "Données invalides reçues du PointSetManager",
        )
    except Exception:
        return _reponse_erreur(
            500,
            "TRIANGULATION_FAILED",
            "Erreur interne lors du calcul",
        )

    return Response(charge_utile, status=200, content_type='application/octet-stream')


if __name__ == '__main__':
    app.run(debug=True)
