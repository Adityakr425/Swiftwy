from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import RouteQuery, RouteSuggestion
from data import get_live_data
from graph import calculate_best_route
import subprocess
import os
import signal

app = FastAPI()

# Allow CORS for all domains (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store Vite process globally so we don't start it twice
vite_process = None


def start_frontend():
    """
    Starts the React/Vite frontend automatically.
    Prevents multiple processes from being created.
    Works on Windows.
    """

    global vite_process

    if vite_process is not None:
        print("Frontend already running.")
        return

    frontend_path = os.path.join(os.getcwd(), "traffic-ui")

    if not os.path.exists(frontend_path):
        print("❌ ERROR: Frontend folder 'traffic-ui' not found!")
        return

    print("🚀 Starting Vite frontend...")

    # Windows-safe start
    vite_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_path,
        shell=True
    )


@app.on_event("startup")
def on_startup():
    print("🚦 Backend started. Launching frontend...")
    start_frontend()


# -----------------------------
# LIVE TRAFFIC ENDPOINT
# -----------------------------
@app.get("/traffic")
def traffic_data():
    roads, hotspots = get_live_data()
    return {
        "roads": roads,
        "hotspots": hotspots
    }


# -----------------------------
# ROUTE SUGGESTION ENDPOINT
# -----------------------------
@app.post("/route", response_model=RouteSuggestion)
def get_route(data: RouteQuery):
    best_route, best_eta, main_route, main_eta = calculate_best_route(
        start=data.start,
        end=data.end
    )

    return {
        "status": "ok",
        "main_route": main_route,
        "main_eta": main_eta,
        "best_route": best_route,
        "best_eta": best_eta
    }


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
    finally:
        # Kill the Vite process on exit
        if vite_process:
            print("🛑 Stopping frontend...")
            vite_process.send_signal(signal.SIGTERM)
