from dataclasses import dataclass
import datetime
import requests
import time

base = "https://tt.horner.tj"
request_timeout = 10

@dataclass
class stop_data:
    stopId : str
    stopCode : str
    name : str
    lat : float
    lon : float

@dataclass
class trip_data:
    tripId : str
    
    routeId : str
    routeName : str
    routeColor : str # hex
    
    stopId : str
    stopName : str
    
    headsign : str
    directionId : int
    
    arrivalTime : int
    departureTime : int

    vehicle : int
    isRealTime : bool

def get_response(request):
    response = requests.get(base + request, timeout=request_timeout)
    response.raise_for_status()
    return response.json()

def get_stops_in_bbox(bbox : str):
    stops_response = get_response(f"/stops/within/{bbox}")

    stops = []
    for stop_response in stops_response:
        stops.append(stop(
            stop_response['stopId'],
            stop_response['stopCode'],
            stop_response['name'],
            stop_response['lat'],
            stop_response['lon']
        ))

    return stops

print(get_stops_in_bbox("-72.524341,42.387466,-72.522960,42.388068"))