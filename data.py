# data.py
from simulator import segment_status, hotspot_status

def get_live_data():
    """
    Returns (roads, hotspots)
    roads: list of segment dictionaries
    hotspots: list of hotspot dictionaries
    """
    roads = segment_status()
    hotspots = hotspot_status()
    return roads, hotspots
