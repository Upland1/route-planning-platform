# Emergency Response & Route Planning Platform

This project is a geospatial application designed to simulate an emergency response system using real urban data. It combines advanced search algorithms, spatial data structures, and computational geometry to solve navigation and resource allocation problems in Zapopan, Jalisco.

## Overview

The platform addresses three main challenges in urban mobility:

- **Optimized Location Search**: Uses KD-Trees to instantly find the nearest map node to any GPS coordinate, reducing search time from linear to logarithmic complexity.

- **Emergency Routing**: Implements a Voronoi Partition logic to automatically assign the nearest hospital based on the user's location (influence areas) rather than just straight-line distance.

- **Pathfinding**: Calculates the optimal route using the **A* (A-Star)** algorithm over a weighted road network graph extracted from OpenStreetMap.

## Features

- **Real-time Map Data**: Downloads and processes live street data using OSMnx.

- **Interactive Interface**: A web-based frontend using Leaflet.js to visualize the map, user location, and calculated routes.

- **Smart Hospital Assignment**: Automatically detects which hospital "owns" the region where the emergency occurred.

- **High Performance**: Utilizes `scipy.spatial` and `networkx` for efficient geometric calculations and graph traversal.

## Requirements

- Python 3.8+
- Modern Web Browser (Chrome, Firefox, Edge)
- Internet Connection (to download map tiles and OSM data)

## Installation

1. **Clone the repository:**

2. **Install dependencies:**

It is recommended to use a virtual environment.

```bash
pip install -r requirements.txt
```

## How to Run

The application consists of a Python backend (FastAPI) and a simple HTML frontend. You need to run both concurrently.

### 1. Start the Backend API

This server handles the heavy lifting: downloading the map, building the KD-Tree, and calculating routes.

Open a terminal in the project root and run:

```bash
python -m uvicorn Interface.server:app --reload --host 127.0.0.1 --port 8000
```

Wait until you see the message: `Application startup complete.`

### 2. Start the Frontend

You need to serve the HTML file. You can use Python's built-in HTTP server or the Live Server extension in VS Code.

**Option A (Python):**

Open a new terminal window and run:

```bash
cd Interface
python -m http.server 5500
```

**Option B (VS Code):**

Open `Interface/index.html` and click "Go Live" (if Live Server extension is installed).

### 3. Use the Application

1. Open your browser and go to `http://127.0.0.1:5500/index.html`.
2. You will see the map of Zapopan.
3. Click anywhere on the map to simulate an emergency.
4. The system will:
   - Identify your location.
   - Find the correct hospital for your sector (Voronoi region).
   - Draw the optimal driving route in red.

## Troubleshooting

### Module not found errors

Make sure you're running commands from the project root directory and your virtual environment is activated:

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### CORS issues

The `server.py` already includes CORS middleware. Make sure you're accessing the frontend through `http://127.0.0.1:5500` and not opening the HTML file directly (`file://`).

### Installation issues on Windows

For geospatial packages, using Conda is recommended:

```bash
conda create -n route python=3.10 -y
conda activate route
conda install -c conda-forge osmnx geopandas rtree shapely pyproj fiona numpy scipy matplotlib networkx pandas -y
pip install fastapi "uvicorn[standard]"
```