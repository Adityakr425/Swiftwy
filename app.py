from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import RouteQuery, RouteSuggestion
from data import get_live_data
from graph import calculate_best_route, build_graphs, shortest_path
from hospitals import HOSPITALS
import subprocess
import os
import signal
import requests

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vite_process = None


def start_frontend():
    """Auto-start React frontend."""
    global vite_process

    if vite_process is not None:
        return

    path = os.path.join(os.getcwd(), "traffic-ui")
    if not os.path.exists(path):
        print("❌ 'traffic-ui' folder not found. Start React manually.")
        return

    try:
        vite_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=path,
            shell=True,
        )
        print("▶️ Started Vite dev server")
    except Exception as e:
        print("⚠️ Could not start frontend:", e)


@app.on_event("startup")
def on_startup():
    print("🚦 Backend started.")
    start_frontend()


# =====================================
# LIVE TRAFFIC ENDPOINT
# =====================================
@app.get("/traffic")
def traffic():
    roads, hotspots = get_live_data()
    return {"roads": roads, "hotspots": hotspots}


# =====================================
# SIMULATOR ROUTE ENDPOINT
# =====================================
@app.post("/route", response_model=RouteSuggestion)
def route(data: RouteQuery):
    best_route, best_eta, main_route, main_eta = calculate_best_route(
        data.start, data.end
    )
    return {
        "status": "ok",
        "main_route": main_route,
        "main_eta": main_eta,
        "best_route": best_route,
        "best_eta": best_eta,
    }


# =====================================
# REAL ORS ROUTE
# =====================================

NODE_COORDS = {
    "Dehradun": (78.0322, 30.3165),
    "Rishikesh": (78.2676, 30.0869),
    "Haridwar": (78.1642, 29.9457),
    "Kotdwar": (78.5415, 29.7919),
    "Haldwani": (79.5276, 29.2183),
    "Nainital": (79.4549, 29.3919),
    "Almora": (79.6591, 29.5970),
}

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImQ3YmFhOGNhMzZkZDRlODFiN2ZkY2E5OGZiNjUwMTE1IiwiaCI6Im11cm11cjY0In0="


@app.post("/realroute")
def real_route(data: RouteQuery):
    start = data.start
    end = data.end

    if start not in NODE_COORDS or end not in NODE_COORDS:
        raise HTTPException(400, "Invalid city")

    body = {
        "coordinates": [
            [NODE_COORDS[start][0], NODE_COORDS[start][1]],
            [NODE_COORDS[end][0], NODE_COORDS[end][1]],
        ]
    }

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"

    try:
        res = requests.post(
            url,
            json=body,
            headers={"Authorization": ORS_API_KEY},
            timeout=20,
        )

        geo = res.json()
        coords = geo["features"][0]["geometry"]["coordinates"]
        latlon = [[c[1], c[0]] for c in coords]

        return {"points": latlon}

    except Exception as e:
        raise HTTPException(502, f"ORS failed: {e}")


# =====================================
# HOSPITALS
# =====================================
@app.get("/hospitals")
def hospitals():
    return {"hospitals": HOSPITALS}


# =====================================
# ROUTE TO NEAREST HOSPITAL
# =====================================
@app.post("/route_to_hospital")
def route_to_hospital(data: RouteQuery):
    start_city = data.start

    graph, graph_low = build_graphs()

    if start_city not in graph:
        raise HTTPException(400, "Invalid start city")

    best_choice = None

    for h in HOSPITALS:
        city = h["city"]
        if city not in graph:
            continue

        route_best = shortest_path(graph_low, start_city, city)
        if not route_best:
            continue

        eta_best = sum(graph_low[route_best[i]][route_best[i + 1]]["eta"]
                       for i in range(len(route_best) - 1))

        route_main = shortest_path(graph, start_city, city)
        eta_main = sum(graph[route_main[i]][route_main[i + 1]]["eta"]
                       for i in range(len(route_main) - 1))

        if best_choice is None or eta_best < best_choice["eta_best"]:
            best_choice = {
                "hospital": h,
                "route_best": route_best,
                "eta_best": eta_best,
                "route_main": route_main,
                "eta_main": eta_main,
            }

    if best_choice is None:
        raise HTTPException(404, "No reachable hospital")

    return {
        "status": "ok",
        "hospital": best_choice["hospital"],
        "best_route": best_choice["route_best"],
        "best_eta": best_choice["eta_best"],
        "main_route": best_choice["route_main"],
        "main_eta": best_choice["eta_main"],
    }


if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
    finally:
        if vite_process:
            vite_process.send_signal(signal.SIGTERM)
