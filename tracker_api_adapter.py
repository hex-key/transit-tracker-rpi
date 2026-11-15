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
class stoproute_data:
    routeId : str
    name : str
    color : str # hex
    headsigns : list[str]



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
    schedule_responses = get_response(f"/schedule/{route_stop_pairs}")["trips"]

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
            schedule_response['isRealtime'],
        ))

    return schedules



def get_next_trips_from_bbox(bbox : str, count : int = 3) -> list[trip_data]:
    # get stops in bbox
    stop_datas = get_stops_in_bbox(bbox)

    schedule_str = ""
    for stop in stop_datas:
        # get each route at these stops
        routes = get_routes_serving_stop(stop.stopId)

        # build route,stop pairs
        if schedule_str: schedule_str += ";"
        schedule_str += ";".join(
            f"{route.routeId},{stop.stopId}" for route in routes
        )

    # get upcoming trips with these pairs
    return sorted(get_schedule(schedule_str), key=lambda s: s.arrivalTime)[:count]



def convert_duration_to_eta(delta_seconds : int) -> str:
    hours, r = divmod(delta_seconds, 3600)
    minutes, r = divmod(delta_seconds, 60)

    out_str = ""
    if hours > 0:
        out_str += f"{int(hours)}h "
    out_str += f"{int(minutes)}m"

    return out_str



def main():
    """Sample usage"""
    
    bbox_studio_arts = "-72.524341,42.387466,-72.522960,42.388068"
    stop_datas = get_stops_in_bbox(bbox_studio_arts)
    for i, stop in enumerate(stop_datas):
        print(f"\n######\nSTOP {i}")
        print(stop)

    schedule_str = ""
    for stop in stop_datas:
        routes = get_routes_serving_stop(stop.stopId)
        
        print(f"\n######\nROUTES SERVING STOP {stop.stopId} {stop.name}\n")
        for route in routes:
            print(f"\n### ROUTE {route.name} AT {stop.name}")
            print(route)

        if schedule_str: schedule_str += ";"
        schedule_str += ";".join(
            f"{route.routeId},{stop.stopId}" for route in routes
        )

    trip_datas = sorted(get_schedule(schedule_str), key=lambda s: s.arrivalTime)
    print("\n###### UPCOMING TRIPS AT THESE STOPS")
    for trip in trip_datas:
        print(f"\nROUTE {trip.routeId} TO {trip.headsign}")
        print(trip)
    

    
        

    

    


if __name__ == "__main__":
    main()