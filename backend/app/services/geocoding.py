import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

from app.config import settings

# City centers aligned with frontend LOCATION_CITIES (fallback when geocoding fails).
CITY_CENTERS: dict[tuple[str, str], tuple[float, float]] = {
    ("Berlin", "Germany"): (52.52, 13.405),
    ("Mumbai", "India"): (19.076, 72.8777),
    ("Austin", "USA"): (30.2672, -97.7431),
}

NominatimFetcher = Callable[[str], list[dict]]


@dataclass(frozen=True)
class ResolvedCoordinates:
    latitude: float
    longitude: float
    source: str  # nominatim | gps | city_center


def build_geocode_query(
    name: str,
    address: str | None,
    city: str,
    country: str,
) -> str:
    parts = [name.strip()]
    if address and address.strip():
        parts.append(address.strip())
    parts.append(city.strip())
    parts.append(country.strip())
    return ", ".join(parts)


def city_center_coords(city: str, country: str) -> tuple[float, float] | None:
    key = (city.strip(), country.strip())
    return CITY_CENTERS.get(key)


def parse_nominatim_results(results: list[dict]) -> tuple[float, float] | None:
    if not results:
        return None
    first = results[0]
    try:
        return float(first["lat"]), float(first["lon"])
    except (KeyError, TypeError, ValueError):
        return None


def fetch_nominatim(query: str) -> list[dict]:
    if not settings.geocoding_enabled:
        return []

    params = urllib.parse.urlencode(
        {
            "q": query,
            "format": "json",
            "limit": 1,
            "addressdetails": 0,
        }
    )
    url = f"{settings.nominatim_base_url.rstrip('/')}/search?{params}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": settings.geocoding_user_agent},
    )
    try:
        with urllib.request.urlopen(
            request, timeout=settings.geocoding_timeout_seconds
        ) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []


def resolve_coordinates(
    *,
    name: str,
    address: str | None,
    city: str,
    country: str,
    client_latitude: float | None = None,
    client_longitude: float | None = None,
    geocoder: NominatimFetcher | None = None,
) -> ResolvedCoordinates:
    lookup = geocoder or fetch_nominatim
    query = build_geocode_query(name, address, city, country)
    coords = parse_nominatim_results(lookup(query))
    if coords:
        return ResolvedCoordinates(latitude=coords[0], longitude=coords[1], source="nominatim")

    if client_latitude is not None and client_longitude is not None:
        return ResolvedCoordinates(
            latitude=client_latitude,
            longitude=client_longitude,
            source="gps",
        )

    center = city_center_coords(city, country)
    if center:
        return ResolvedCoordinates(latitude=center[0], longitude=center[1], source="city_center")

    raise ValueError(f"No coordinates available for {city}, {country}")
