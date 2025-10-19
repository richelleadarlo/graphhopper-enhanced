<h1>DevNet & Chill | Activity 3 - Social Coding | Enhancing a Python Project using GraphHopper API</h1>

<h3>Overview</h3>
DevNet & Chill’s GraphHopper Enhanced Route Planner is a Python-based route mapping application that integrates the GraphHopper Directions API with enhanced UI features and an optional airplane simulation mode for international routes.
The project demonstrates teamwork, API integration, and feature enhancement within a collaborative GitHub workflow for the Cisco DevNet Associate (DEVASC) course.

<h3>Features</h3>

- Multi-Mode Route Planning – Supports car, bike, foot, and airplane ✈️

- Real-Time Map Visualization – Opens route maps directly in your browser

- International Flight Simulation – Calculates distance, duration, and estimated airfare

- Color-Coded, Tabulated Terminal Output – Sleek and easy to read

- Elevation & Fuel Estimates – For land routes

- Route Logging – Automatically saves route history to a UTF-8 text file

- Graphical Enhancements – Banner, icons, and tables for a modern CLI experience


<h3>Tech Stack</h3>

- Python 3

- GraphHopper Directions API
  
- Requests – for REST API calls
  
- Folium – for map generation and display
  
- Tabulate – for elegant table formatting
  
- Colorama – for colored terminal output
  
- Webbrowser & OS – for automatic route display


<h3>Setup Instructions</h3>

1) Clone this repo: 
git clone https://github.com/yourusername/graphhopper-enhanced-route-planner.git
cd graphhopper-enhanced-route-planner

2) Install dependencies: pip install requests folium tabulate colorama

3) Add your GraphHopper API Key from https://www.graphhopper.com/: Inyour code, insert your API at API_KEY = "your_api_key_here"

4) Run the application: python graphhopper_enhanced.py


<h3>Usage</h3>

- Choose a vehicle profile: car, bike, foot, or airplane

- Input your starting location and destination

- Watch your terminal display distance, duration, and step-by-step directions

- The route map automatically opens in your default web browser 🌍

- For airplane mode, the app simulates an international flight route using a world map via Folium



