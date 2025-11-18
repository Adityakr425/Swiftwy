import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  GeoJSON
} from "react-leaflet";

import { useEffect, useState, useRef } from "react";
import axios from "axios";
import L from "leaflet";

import boundaryUrl from "../data/Uttarakhand.geojson?url";

export default function UttarakhandMap({ highlightRoute }) {
  const [roads, setRoads] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [boundary, setBoundary] = useState(null);
  const mapRef = useRef(null);

  const MAPTILER_KEY = "zUPK5Dk5R7QtJPh1ALTy";

  // --- FIX 1: AUTO-CONVERT BOUNDARY COORDINATES ---
  function fixGeoJSONCoordinates(geojson) {
    function flip(coords) {
      return coords.map(c => {
        if (Array.isArray(c[0])) return flip(c);
        return [c[1], c[0]]; // swap lon<->lat
      });
    }

    const fixed = JSON.parse(JSON.stringify(geojson));

    fixed.features.forEach(f => {
      if (f.geometry.type === "Polygon") {
        f.geometry.coordinates = flip(f.geometry.coordinates);
      }
      if (f.geometry.type === "MultiPolygon") {
        f.geometry.coordinates = f.geometry.coordinates.map(poly => flip(poly));
      }
    });

    return fixed;
  }

  // Load GEOJSON boundary with fix
  useEffect(() => {
    fetch(boundaryUrl)
      .then(res => res.json())
      .then(data => {
        const fixed = fixGeoJSONCoordinates(data);
        setBoundary(fixed);
      });
  }, []);

  // Fit map bounds when boundary loads
  useEffect(() => {
    if (!boundary || !mapRef.current) return;

    const layer = L.geoJSON(boundary);
    const bounds = layer.getBounds();
    mapRef.current.fitBounds(bounds, { padding: [20, 20] });
  }, [boundary]);

  // Load live traffic
  useEffect(() => {
    loadData();
    const t = setInterval(loadData, 3000);
    return () => clearInterval(t);
  }, []);

  async function loadData() {
    try {
      const res = await axios.get("http://127.0.0.1:8000/traffic");
      setRoads(res.data.roads || []);
      setHotspots(res.data.hotspots || []);
    } catch (err) {
      console.log("API error:", err.message);
    }
  }

  // Build exact pair set for highlight logic
  function pairSet(route) {
    const set = new Set();
    for (let i = 0; i < route.length - 1; i++) {
      set.add(`${route[i]}|${route[i + 1]}`);
    }
    return set;
  }

  const routePairs = pairSet(highlightRoute);

  function isHighlighted(r) {
    return routePairs.has(`${r.start}|${r.end}`);
  }

  function getColor(c) {
    if (c < 30) return "green";
    if (c < 70) return "orange";
    return "red";
  }

  return (
    <MapContainer
      center={[30.3165, 78.0322]}
      zoom={8}
      style={{ height: "100%", width: "100%" }}
      whenCreated={map => (mapRef.current = map)}
    >
      <TileLayer
        url={`https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`}
        attribution='&copy; MapTiler &copy; OpenStreetMap contributors'
      />

      {boundary && (
        <GeoJSON
          data={boundary}
          style={{
            color: "#0066ff",
            weight: 2,
            fillOpacity: 0.1
          }}
        />
      )}

      {/* Roads */}
      {roads.map(r => (
        <Polyline
          key={r.id}
          positions={r.coords}
          pathOptions={{
            color: isHighlighted(r) ? getColor(r.congestion) : "#ccc",
            weight: isHighlighted(r) ? 7 : 3,
            opacity: isHighlighted(r) ? 1 : 0.4
          }}
        >
          <Popup>
            <b>{r.name}</b>
            <br />
            Congestion: {r.congestion}%
          </Popup>
        </Polyline>
      ))}

      {/* Hotspots */}
      {hotspots.map(h => (
        <Marker key={h.id} position={h.coords}>
          <Popup>{h.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
