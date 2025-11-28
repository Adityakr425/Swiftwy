import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  GeoJSON
} from "react-leaflet";

import { useEffect, useState, useRef } from "react";
import axios from "axios";
import L from "leaflet";

import boundaryUrl from "../data/Uttarakhand.geojson?url";

// Blue pin
const blueIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// Hospital icon
const hospitalIcon = L.icon({
  iconUrl: "/icons/hospital.png",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
});

// City coords
const NODE_COORDS = {
  Dehradun: [30.3165, 78.0322],
  Rishikesh: [30.0869, 78.2676],
  Haridwar: [29.9457, 78.1642],
  Kotdwar: [29.7919, 78.5415],
  Haldwani: [29.2183, 79.5276],
  Nainital: [29.3919, 79.4549],
  Almora: [29.5970, 79.6591],
};

// Traffic color
function getColor(level) {
  if (level < 20) return "green";
  if (level < 50) return "yellow";
  if (level < 80) return "orange";
  return "red";
}

export default function UttarakhandMap({ highlightRoute }) {
  const [roads, setRoads] = useState([]);
  const [boundary, setBoundary] = useState(null);
  const [hospitals, setHospitals] = useState([]);
  const [realRoute, setRealRoute] = useState([]);
  const mapRef = useRef(null);

  const MAPTILER_KEY = "zUPK5Dk5R7QtJPh1ALTy";

  function fixBoundary(geojson) {
    function flip(coords) {
      return coords.map((c) =>
        Array.isArray(c[0]) ? flip(c) : [c[1], c[0]]
      );
    }

    const copy = JSON.parse(JSON.stringify(geojson));
    copy.features.forEach((f) => {
      if (f.geometry.type === "Polygon")
        f.geometry.coordinates = flip(f.geometry.coordinates);
      else if (f.geometry.type === "MultiPolygon")
        f.geometry.coordinates = f.geometry.coordinates.map((p) => flip(p));
    });

    return copy;
  }

  useEffect(() => {
    fetch(boundaryUrl)
      .then((r) => r.json())
      .then((j) => setBoundary(fixBoundary(j)));
  }, []);

  useEffect(() => {
    if (!boundary || !mapRef.current) return;
    const layer = L.geoJSON(boundary);
    mapRef.current.fitBounds(layer.getBounds(), { padding: [40, 40] });
  }, [boundary]);

  // Fetch traffic
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/traffic")
      .then((res) => setRoads(res.data.roads || []));
  }, []);

  // Fetch hospitals
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/hospitals")
      .then((res) => setHospitals(res.data.hospitals || []));
  }, []);

  // Load ORS curved route
  useEffect(() => {
    if (!highlightRoute || highlightRoute.length < 2) return;

    const load = async () => {
      const start = highlightRoute[0];
      const end = highlightRoute[highlightRoute.length - 1];

      const res = await axios.post("http://127.0.0.1:8000/realroute", {
        start,
        end,
      });

      const pts = res.data.points || [];
      setRealRoute(pts);

      if (pts.length && mapRef.current) {
        mapRef.current.fitBounds(L.latLngBounds(pts), {
          padding: [40, 40],
        });
      }
    };

    load();
  }, [highlightRoute]);

  // Determine route color based on max traffic segment
  let routeColor = "red";
  if (highlightRoute.length > 1) {
    let maxT = 0;
    highlightRoute.forEach((city, i) => {
      if (i === highlightRoute.length - 1) return;
      const next = highlightRoute[i + 1];

      const seg = roads.find(
        (r) =>
          (r.start === city && r.end === next) ||
          (r.start === next && r.end === city)
      );

      if (seg) maxT = Math.max(maxT, seg.traffic);
    });

    routeColor = getColor(maxT);
  }

  return (
    <div style={{ position: "relative", height: "100%", width: "100%" }}>
      <MapContainer
        center={[30.3165, 78.0322]}
        zoom={8}
        style={{ height: "100%", width: "100%" }}
        whenCreated={(map) => (mapRef.current = map)}
      >
        <TileLayer
          url={`https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=${MAPTILER_KEY}`}
          attribution="&copy; MapTiler"
        />

        {/* Boundary */}
        {boundary && (
          <GeoJSON
            data={boundary}
            style={{
              color: "#0066ff",
              weight: 2,
              fillOpacity: 0.02,
            }}
          />
        )}

        {/* ORS REAL COLORED ROUTE */}
        {realRoute.length > 1 && (
          <Polyline
            positions={realRoute}
            pathOptions={{
              color: routeColor,
              weight: 7,
              opacity: 0.9,
            }}
          />
        )}

        {/* Hospital markers */}
        {hospitals.map((h) => (
          <Marker key={h.id} position={h.coords} icon={hospitalIcon}>
            <Popup>
              <b>{h.name}</b>
              <br />
              ({h.city})
            </Popup>
          </Marker>
        ))}

        {/* Start marker */}
        {realRoute.length > 0 && (
          <Marker
            position={NODE_COORDS[highlightRoute[0]]}
            icon={blueIcon}
          />
        )}

        {/* End marker */}
        {realRoute.length > 0 && (
          <Marker
            position={NODE_COORDS[highlightRoute[highlightRoute.length - 1]]}
            icon={blueIcon}
          />
        )}
      </MapContainer>

      {/* TRAFFIC LEGEND */}
      <div className="traffic-legend">
        <div className="traffic-item">
          <div className="traffic-color-box" style={{ background: "green" }}></div>
          Low Traffic
        </div>
        <div className="traffic-item">
          <div className="traffic-color-box" style={{ background: "yellow" }}></div>
          Moderate Traffic
        </div>
        <div className="traffic-item">
          <div className="traffic-color-box" style={{ background: "orange" }}></div>
          Heavy Traffic
        </div>
        <div className="traffic-item">
          <div className="traffic-color-box" style={{ background: "red" }}></div>
          Severe Traffic
        </div>
      </div>
    </div>
  );
}
