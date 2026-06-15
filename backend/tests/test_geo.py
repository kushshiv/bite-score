from app.services.geo import haversine_km


def test_haversine_same_point_is_zero():
    assert haversine_km(52.52, 13.405, 52.52, 13.405) == 0.0


def test_haversine_known_distance_berlin():
    distance = haversine_km(52.52, 13.405, 53.52, 13.405)
    assert 110 < distance < 112


def test_haversine_is_symmetric():
    a = haversine_km(52.52, 13.405, 48.1351, 11.582)
    b = haversine_km(48.1351, 11.582, 52.52, 13.405)
    assert a == b


def test_haversine_short_city_distance():
    distance = haversine_km(52.52, 13.405, 52.521, 13.406)
    assert 0 < distance < 1
