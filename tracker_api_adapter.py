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

@dataclass 
class stoproute_data:
    routeId : str
    name : str
    color : str # hex
    headsigns : list[str]


def get_response(request):
    response = requests.get(base + request, timeout=request_timeout)
    response.raise_for_status()
    return response.json()

def get_stops_in_bbox(bbox : str) -> list[stop_data]:
    stops_responses = get_response(f"/stops/within/{bbox}")

    stops = []
    for stop_response in stops_responses:
        stops.append(stop_data(
            stop_response['stopId'],
            stop_response['stopCode'],
            stop_response['name'],
            stop_response['lat'],
            stop_response['lon']
        ))

    return stops

def get_routes_serving_stop(stop_id : str) -> list[stoproute_data]:
    routes_responses = get_response(f"/stops/{stop_id}/routes")
    
    routes = []
    for route_response in routes_responses:
        routes.append(stoproute_data(
            route_response['routeId'],
            route_response['name'],
            route_response['color'],
            route_response['headsigns']
        ))

    return routes

def get_schedule(route_stop_pairs : str) -> list[trip_data]:
    schedule_responses = get_response(f"/schedule/{route_stop_pairs}")

    schedules = []
    for schedule_response in schedule_responses:
        schedules.append(trip_data(
            schedule_response['tripId'],
            schedule_response['routeId'],
            schedule_response['routeName'],
            schedule_response['routeColor'],
            schedule_response['stopId'],
            schedule_response['stopName'],
            schedule_response['headsign'],
            schedule_response['directionId'],
            schedule_response['arrivalTime'],
            schedule_response['departureTime'],
            schedule_response['vehicle'],
            schedule_response['isRealTime'],
        ))


#print(get_stops_in_bbox("-72.524341,42.387466,-72.522960,42.388068"))