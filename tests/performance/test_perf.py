"""Tests de performance sur la triangulation."""

import time

import pytest

from src.business import trianguler_points


@pytest.mark.performance
def test_performance_charge_massive_10k():
    """Doit s'exécuter en moins de 2s sur 10k points colinéaires."""
    #génération d'un gros set de points mock data
    nuage_points_massif = [(float(i), float(i)) for i in range(10000)]

    start_time = time.time()
    trianguler_points(nuage_points_massif)
    end_time = time.time()

    duration = end_time - start_time
    #le test échouera peut-être si c'est trop len ou il passera instantanément
    assert duration < 2.0  #doit prendre moins de 2 secondes


#ajout : baseline plus petite pour limiter la flakiness
@pytest.mark.performance
def test_performance_baseline_1k():
    """Doit s'exécuter en moins de 0.5s sur 1k points colinéaires."""
    nuage_points_1k = [(float(i), float(i)) for i in range(1000)]

    start_time = time.time()
    trianguler_points(nuage_points_1k)
    duration = time.time() - start_time

    assert duration < 0.5
