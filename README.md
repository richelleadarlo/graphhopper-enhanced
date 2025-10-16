# GraphHopper Enhanced

A CLI wrapper around the GraphHopper Geocoding and Routing APIs with interactive map visualization.

## Features

- CLI with argparse (single-shot and interactive modes)
- Environment variable support for API key (`GRAPHOPPER_API_KEY`)
- Interactive map visualization with folium
- **NEW**: Flask-based localhost server to view maps in browser
- Vehicle profile icons (car 🚗, bike 🚴, foot 🚶)
- Improved error handling and timeouts
- Colored terminal output

## Installation

```powershell
python -m pip install -r requirements.txt
```

## Usage

### Interactive mode
```powershell
python graphhopper_enhanced.py
```

### Single-shot (non-interactive)
```powershell
$env:GRAPHOPPER_API_KEY = "<your-key>"
python graphhopper_enhanced.py --from "Berlin" --to "Potsdam" --vehicle car --units km --show-map
```

### Localhost server mode (NEW!)
Open the map in a browser via Flask server:
```powershell
$env:GRAPHOPPER_API_KEY = "<your-key>"
python graphhopper_enhanced.py --from "Berlin" --to "Potsdam" --vehicle bike --serve --port 5000
```
Then open `http://localhost:5000/map` in your browser to see the interactive map with vehicle icons.

### CLI Options
- `--from`: Starting location
- `--to`: Destination location
- `--vehicle`: Vehicle profile (car, bike, foot) - default: car
- `--units`: Distance units (km, miles) - default: km
- `--show-map`: Open route in browser (static HTML file)
- `--map-output PATH`: Save map HTML to specific path
- `--serve`: Start Flask server to serve map on localhost
- `--port PORT`: Port for Flask server (default: 5000)
- `--api-key`: GraphHopper API key (overrides env var)
- `--debug`: Enable debug logging

## Vehicle Profile Icons

The map displays different icons based on vehicle profile:
- 🚗 **Car**: Blue car icon
- 🚴 **Bike**: Orange bicycle icon  
- 🚶 **Foot**: Green person icon

## Notes

- Set `GRAPHOPPER_API_KEY` environment variable instead of hardcoding
- Localhost server mode requires Flask
- Route coordinates require `points_encoded=false` in API request
