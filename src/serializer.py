"""Sérialisation/désérialisation binaire des structures PointSet et Triangles."""


def decoder_pointset_binaire(donnees: bytes):
    """Decode le format binaire PointSet."""
    import math
    import struct

    if len(donnees) < 4:
        raise ValueError("payload trop court pour contenir un PointSet")

    try:
        (nombre_points,) = struct.unpack(">L", donnees[:4])
    except struct.error as exc:  #pragma: no cover
        raise ValueError("en-tête PointSet invalide") from exc

    longueur_attendue = 4 + nombre_points * 8
    if len(donnees) != longueur_attendue:
        raise ValueError(
            "taille du payload incohérente avec le nombre de points annoncé"
        )

    points = []
    decalage = 4
    for _ in range(nombre_points):
        coord_x, coord_y = struct.unpack_from(">ff", donnees, decalage)
        decalage += 8
        if not (math.isfinite(coord_x) and math.isfinite(coord_y)):
            raise ValueError("coordonnées non finies détectées dans le PointSet")
        points.append((coord_x, coord_y))

    return points


def encoder_triangles_binaire(points, triangles):
    """Encode le résultat au format binaire Triangles."""
    import math
    import struct

    if points is None:
        raise ValueError("liste de points manquante")

    if triangles is None:
        raise ValueError("liste de triangles manquante")

    nombre_points = len(points)
    charge_utile = bytearray()
    charge_utile.extend(struct.pack(">L", nombre_points))

    for point in points:
        if (
            not isinstance(point, (list, tuple))
            or len(point) != 2
            or not all(isinstance(coord, (int, float)) for coord in point)
        ):
            raise ValueError("point invalide dans la liste")
        if not (math.isfinite(point[0]) and math.isfinite(point[1])):
            raise ValueError("coordonnées non finies détectées dans la liste de points")
        charge_utile.extend(struct.pack(">ff", float(point[0]), float(point[1])))

    nombre_triangles = len(triangles)
    charge_utile.extend(struct.pack(">L", nombre_triangles))

    for triangle in triangles:
        if not isinstance(triangle, (list, tuple)) or len(triangle) != 3:
            raise ValueError("triangle invalide, il faut 3 indices")

        if any(not isinstance(idx, int) for idx in triangle):
            raise ValueError("indices de triangle non entiers")

        if any(idx < 0 or idx >= nombre_points for idx in triangle):
            raise ValueError("indice de triangle hors bornes")

        if len({triangle[0], triangle[1], triangle[2]}) != 3:
            raise ValueError("triangle dégénéré avec des sommets dupliqués")

        charge_utile.extend(struct.pack(">LLL", *triangle))

    return bytes(charge_utile)
