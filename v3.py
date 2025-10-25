# ========================================================================================================
# COMMENTS from Team DevOps 

# Shanyka Tiemsim - Route History
# As one can see, the route history feature is an accessible and convenient function, as it enables users 
# to remember their past trips for comparison or reference. It does not only make  the  program  a  route 
# generator, but a more interactive travel or journey assistant. By automatically saving the route into a 
# text file, the data collected from previous sessions aren't lost and can be  utilized  for  the  future. 
# Hence, it gives a sense of progress to the user as someone who is navigating through the roads, skies or 
# seas. In future versions, it would be nice to have a visual interface for the history or save a preload 
# of past routes based on the records that have already been saved.
# ==========================================================================================================



import requests
import urllib.parse
import webbrowser
import folium
import os
from tabulate import tabulate
from colorama import Fore, Style, init
from math import radians, sin, cos, sqrt, atan2
import time
import pyfiglet

# Initialize colorama
init(autoreset=True)

# --- Replace with your actual GraphHopper API key ---
API_KEY = "f7635944-8b58-4494-aab4-6367c4890e31"

GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"
ROUTE_URL = "https://graphhopper.com/api/1/route?"

# ===================== WELCOME BANNER =====================


banner = pyfiglet.figlet_format("RouteFinder", font="slant")
print(Fore.CYAN + banner)
print(Fore.YELLOW + "Powered by GraphHopper API 🌐\n")

# ===================== GEOCODING FUNCTION =====================
def geocoding(location, key):
    while location.strip() == "":
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
        print(Fore.CYAN + f"📍 Geocoding {full_name} (Type: {value})")
    else:
        lat = lng = None
        full_name = location
        print(Fore.RED + f"⚠️ Geocode API error: {status}, message: " + json_data.get("message", "Invalid input"))

    return status, lat, lng, full_name, country


