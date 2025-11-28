import { useState, useEffect } from "react";
import axios from "axios";
import UttarakhandMap from "./components/UttarakhandMap";
import "./App.css";

export default function App() {
  const [start, setStart] = useState("Dehradun");
  const [end, setEnd] = useState("Haridwar");

  const [bestRoute, setBestRoute] = useState([]);
  const [bestEta, setBestEta] = useState(null);
  const [mainRoute, setMainRoute] = useState([]);
  const [mainEta, setMainEta] = useState(null);

  const [mapRoute, setMapRoute] = useState([]);

  // AUTO REROUTING
  const [autoRouteActive, setAutoRouteActive] = useState(false);

  async function findRoute() {
    const res = await axios.post("http://127.0.0.1:8000/route", {
      start,
      end,
    });

    setBestRoute(res.data.best_route);
    setBestEta(res.data.best_eta);
    setMainRoute(res.data.main_route);
    setMainEta(res.data.main_eta);

    setMapRoute(res.data.best_route);
  }

  // AUTO REROUTING EVERY 20 SECONDS
  useEffect(() => {
    if (!autoRouteActive || !start || !end || bestRoute.length === 0) return;

    const interval = setInterval(async () => {
      try {
        const res = await axios.post("http://127.0.0.1:8000/route", {
          start,
          end,
        });

        const newRoute = res.data.best_route;
        const newEta = res.data.best_eta;

        if (newEta < bestEta * 0.9) {
          alert("⚠ Traffic changed — auto-rerouting…");

          setBestRoute(newRoute);
          setBestEta(newEta);
          setMainRoute(res.data.main_route);
          setMainEta(res.data.main_eta);

          setMapRoute(newRoute);
        }
      } catch (err) {
        console.log("Auto-reroute error:", err);
      }
    }, 20000);

    return () => clearInterval(interval);
  }, [autoRouteActive, bestEta, bestRoute, start, end]);

  return (
    <div className="app-container">
      <div className="sidebar">

        <h2>Uttarakhand Smart Emergency Routing</h2>

        <label>Start City:</label>
        <select value={start} onChange={(e) => setStart(e.target.value)}>
          <option>Dehradun</option>
          <option>Rishikesh</option>
          <option>Haridwar</option>
          <option>Kotdwar</option>
          <option>Haldwani</option>
          <option>Nainital</option>
          <option>Almora</option>
        </select>

        <label>Destination City:</label>
        <select value={end} onChange={(e) => setEnd(e.target.value)}>
          <option>Dehradun</option>
          <option>Rishikesh</option>
          <option>Haridwar</option>
          <option>Kotdwar</option>
          <option>Haldwani</option>
          <option>Nainital</option>
          <option>Almora</option>
        </select>

        <button onClick={findRoute}>Find Best Route</button>

        <button
          style={{ marginTop: "10px", backgroundColor: "#444" }}
          onClick={() => setAutoRouteActive(!autoRouteActive)}
        >
          {autoRouteActive ? "🛑 Stop Auto-Rerouting" : "♻ Enable Auto-Rerouting"}
        </button>

        <div className="result-box">
          <h3>Best Route (Traffic Aware)</h3>
          <p><b>Route:</b> {bestRoute.join(" → ")}</p>
          <p><b>ETA:</b> {bestEta} min</p>
        </div>

        <div className="result-box">
          <h3>Main Route (Distance Based)</h3>
          <p><b>Route:</b> {mainRoute.join(" → ")}</p>
          <p><b>ETA:</b> {mainEta} min</p>
        </div>

      </div>

      <div className="map-area">
        <UttarakhandMap highlightRoute={mapRoute} />
      </div>
    </div>
  );
}
