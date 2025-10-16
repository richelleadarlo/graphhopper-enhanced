import argparse
import logging
import os
import sys
import urllib.parse

import requests
from colorama import Fore, init
from tabulate import tabulate

# Initialize colorama for colored terminal output
init(autoreset=True)

# Default GraphHopper endpoints
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"
ROUTE_URL = "https://graphhopper.com/api/1/route"

# Fallback API key (kept for backward compatibility). Prefer using env var GRAPHOPPER_API_KEY.
API_KEY = os.environ.get("GRAPHOPPER_API_KEY", "f7635944-8b58-4494-aab4-6367c4890e31")

logger = logging.getLogger(__name__)


def get_api_key(cmdline_key: str | None) -> str:
    """Return API key: prefer command-line value, then env var, then fallback constant.

    Simple contract: returns a non-empty string. If missing, functions will likely fail with HTTP errors.
    """
    if cmdline_key:
        return cmdline_key
    return os.environ.get("GRAPHOPPER_API_KEY") or API_KEY


def geocode(location: str, key: str) -> dict:
    """Call GraphHopper geocode API for a single location.

    Returns a dict with keys: status (int), lat (float|None), lng (float|None), name (str), raw (response json)
    """
    if not location:
        return {"status": 400, "lat": None, "lng": None, "name": "", "raw": None}

    params = {"q": location, "limit": 1, "key": key}
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        data = resp.json() if resp.content else {}
    except requests.RequestException as e:
        logger.debug("Geocode request failed", exc_info=e)
        return {"status": 0, "lat": None, "lng": None, "name": location, "raw": None}

    if resp.status_code == 200 and data.get("hits"):
        hit = data["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        name = hit.get("name") or location
        return {"status": 200, "lat": lat, "lng": lng, "name": name, "raw": data}

    return {"status": resp.status_code, "lat": None, "lng": None, "name": location, "raw": data}


def get_route(start_lat: float, start_lng: float, end_lat: float, end_lng: float, vehicle: str, key: str) -> dict:
    """Call GraphHopper routing API and return parsed JSON (or error info).

    Returns dict with keys: status (int) and data (json or None)
    """
    params = {"vehicle": vehicle, "key": key, "points_encoded": "false"}
    # Build point parameters manually to avoid double-encoding weirdness
    points = [(start_lat, start_lng), (end_lat, end_lng)]
    url = ROUTE_URL
    try:
        # append points to params via query string
        query = urllib.parse.urlencode(params)
        for lat, lng in points:
            query += f"&point={lat}%2C{lng}"
        full_url = f"{url}?{query}"
        resp = requests.get(full_url, timeout=15)
        data = resp.json() if resp.content else {}
        return {"status": resp.status_code, "data": data, "url": full_url}
    except requests.RequestException as e:
        logger.debug("Routing request failed", exc_info=e)
        return {"status": 0, "data": None, "url": None}


def format_duration(ms: int) -> str:
    total_seconds = int(ms / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_distance(meters: float, unit: str = "km") -> str:
    km = meters / 1000.0
    if unit == "miles":
        miles = km / 1.61
        return f"{miles:.2f} miles"
    return f"{km:.2f} km"


def print_route_summary(route_json: dict, orig_name: str, dest_name: str, vehicle: str, unit_choice: str):
    paths = route_json.get("paths")
    if not paths:
        print(Fore.RED + "No path found in routing response.")
        return

    p = paths[0]
    distance_m = p.get("distance", 0)
    time_ms = p.get("time", 0)
    ascend = p.get("ascend", 0)
    descend = p.get("descend", 0)

    km = distance_m / 1000.0
    fuel = (km / 10) if vehicle == "car" else 0

    print(Fore.CYAN + f"Routing result: from {orig_name} to {dest_name} (profile: {vehicle})")
    print(Fore.GREEN + f"Distance: {format_distance(distance_m, unit_choice)}")
    print(Fore.GREEN + f"Duration: {format_duration(time_ms)}")
    print(Fore.CYAN + f"Elevation Gain: {ascend:.1f} m | Loss: {descend:.1f} m")
    if fuel > 0:
        print(Fore.MAGENTA + f"Estimated fuel: {fuel:.2f} L (approx)")

    # Instructions table
    instructions = p.get("instructions", [])
    rows = []
    for instr in instructions:
        text = instr.get("text", "")
        d = instr.get("distance", 0)
        rows.append([text, format_distance(d, unit_choice)])

    if rows:
        print(tabulate(rows, headers=[Fore.YELLOW + "Instruction", Fore.YELLOW + "Distance"], tablefmt="grid"))


def show_route_map(route_json: dict, map_filename: str | None = None) -> str | None:
    """Render the route geometry into an interactive HTML map using folium.

    Requires that the routing response contains 'points' with 'coordinates' (points_encoded=false).
    Returns the path to the generated HTML file or None on failure.
    """
    try:
        import folium
        import webbrowser
        import tempfile
        import os
    except Exception:
        logger.info("folium or webbrowser not available; install folium to use map rendering")
        return None

    paths = route_json.get("paths")
    if not paths:
        return None

    p = paths[0]
    points = p.get("points")
    coords = None
    if points:
        # points is expected to be a dict with 'coordinates' when points_encoded=false
        coords = points.get("coordinates")

    if not coords:
        return None

    # coordinates are [lng, lat] pairs per GeoJSON spec
    polyline = [(lat, lng) for lng, lat in coords]

    # center map on midpoint
    mid = polyline[len(polyline) // 2]
    m = folium.Map(location=mid, zoom_start=13)
    folium.PolyLine(locations=polyline, color="blue", weight=5, opacity=0.8).add_to(m)
    folium.Marker(location=polyline[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(location=polyline[-1], popup="End", icon=folium.Icon(color="red")).add_to(m)

    if not map_filename:
        fd, map_filename = tempfile.mkstemp(prefix="route_", suffix=".html")
        os.close(fd)

    m.save(map_filename)
    webbrowser.open(f"file:///{os.path.abspath(map_filename)}")
    return map_filename


def run_interactive(default_key: str):
    profiles = ["car", "bike", "foot"]
    while True:
        print(Fore.YELLOW + "\nAvailable vehicle profiles: car, bike, foot")
        vehicle = input(Fore.WHITE + "Enter a vehicle profile (or 'q' to quit): ").strip().lower()
        if vehicle in ("q", "quit"):
            print(Fore.MAGENTA + "Goodbye")
            return
        if vehicle not in profiles:
            print(Fore.RED + "Invalid vehicle; defaulting to car")
            vehicle = "car"

        unit_choice = input("Display distance in (km/miles)? ").strip().lower()
        if unit_choice not in ("km", "miles"):
            unit_choice = "km"

        loc1 = input(Fore.GREEN + "Starting location (or 'q' to quit): ")
        if loc1 in ("q", "quit"):
            return
        orig = geocode(loc1, default_key)

        loc2 = input(Fore.GREEN + "Destination (or 'q' to quit): ")
        if loc2 in ("q", "quit"):
            return
        dest = geocode(loc2, default_key)

        if orig["status"] == 200 and dest["status"] == 200:
            result = get_route(orig["lat"], orig["lng"], dest["lat"], dest["lng"], vehicle, default_key)
            print(Fore.CYAN + f"Routing API Status: {result.get('status')}\nURL: {result.get('url')}")
            if result.get("status") == 200 and result.get("data"):
                print_route_summary(result["data"], orig["name"], dest["name"], vehicle, unit_choice)
            else:
                print(Fore.RED + "Routing failed. See status and/or check your API key and network.")
        else:
            print(Fore.RED + f"Geocoding failed for: {loc1 if orig['status']!=200 else ''} {loc2 if dest['status']!=200 else ''}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="GraphHopper enhanced CLI")
    parser.add_argument("--from", dest="from_loc", help="Starting location")
    parser.add_argument("--to", dest="to_loc", help="Destination location")
    parser.add_argument("--vehicle", choices=["car", "bike", "foot"], default="car", help="Vehicle profile")
    parser.add_argument("--units", choices=["km", "miles"], default="km", help="Distance units")
    parser.add_argument("--api-key", dest="api_key", help="GraphHopper API key (overrides env GRAPHOPPER_API_KEY)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--show-map", action="store_true", help="Open route in a browser map (requires folium)")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    key = get_api_key(args.api_key)
    if not key:
        print(Fore.RED + "No GraphHopper API key provided. Set GRAPHOPPER_API_KEY or pass --api-key.")
        return 2

    # If both from and to are provided, run single-shot non-interactive mode
    if args.from_loc and args.to_loc:
        orig = geocode(args.from_loc, key)
        dest = geocode(args.to_loc, key)
        if orig["status"] == 200 and dest["status"] == 200:
            result = get_route(orig["lat"], orig["lng"], dest["lat"], dest["lng"], args.vehicle, key)
            print(Fore.CYAN + f"Routing API Status: {result.get('status')}\nURL: {result.get('url')}")
            if result.get("status") == 200 and result.get("data"):
                print_route_summary(result["data"], orig["name"], dest["name"], args.vehicle, args.units)
                if args.show_map:
                    map_path = show_route_map(result["data"])
                    if map_path:
                        print(Fore.CYAN + f"Map saved and opened: {map_path}")
                    else:
                        print(Fore.RED + "Could not render map (missing coordinates or folium not installed).")
                return 0
            print(Fore.RED + "Routing failed.")
            return 1
        print(Fore.RED + "Geocoding failed for one or both locations.")
        return 1

    # Otherwise fall back to interactive mode
    run_interactive(key)
    return 0


if __name__ == "__main__":
    sys.exit(main())
