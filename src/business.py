"""Logique métier de triangulation."""


def trianguler_points(liste_points):
    """Compute Delaunay triangulation for a 2D point set (Bowyer-Watson)."""
    import math

    if liste_points is None:
        raise ValueError("liste de points manquante")

    if not isinstance(liste_points, (list, tuple)):
        raise TypeError("liste_points doit être une liste ou un tuple")

    points = list(liste_points)

    if len(points) < 3:
        return []

    for point in points:
        if (
            not isinstance(point, (list, tuple))
            or len(point) != 2
            or not all(isinstance(coord, (int, float)) for coord in point)
        ):
            raise ValueError("point invalide dans la liste")
        if not (math.isfinite(point[0]) and math.isfinite(point[1])):
            raise ValueError("coordonnées non finies détectées")

    if len(points) != len(set(tuple(p) for p in points)):
        raise ValueError("points dupliqués détectés")

    def produit_vectoriel(point_origine, point_a, point_b):
        """Aire orientée (determinant 2D) pour tester colinearité/sens de rotation."""
        return (point_a[0] - point_origine[0]) * (point_b[1] - point_origine[1]) - (
            point_a[1] - point_origine[1]
        ) * (point_b[0] - point_origine[0])

    #detecte colinéarité globale (aucune aire)
    point0 = points[0]
    point1 = points[1]
    tous_colineaires = True
    for point in points[2:]:
        if abs(produit_vectoriel(point0, point1, point)) > 1e-12:
            tous_colineaires = False
            break
    if tous_colineaires:
        return []

    #construction d'un super-triangle très large qui contient tous les points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    dx = max_x - min_x
    dy = max_y - min_y
    delta = max(dx, dy) or 1.0
    mid_x = (min_x + max_x) / 2.0
    mid_y = (min_y + max_y) / 2.0

    super_point1 = (mid_x - 20 * delta, mid_y - delta)
    super_point2 = (mid_x, mid_y + 20 * delta)
    super_point3 = (mid_x + 20 * delta, mid_y - delta)

    points_ext = points + [super_point1, super_point2, super_point3]
    indices_super = (len(points), len(points) + 1, len(points) + 2)

    #triangles courants : liste de tuples (i, j, k) indices dans points_ext
    triangles_actuels = [indices_super]

    def cercle_circonscrit_contient(triangle, point_test):
        """Teste si point_test est à l'intérieur du cercle circonscrit du triangle."""
        ax, ay = points_ext[triangle[0]]
        bx, by = points_ext[triangle[1]]
        cx, cy = points_ext[triangle[2]]
        dx, dy = point_test

        #matrice de déterminant pour tester inclusion dans le cercle circonscrit
        #| ax-dx ay-dy (ax-dx)^2+(ay-dy)^2 |
        #| bx-dx by-dy (bx-dx)^2+(by-dy)^2 |
        #| cx-dx cy-dy (cx-dx)^2+(cy-dy)^2 |
        a_dx = ax - dx
        a_dy = ay - dy
        b_dx = bx - dx
        b_dy = by - dy
        c_dx = cx - dx
        c_dy = cy - dy

        det = (
            (a_dx * a_dx + a_dy * a_dy) * (b_dx * c_dy - b_dy * c_dx)
            - (b_dx * b_dx + b_dy * b_dy) * (a_dx * c_dy - a_dy * c_dx)
            + (c_dx * c_dx + c_dy * c_dy) * (a_dx * b_dy - a_dy * b_dx)
        )
        return det > 1e-12

    for indice_point, point in enumerate(points):
        triangles_incorrects = []
        for triangle in triangles_actuels:
            if cercle_circonscrit_contient(triangle, point):
                triangles_incorrects.append(triangle)

        #aretes de la cavité (chaque arête est un tuple trié)
        aretes = []
        for triangle in triangles_incorrects:
            aretes.extend(
                [
                    (triangle[0], triangle[1]),
                    (triangle[1], triangle[2]),
                    (triangle[2], triangle[0]),
                ]
            )

        def cle_arete(arete):
            """Clé normalisée (ordre trié) pour compter les arêtes frontières."""
            return tuple(sorted(arete))

        #supprime les triangles mauvais
        triangles_actuels = [
            triangle
            for triangle in triangles_actuels
            if triangle not in triangles_incorrects
        ]

        #aretes dupliquées = internes, on les retire
        aretes_frontiere = []
        compte_aretes = {}
        for arete in aretes:
            cle = cle_arete(arete)
            compte_aretes[cle] = compte_aretes.get(cle, 0) + 1
        for arete in aretes:
            cle = cle_arete(arete)
            if compte_aretes[cle] == 1:
                aretes_frontiere.append(arete)

        #reconstruit en reliant le point à chaque arête frontière
        for arete in aretes_frontiere:
            triangles_actuels.append((arete[0], arete[1], indice_point))

    #filtrer les triangles qui utilisent le super-triangle
    triangles_finaux = []
    for triangle in triangles_actuels:
        if any(sommet in indices_super for sommet in triangle):
            continue
        triangles_finaux.append(triangle)

    #renvoie les indices par rapport à la liste d'origine (points)
    return triangles_finaux
