import random
import time
import config

# Named nodes (cities) used by the graph
NODES = ["Dehradun", "Rishikesh", "Haridwar", "Kotdwar",
         "Haldwani", "Nainital", "Almora"]

# Static base network (coords are [lat, lon])
_base_segments = [
    {
        "id": 1,
        "name": "Dehradun - Rishikesh",
        "start": "Dehradun",
        "end": "Rishikesh",
        "distance_km": 45.0,
        "coords": [[30.3165, 78.0322], [30.0869, 78.2676]],
        "speed_kmph": 50,
    },
    {
        "id": 2,
        "name": "Rishikesh - Haridwar",
        "start": "Rishikesh",
        "end": "Haridwar",
        "distance_km": 30.0,
        "coords": [[30.0869, 78.2676], [29.9457, 78.1642]],
        "speed_kmph": 55,
    },
    {
        "id": 3,
        "name": "Dehradun - Kotdwar",
        "start": "Dehradun",
        "end": "Kotdwar",
        "distance_km": 85.0,
        "coords": [[30.3165, 78.0322], [29.7919, 78.5415]],
        "speed_kmph": 50,
    },
    {
        "id": 4,
        "name": "Kotdwar - Haldwani",
        "start": "Kotdwar",
        "end": "Haldwani",
        "distance_km": 120.0,
        "coords": [[29.7919, 78.5415], [29.2183, 79.5276]],
        "speed_kmph": 60,
    },
    {
        "id": 5,
        "name": "Haridwar - Kotdwar",
        "start": "Haridwar",
        "end": "Kotdwar",
        "distance_km": 90.0,
        "coords": [[29.9457, 78.1642], [29.7919, 78.5415]],
        "speed_kmph": 55,
    },
    {
        "id": 6,
        "name": "Haldwani - Nainital",
        "start": "Haldwani",
        "end": "Nainital",
        "distance_km": 65.0,
        "coords": [[29.2183, 79.5276], [29.3919, 79.4549]],
        "speed_kmph": 40,
    },
    {
        "id": 7,
        "name": "Nainital - Almora",
        "start": "Nainital",
        "end": "Almora",
        "distance_km": 60.0,
        "coords": [[29.3919, 79.4549], [29.5970, 79.6591]],
        "speed_kmph": 40,
    },
    {
        "id": 8,
        "name": "Dehradun - Haridwar (Direct)",
        "start": "Dehradun",
        "end": "Haridwar",
        "distance_km": 50.0,
        "coords": [[30.3165, 78.0322], [29.9457, 78.1642]],
        "speed_kmph": 50,
    },
]

# ----------------------------------------------------------------------
# 15-MINUTE CACHING (stable values for UI)
# ----------------------------------------------------------------------
_last_update_time = 0
_cached_segments = None


def _randomize_segment(seg):
    """Return a copy of seg with randomized congestion/speed/eta."""
    s = seg.copy()

    # Congestion between 10% and 85%
    s["congestion"] = random.randint(10, 85)

    base_speed = s.get("speed_kmph", 40)
    speed = max(config.MIN_SPEED_KMPH, int(base_speed * (1 - s["congestion"] / 120)))
    s["speed_kmph"] = speed

    s["eta_min"] = max(1, int((s["distance_km"] / speed) * 60))
    return s


def segment_status():
    """
    Return list of segments with congestion, speed, eta.
    Cached for 15 minutes so map markers do not flicker too fast.
    """
    global _last_update_time, _cached_segments

    now = time.time()
    if _cached_segments is None or now - _last_update_time > 900:  # 900 sec = 15 min
        _cached_segments = [_randomize_segment(s) for s in _base_segments]
        _last_update_time = now

    return _cached_segments


def hotspot_status():
    """
    Hotspots derived from current segment status.
    Uses last coordinate of each segment (already [lat, lon]).
    """
    hotspots = []
    segs = segment_status()

    for s in segs:
        if s["congestion"] >= config.CONGESTION_MED:
            coord = s["coords"][-1]
            hotspots.append(
                {
                    "id": f"hs-{s['id']}",
                    "name": s["name"],
                    "coords": coord,
                    "congestion": s["congestion"],
                    "eta_min": s["eta_min"],
                }
            )

    fixed = [
        {
            "id": "poi-ddn",
            "name": "Dehradun Clock Tower",
            "coords": [30.3256, 78.0415],
            "congestion": 40,
            "eta_min": 10,
        },
        {
            "id": "poi-nai",
            "name": "Mall Road Nainital",
            "coords": [29.3919, 79.4549],
            "congestion": 50,
            "eta_min": 12,
        },
    ]

    hotspots.extend(fixed)
    return hotspots
