from flask import Flask, request, Response
from src.business import triangulate_points
from src.serializer import parse_point_set_binary, serialize_triangles_binary
import requests

app = Flask(__name__)

POINT_SET_MANAGER_URL = "http://point_set_manager:8000"


@app.route('/triangulate', methods=['POST'])
def triangulate():
    # récupérer l'ID 
    # appeler le PointSetManager
    # parser le binaire
    # calculer
    # renvoyer la réponse
    return Response(b"", status=200)


if __name__ == '__main__':
    app.run(debug=True)
