# GraphHopper Enhanced

A small CLI wrapper around the GraphHopper Geocoding and Routing APIs.

Features added:
- CLI with argparse and non-interactive mode (--from, --to)
- Environment variable support for the API key (GRAPHOPPER_API_KEY)
- Improved error handling and timeouts
- Better formatting of distance and duration output
- Interactive fallback mode for convenience

Usage examples:

Install requirements:

```powershell
python -m pip install -r requirements.txt
```

Run interactively:

```powershell
python graphhopper-enhanced.py
```

Run single-shot (non-interactive):

```powershell
$env:GRAPHOPPER_API_KEY = "<your-key>"; python graphhopper-enhanced.py --from "Berlin" --to "Potsdam" --vehicle car --units km
```

Notes:
- Prefer setting `GRAPHOPPER_API_KEY` in your environment instead of hardcoding it.
- This repository contains a minimal single-file tool; consider adding tests and CI for production use.

Map popup feature:

- The CLI/module can render an interactive map of the route into an HTML file using `folium`.
- Install folium (it's listed in `requirements.txt`). When the routing API is called we request `points_encoded=false` so the response contains raw coordinates suitable for drawing.
- If available, the module will open the route in your system default browser automatically.

Example (single-shot):

```powershell
$env:GRAPHOPPER_API_KEY = "<your-key>"
python graphhopper_enhanced.py --from "Berlin" --to "Potsdam" --vehicle car --units km
```

If the routing response contains coordinates, a browser tab/window will open with the map.
