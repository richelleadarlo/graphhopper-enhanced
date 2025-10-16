import requests
import urllib.parse
import webbrowser
import folium
import os
from tabulate import tabulate
from colorama import Fore, init

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
        print(Fore.CYAN + f"Geocoding {full_name} (Type: {value})")
    else:
        lat = lng = None
        full_name = location
        print(Fore.RED + f"Geocode API error: {status}, message: " + json_data.get("message", "Invalid input"))

    return status, lat, lng, full_name, country


# --- Function: Display Air Route ---
def display_air_route(orig, dest):
    print(Fore.BLUE + "\nCalculating flight route...")

    # Simple flight assumptions
    from math import radians, sin, cos, sqrt, atan2
    R = 6371.0  # Earth radius in km

    lat1, lon1 = radians(orig[1]), radians(orig[2])
    lat2, lon2 = radians(dest[1]), radians(dest[2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance_km = R * c

    # Flight time: assume 850 km/h
    hours = distance_km / 850
    cost = distance_km * 0.12  # Estimated 0.12 USD/km

    print(Fore.GREEN + f"Estimated Air Distance: {distance_km:.1f} km")
    print(Fore.GREEN + f"Approximate Flight Duration: {hours:.2f} hours")
    print(Fore.MAGENTA + f"Estimated Ticket Cost: ${cost:.2f}")
    print("=================================================")

    # --- Create Map ---
    m = folium.Map(location=[(orig[1] + dest[1]) / 2, (orig[2] + dest[2]) / 2], zoom_start=4)
    folium.Marker([orig[1], orig[2]], popup=f"Origin: {orig[3]}", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([dest[1], dest[2]], popup=f"Destination: {dest[3]}", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([[orig[1], orig[2]], [dest[1], dest[2]]], color="blue", weight=3, opacity=0.7).add_to(m)

    html_file = "air_route_map.html"
    m.save(html_file)
    print(Fore.CYAN + f"Opening flight route map in browser...")
    webbrowser.open('file://' + os.path.realpath(html_file))


# --- Main Program ---
while True:
    print(Fore.YELLOW + "\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on GraphHopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot, airplane ✈️")
    print("+++++++++++++++++++++++++++++++++++++++++++++")

    profile = ["car", "bike", "foot", "airplane"]
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

    # --- User inputs ---
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
        # --- Detect cross-country or long routes ---
        same_country = (orig[4] == dest[4])
        if vehicle == "airplane" or not same_country:
            display_air_route(orig, dest)
            continue

        # --- GraphHopper for land routes ---
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
            distance_m = data["paths"][0]["distance"]
            time_ms = data["paths"][0]["time"]
            km = distance_m / 1000
            miles = km / 1.61
            sec = int(time_ms / 1000 % 60)
            minute = int(time_ms / 1000 / 60 % 60)
            hour = int(time_ms / 1000 / 60 / 60)
            ascend = data["paths"][0].get("ascend", 0)
            descend = data["paths"][0].get("descend", 0)
            fuel = (km / 10) if vehicle == "car" else 0

            dist_str = f"{km:.1f} km" if unit_choice == "km" else f"{miles:.1f} miles"
            print(Fore.GREEN + f"Distance: {dist_str}")
            print(Fore.GREEN + f"Duration: {hour:02d}:{minute:02d}:{sec:02d}")
            print(Fore.CYAN + f"Elevation Gain: {ascend:.1f} m | Loss: {descend:.1f} m")
            if fuel > 0:
                print(Fore.MAGENTA + f"Estimated Fuel: {fuel:.1f} L")

            directions = []
            for step in data["paths"][0]["instructions"]:
                text = step["text"]
                d_km = step["distance"] / 1000
                d_miles = d_km / 1.61
                dist_display = f"{d_km:.2f} km / {d_miles:.2f} mi"
                directions.append([text, dist_display])
            print(tabulate(directions, headers=["Instruction", "Distance"], tablefmt="grid"))

            map_url = f"https://graphhopper.com/maps/?point={orig[1]},{orig[2]}&point={dest[1]},{dest[2]}&vehicle={vehicle}"
            print(Fore.BLUE + f"\nOpening map in browser: {map_url}\n")
            webbrowser.open(map_url)
        else:
            print(Fore.RED + "Error: " + data.get("message", "Route could not be found."))
    print(Fore.WHITE + "=================================================")