# ===================== AIR ROUTE FUNCTION =====================
def display_air_route(orig, dest):
    print(Fore.BLUE + "\n✈️ Calculating flight route...")

    R = 6371.0  # Earth radius in km
    lat1, lon1 = radians(orig[1]), radians(orig[2])
    lat2, lon2 = radians(dest[1]), radians(dest[2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance_km = R * c

    # Flight assumptions
    hours = distance_km / 850
    cost = distance_km * 0.12  # Estimated cost per km

    stats = [
        ["Estimated Air Distance", f"{distance_km:.1f} km"],
        ["Approximate Duration", f"{hours:.2f} hours"],
        ["Estimated Ticket Cost", f"${cost:.2f}"],
    ]
    print(Fore.YELLOW + tabulate(stats, headers=["Flight Info", "Value"], tablefmt="fancy_grid"))

    # --- Create flight route map ---
    m = folium.Map(location=[(orig[1] + dest[1]) / 2, (orig[2] + dest[2]) / 2], zoom_start=4)
    folium.Marker([orig[1], orig[2]], popup=f"Origin: {orig[3]}", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([dest[1], dest[2]], popup=f"Destination: {dest[3]}", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([[orig[1], orig[2]], [dest[1], dest[2]]], color="blue", weight=3, opacity=0.7).add_to(m)

    html_file = "air_route_map.html"
    m.save(html_file)
    print(Fore.CYAN + f"🌐 Opening flight route map in browser...")
    webbrowser.open('file://' + os.path.realpath(html_file))

    # --- Log route history (UTF-8 safe) ---
    with open("route_history.txt", "a", encoding="utf-8") as log:
        log.write(f"{orig[3]} → {dest[3]} (Airplane, {distance_km:.1f} km, {hours:.2f} hrs)\n")


# ===================== MAIN PROGRAM =====================


while True:
    print(Fore.YELLOW + "\n═══════════════════════════════════════════════")
    print("🚗 Available vehicle profiles:")
    print("═══════════════════════════════════════════════")
    print("car    🚗")
    print("bike   🚴")
    print("foot   🚶")
    print("airplane ✈️")
    print("═══════════════════════════════════════════════")

    profile = ["car", "bike", "foot", "airplane"]
    vehicle = input(Fore.WHITE + "Enter a vehicle profile: ").strip().lower()

    if vehicle in ["quit", "q"]:
        print(Fore.MAGENTA + "👋 Exiting program... Goodbye!")
        break
    elif vehicle not in profile:
        print(Fore.RED + "⚠️ Invalid vehicle. Defaulting to car.")
        vehicle = "car"

    unit_choice = input("Display distance in (km/miles)? ").lower().strip()
    if unit_choice not in ["km", "miles"]:
        unit_choice = "km"

    # --- User inputs ---
    loc1 = input(Fore.GREEN + "🟢 Starting Location: ")
    if loc1 in ["quit", "q"]:
        break
    orig = geocoding(loc1, API_KEY)

    loc2 = input(Fore.GREEN + "🔴 Destination: ")
    if loc2 in ["quit", "q"]:
        break
    dest = geocoding(loc2, API_KEY)

    print(Fore.WHITE + "=================================================")

    if orig[0] == 200 and dest[0] == 200:
        # Detect international routes or airplane request
        same_country = (orig[4] == dest[4])
        if vehicle == "airplane" or not same_country:
            display_air_route(orig, dest)
            continue

        # --- Land Route with GraphHopper ---
        
        # =============================================================================================================
        # DEVS - GEOTRAVEL                                                                                                         =
        # Displays trip summary (distance, time, elevation, fuel) in a neat table for quick route overview - JUSTIN   =
        #                                                                                                             =
        #==============================================================================================================
        
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"
        route_url = ROUTE_URL + urllib.parse.urlencode({"key": API_KEY, "vehicle": vehicle}) + op + dp

        r = requests.get(route_url)
        status = r.status_code
        data = r.json()

        print(Fore.CYAN + f"📡 Routing API Status: {status}")
        print(Fore.CYAN + f"🔗 Routing API URL: {route_url}")
        print("=================================================")
        print(Fore.YELLOW + f"🗺️ Directions from {orig[3]} to {dest[3]} by {vehicle}")
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

            summary = [
                ["Total Distance", dist_str],
                ["Estimated Duration", f"{hour:02d}:{minute:02d}:{sec:02d}"],
                ["Elevation Gain / Loss", f"{ascend:.1f} m / {descend:.1f} m"],
                ["Fuel Used", f"{fuel:.1f} L" if fuel > 0 else "N/A"]
            ]
            print(Fore.GREEN + tabulate(summary, headers=["Trip Info", "Details"], tablefmt="fancy_grid"))

            # Directions Table
            directions = []
            for step in data["paths"][0]["instructions"]:
                text = step["text"]
                d_km = step["distance"] / 1000
                d_miles = d_km / 1.61
                dist_display = f"{d_km:.2f} km / {d_miles:.2f} mi"
                directions.append([text, dist_display])
            print(Fore.CYAN + tabulate(directions, headers=["Instruction", "Distance"], tablefmt="rounded_outline"))

            # --- Open route in browser ---
            map_url = f"https://graphhopper.com/maps/?point={orig[1]},{orig[2]}&point={dest[1]},{dest[2]}&vehicle={vehicle}"
            print(Fore.BLUE + f"\n🌍 Opening map in browser: {map_url}\n")
            webbrowser.open(map_url)

            # --- Log route ---
            with open("route_history.txt", "a", encoding="utf-8") as log:
                log.write(f"{orig[3]} → {dest[3]} ({vehicle}, {dist_str}, {hour:02d}:{minute:02d}:{sec:02d})\n")

        else:
            print(Fore.RED + "❌ Error: " + data.get("message", "Route could not be found."))
    else:
        print(Fore.RED + "❌ Geocoding failed for one or both locations.")

    print(Fore.WHITE + "=================================================")
