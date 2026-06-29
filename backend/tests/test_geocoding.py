from unittest.mock import patch

import pytest

from app.services.geocoding import (
    CITY_CENTERS,
    ResolvedCoordinates,
    build_geocode_query,
    city_center_coords,
    parse_nominatim_results,
    resolve_coordinates,
)
from tests.conftest import auth_header


class TestBuildGeocodeQuery:
    def test_includes_name_address_city_country(self):
        query = build_geocode_query("Joe's Taco Stand", "Main St 1", "Berlin", "Germany")
        assert query == "Joe's Taco Stand, Main St 1, Berlin, Germany"

    def test_omits_empty_address(self):
        query = build_geocode_query("Spice Kitchen", None, "Mumbai", "India")
        assert query == "Spice Kitchen, Mumbai, India"


class TestParseNominatimResults:
    def test_parses_first_result(self):
        results = [{"lat": "52.531", "lon": "13.412", "display_name": "Berlin"}]
        assert parse_nominatim_results(results) == (52.531, 13.412)

    def test_returns_none_for_empty(self):
        assert parse_nominatim_results([]) is None


class TestCityCenterCoords:
    def test_known_city(self):
        assert city_center_coords("Berlin", "Germany") == CITY_CENTERS[("Berlin", "Germany")]

    def test_unknown_city(self):
        assert city_center_coords("Unknown", "Nowhere") is None


class TestResolveCoordinates:
    def test_uses_nominatim_when_available(self):
        def fake_geocoder(query: str) -> list[dict]:
            assert "Joe's Taco Stand" in query
            return [{"lat": "52.501", "lon": "13.401"}]

        resolved = resolve_coordinates(
            name="Joe's Taco Stand",
            address="Alexanderplatz",
            city="Berlin",
            country="Germany",
            geocoder=fake_geocoder,
        )
        assert resolved.latitude == 52.501
        assert resolved.longitude == 13.401
        assert resolved.source == "nominatim"

    def test_falls_back_to_gps_when_geocode_misses(self):
        resolved = resolve_coordinates(
            name="Street Cart",
            address=None,
            city="Berlin",
            country="Germany",
            client_latitude=52.55,
            client_longitude=13.44,
            geocoder=lambda _q: [],
        )
        assert resolved.source == "gps"
        assert resolved.latitude == 52.55

    def test_falls_back_to_city_center(self):
        resolved = resolve_coordinates(
            name="Mystery Place",
            address=None,
            city="Austin",
            country="USA",
            geocoder=lambda _q: [],
        )
        assert resolved.source == "city_center"
        assert resolved.latitude == pytest.approx(30.2672)

    def test_create_business_integration_uses_geocoder(self, client, test_user, sample_business):
        headers = auth_header(client, test_user.email, "Test1234!")
        fake = ResolvedCoordinates(latitude=52.501, longitude=13.401, source="nominatim")

        with patch("app.services.business_create.resolve_coordinates", return_value=fake):
            response = client.post(
                "/businesses",
                headers=headers,
                json={
                    "name": "Geocoded Spot",
                    "address": "Unter den Linden 1",
                    "city": "Berlin",
                    "country": "Germany",
                    "category": "test-cafe",
                },
            )

        assert response.status_code == 201
        loc = response.json()["location"]
        assert loc["latitude"] == 52.501
        assert loc["longitude"] == 13.401
