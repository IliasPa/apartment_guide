from __future__ import annotations

import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = WORKSPACE_ROOT / "apartment_guide"
PROPERTIES_INDEX_PATH = SITE_ROOT / "data" / "properties.json"
BEACHES_PATH = SITE_ROOT / "dataset" / "beaches.json"
OUTPUT_PATH = SITE_ROOT / "data" / "beach_distance_matrix.json"
OSRM_BASE_URL = "https://router.project-osrm.org/route/v1/driving"
USER_AGENT = "ApartmentGuideDistanceScript/1.0"


def log(message: str) -> None:
    print(message, file=sys.stderr)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_number(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number)


def extractCoordsFromGoogleMapsUrl(url: str | None) -> tuple[float, float] | None:
    if not url:
        return None

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key in ("q", "query", "ll"):
        for value in query.get(key, []):
            match = re.search(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)", value)
            if match:
                return float(match.group(1)), float(match.group(2))

    combined = f"{parsed.path} {parsed.fragment}"
    at_match = re.search(r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", combined)
    if at_match:
        return float(at_match.group(1)), float(at_match.group(2))

    return None


def resolve_coordinates(entity: dict[str, Any], label: str) -> tuple[float, float] | None:
    coords = entity.get("coordinates") or {}
    lat = coords.get("lat")
    lon = coords.get("lon")
    if is_number(lat) and is_number(lon):
      return float(lat), float(lon)

    extracted = extractCoordsFromGoogleMapsUrl(entity.get("mapLink"))
    if extracted:
        return extracted

    log(f"Warning: no coordinates found for {label}")
    return None


def fetch_route(origin: tuple[float, float], destination: tuple[float, float], label: str) -> dict[str, float] | None:
    origin_lat, origin_lon = origin
    dest_lat, dest_lon = destination
    url = (
        f"{OSRM_BASE_URL}/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        "?overview=false"
    )

    for attempt in range(1, 4):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            routes = payload.get("routes") or []
            if not routes:
                raise ValueError("No route returned")
            route = routes[0]
            distance_km = round(float(route["distance"]) / 1000, 1)
            drive_time_min = int(round(float(route["duration"]) / 60))
            return {
                "distance_km": distance_km,
                "drive_time_min": drive_time_min,
            }
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
            if attempt == 3:
                log(f"Warning: route failed for {label}: {exc}")
                return None
            time.sleep(attempt)

    return None


def load_properties() -> list[dict[str, Any]]:
    properties_index = read_json(PROPERTIES_INDEX_PATH)
    properties: list[dict[str, Any]] = []
    for entry in properties_index:
        property_id = entry["id"]
        metadata_path = SITE_ROOT / "data" / "properties" / property_id / "property.json"
        metadata = read_json(metadata_path)
        coords = resolve_coordinates(metadata, f"property {property_id}")
        if not coords:
            continue
        metadata["resolvedCoordinates"] = coords
        properties.append(metadata)
    return properties


def load_beaches() -> list[dict[str, Any]]:
    beaches = read_json(BEACHES_PATH).get("items", [])
    resolved: list[dict[str, Any]] = []
    for item in beaches:
        coords = resolve_coordinates(item, f"beach {item.get('id', item.get('name', 'unknown'))}")
        if not coords:
            continue
        item["resolvedCoordinates"] = coords
        resolved.append(item)
    return resolved


def build_matrix() -> dict[str, dict[str, dict[str, float]]]:
    properties = load_properties()
    beaches = load_beaches()
    matrix: dict[str, dict[str, dict[str, float]]] = {}

    for property_meta in properties:
        property_id = property_meta["id"]
        property_coords = property_meta["resolvedCoordinates"]
        matrix[property_id] = {}
        for beach in beaches:
            beach_id = beach["id"]
            route = fetch_route(property_coords, beach["resolvedCoordinates"], f"{property_id} -> {beach_id}")
            if route:
                matrix[property_id][beach_id] = route
            time.sleep(0.2)

    return matrix


def main() -> int:
    matrix = build_matrix()
    write_json(OUTPUT_PATH, matrix)
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())