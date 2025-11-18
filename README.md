# Uttarakhand Traffic API (Local, Simulated)

## 1) Create venv & install
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
pip install -r requirements.txt
2) Start API
uvicorn app:app --reload --port 8000
The API will be available at: http://127.0.0.1:8000
3) Test Endpoints
•	GET /health → API status
•	GET /traffic → returns roads + hotspots with simulated congestion/speeds/ETA
•	GET /route?start=R-05&end=R-07 → best route (Kumaon chain example)
•	GET /route?start=R-01&end=R-03 → compare main vs alternates (Garhwal example)
4) Frontend Integration Notes
•	CORS is open (*) for dev; tighten for production.
•	Poll /traffic every 3 seconds (see FRONTEND_POLL_MS).
•	Draw road polylines with returned coords and color by congestion.
•	On route click, call /route?start=<segIdA>&end=<segIdB> and show popup.
5) Customization
•	Add/edit segments & distances in data.py.
•	Adjust thresholds in config.py.
•	Extend graph connections in graph.py → ROUTE_GRAPH + MAIN_CHAINS.
6) Notes
•	All speeds/ETAs are simulated and non-authoritative.
•	Coordinates are approximate for demo visualization. 
