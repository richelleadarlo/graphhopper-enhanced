import requests
import urllib.parse
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# --- Replace with your actual GraphHopper API key ---
API_KEY = "f7635944-8b58-4494-aab4-6367c4890e31"

GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"
ROUTE_URL = "https://graphhopper.com/api/1/route?"

# Function: Geocoding
def geocoding(location, key):
    while location == "":
        location = input("Enter the location again: ")

    url = GEOCODE_URL + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    response = requests.get(url)
    json_data = response.json()
    status = response.status_code

    if status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        full_name = f"{name}, {state}, {country}" if state and country else name
        print(Fore.CYAN + f"Geocoding API URL for {full_name} (Type: {value})\n" + url)
    else:
        lat = lng = None
        full_name = location
        print(Fore.RED + f"Geocode API status: {status}\nError message: " + json_data.get("message", "Invalid input or missing data"))

    return status, lat, lng, full_name


# --- Main Program ---
while True:
    print(Fore.YELLOW + "\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on GraphHopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")

    profile = ["car", "bike", "foot"]
    vehicle = input(Fore.WHITE + "Enter a vehicle profile: ").strip().lower()

    if vehicle in ["quit", "q"]:
        print(Fore.MAGENTA + "Exiting program...")
        break
    elif vehicle not in profile:
        print(Fore.RED + "Invalid vehicle. Defaulting to car.")
        vehicle = "car"

    unit_choice = input("Display distance in (km/miles)? ").lower().strip()
    if unit_choice not in ["km", "miles"]:
        unit_choice = "km"

    # --- User inputs for start and destination ---
    loc1 = input(Fore.GREEN + "Starting Location: ")
    if loc1 in ["quit", "q"]:
        break
    orig = geocoding(loc1, API_KEY)

    loc2 = input(Fore.GREEN + "Destination: ")
    if loc2 in ["quit", "q"]:
        break
    dest = geocoding(loc2, API_KEY)

    print(Fore.WHITE + "=================================================")

    if orig[0] == 200 and dest[0] == 200:
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"
        route_url = ROUTE_URL + urllib.parse.urlencode({"key": API_KEY, "vehicle": vehicle}) + op + dp

        r = requests.get(route_url)
        status = r.status_code
        data = r.json()

        print(Fore.CYAN + f"Routing API Status: {status}\nRouting API URL:\n{route_url}")
        print("=================================================")
        print(Fore.YELLOW + f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("=================================================")

        if status == 200:
            # Calculate distance/time
            distance_m = data["paths"][0]["distance"]
            time_ms = data["paths"][0]["time"]
            km = distance_m / 1000
            miles = km / 1.61
            sec = int(time_ms / 1000 % 60)
            minute = int(time_ms / 1000 / 60 % 60)
            hour = int(time_ms / 1000 / 60 / 60)

            # Calculate elevation gain/loss
            ascend = data["paths"][0].get("ascend", 0)
            descend = data["paths"][0].get("descend", 0)

            # Estimate fuel (for car only)
            fuel = (km / 10) if vehicle == "car" else 0  # 10 km/L average

            # Format distance
            dist_str = f"{km:.1f} km" if unit_choice == "km" else f"{miles:.1f} miles"

            print(Fore.GREEN + f"Distance Traveled: {dist_str}")
            print(Fore.GREEN + f"Trip Duration: {hour:02d}:{minute:02d}:{sec:02d}")
            print(Fore.CYAN + f"Elevation Gain: {ascend:.1f} m | Loss: {descend:.1f} m")
            if fuel > 0:
                print(Fore.MAGENTA + f"Estimated Fuel Consumption: {fuel:.1f} L")
            print("=================================================")

            # --- Directions Table ---
            directions = []
            for step in data["paths"][0]["instructions"]:
                text = step["text"]
                d_km = step["distance"] / 1000
                d_miles = d_km / 1.61
                dist_display = f"{d_km:.2f} km / {d_miles:.2f} mi"
                directions.append([text, dist_display])

            print(tabulate(directions, headers=[Fore.YELLOW + "Instruction", Fore.YELLOW + "Distance"], tablefmt="grid"))

        else:
            print(Fore.RED + "Error message: " + data.get("message", "Route could not be found."))
            print("*************************************************")

    print(Fore.WHITE + "=================================================")
