import { useState } from "react";
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

  async function findRoute() {
    if (!start || !end) {
      alert("Please select both start and end cities.");
      return;
    }

    try {
      const res = await axios.post("http://127.0.0.1:8000/route", {
        start,
        end,
      });

      setBestRoute(res.data.best_route || []);
      setBestEta(res.data.best_eta || 0);
      setMainRoute(res.data.main_route || []);
      setMainEta(res.data.main_eta || 0);
    } catch (err) {
      console.error("Route API error:", err);
      alert("Error fetching route.");
    }
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Route Finder</h2>

        <label>Start City:</label>
        <select value={start} onChange={(e) => setStart(e.target.value)}>
          <option>Dehradun</option>
          <option>Rishikesh</option>
          <option>Kotdwar</option>
          <option>Haridwar</option>
          <option>Haldwani</option>
          <option>Nainital</option>
          <option>Almora</option>
        </select>

        <label>End City:</label>
        <select value={end} onChange={(e) => setEnd(e.target.value)}>
          <option>Dehradun</option>
          <option>Rishikesh</option>
          <option>Kotdwar</option>
          <option>Haridwar</option>
          <option>Haldwani</option>
          <option>Nainital</option>
          <option>Almora</option>
        </select>

        <button onClick={findRoute}>Find Best Route</button>

        {/* BEST ROUTE */}
        <div className="result-box">
          <h3>Best Route</h3>
          <p><b>Route:</b> {bestRoute.join(" → ")}</p>
          <p><b>ETA:</b> {bestEta} min</p>
        </div>

        {/* MAIN ROUTE */}
        <div className="result-box">
          <h3>Main Route</h3>
          <p><b>Route:</b> {mainRoute.join(" → ")}</p>
          <p><b>ETA:</b> {mainEta} min</p>
        </div>
      </div>

      {/* MAP */}
      <div className="map-area">
        <UttarakhandMap highlightRoute={bestRoute} />
      </div>
    </div>
  );
}
