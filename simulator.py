# simulator.py
import random
import config

# Named nodes (cities) used by the graph
NODES = ["Dehradun", "Rishikesh", "Haridwar", "Kotdwar", "Haldwani", "Nainital", "Almora"]

# Static base network (you can expand with more realistic coords and segments)
_base_segments = [
    {
        "id": 1,
        "name": "Dehradun - Rishikesh",
        "start": "Dehradun",
        "end": "Rishikesh",
        "distance_km": 45.0,
        "coords": [[30.3165, 78.0322], [30.0869, 78.2676]],
        "speed_kmph": 50
    },
    {
        "id": 2,
        "name": "Rishikesh - Haridwar",
        "start": "Rishikesh",
        "end": "Haridwar",
        "distance_km": 30.0,
        "coords": [[30.0869, 78.2676], [29.9457, 78.1642]],
        "speed_kmph": 55
    },
    {
        "id": 3,
        "name": "Dehradun - Kotdwar",
        "start": "Dehradun",
        "end": "Kotdwar",
        "distance_km": 85.0,
        "coords": [[30.3165, 78.0322], [29.7919, 78.5415]],
        "speed_kmph": 50
    },
    {
        "id": 4,
        "name": "Kotdwar - Haldwani",
        "start": "Kotdwar",
        "end": "Haldwani",
        "distance_km": 120.0,
        "coords": [[29.7919, 78.5415], [29.2183, 79.5276]],
        "speed_kmph": 60
    },
    {
        "id": 5,
        "name": "Haridwar - Kotdwar",
        "start": "Haridwar",
        "end": "Kotdwar",
        "distance_km": 90.0,
        "coords": [[29.9457, 78.1642], [29.7919, 78.5415]],
        "speed_kmph": 55
    },
    {
        "id": 6,
        "name": "Haldwani - Nainital",
        "start": "Haldwani",
        "end": "Nainital",
        "distance_km": 65.0,
        "coords": [[29.2183, 79.5276], [29.3919, 79.4549]],
        "speed_kmph": 40
    },
    {
        "id": 7,
        "name": "Nainital - Almora",
        "start": "Nainital",
        "end": "Almora",
        "distance_km": 60.0,
        "coords": [[29.3919, 79.4549], [29.5970, 79.6591]],
        "speed_kmph": 40
    },
    {
        "id": 8,
        "name": "Dehradun - Haridwar (Direct)",
        "start": "Dehradun",
        "end": "Haridwar",
        "distance_km": 50.0,
        "coords": [[30.3165, 78.0322], [29.9457, 78.1642]],
        "speed_kmph": 50
    }
]

def _randomize_segment(seg):
    """Return a copy of seg with randomized congestion, eta and speed adjusted."""
    s = seg.copy()
    # congestion random between 10 and 85
    s["congestion"] = random.randint(10, 85)
    # speed influenced by congestion
    base_speed = s.get("speed_kmph", 40)
    # reduce speed according to congestion (simple model)
    speed = max(config.MIN_SPEED_KMPH, int(base_speed * (1 - s["congestion"] / 120)))
    s["speed_kmph"] = speed
    # ETA in minutes = distance / speed * 60
    s["eta_min"] = max(1, int((s.get("distance_km", config.DEFAULT_SEGMENT_KM) / speed) * 60))
    return s

def segment_status():
    """
    Returns a list of current road segments with dynamic congestion/speed/eta.
    Each item contains keys:
      id, name, start, end, distance_km, coords, congestion, speed_kmph, eta_min
    """
    return [_randomize_segment(s) for s in _base_segments]

def hotspot_status():
    """
    Returns a list of hotspots (points) derived from segments or fixed POIs.
    Each item: id, name, coords [lat,lon], congestion, eta_min
    """
    # create hotspot for segments that currently have high congestion
    hotspots = []
    for s in segment_status():
        if s["congestion"] >= config.CONGESTION_MED:
            # use the end coordinate as hotspot location
            coord = s["coords"][-1] if s.get("coords") else None
            hotspots.append({
                "id": f"hs-{s['id']}",
                "name": s["name"],
                "coords": coord,
                "congestion": s["congestion"],
                "eta_min": s["eta_min"]
            })
    # also add a few fixed POIs (ensures some markers)
    fixed = [
        {"id": "poi-ddn", "name": "Dehradun Clock Tower", "coords":[30.3256, 78.0415], "congestion": random.randint(20,80), "eta_min": random.randint(3,15)},
        {"id": "poi-nai", "name": "Mall Road Nainital", "coords":[29.3919, 79.4549], "congestion": random.randint(20,90), "eta_min": random.randint(5,18)}
    ]
    hotspots.extend(fixed)
    return hotspots
