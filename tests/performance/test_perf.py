import pytest
import time
from src.business import triangulate_points


@pytest.mark.performance
def test_performance_charge_massive_10k():
    # génération d'un gros set de points mock data
    nuage_points_massif = [(float(i), float(i)) for i in range(10000)]

    start_time = time.time()
    triangulate_points(nuage_points_massif)
    end_time = time.time()

    duration = end_time - start_time
    # le test échouera peut-être si c'est trop len ou il passera instantanément
    assert duration < 2.0  # doit prendre moins de 2 secondes


# ajout : baseline plus petite pour limiter la flakiness
@pytest.mark.performance
def test_performance_baseline_1k():
    nuage_points_1k = [(float(i), float(i)) for i in range(1000)]

    start_time = time.time()
    triangulate_points(nuage_points_1k)
    duration = time.time() - start_time

    assert duration < 0.5
