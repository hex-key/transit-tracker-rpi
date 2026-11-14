import datetime
import requests
import time

base = "https://tt.horner.tj"

BBOX_HAIGIS_MALL = "-72.527109,42.386394,-72.525301,42.387728"
BBOX_STUDIO_ARTS = "-72.524341,42.387466,-72.522960,42.388068"

bounding_box = BBOX_STUDIO_ARTS
request_timeout = 10

def get_response(request):
    response = requests.get(base + request, timeout=request_timeout)
    response.raise_for_status()
    return response.json()

def get_departures():
    stops = get_response(f"/stops/within/{bounding_box}")
    departures = []

    for stop in stops:
        routes = get_response(f"/stops/{stop['stopId']}/routes")
        schedule_str = ";".join(
            f"{route['routeId']},{stop['stopId']}" for route in routes
        )
        if not schedule_str: continue

        trips = get_response(f"/schedule/{schedule_str}")["trips"]
        departures.extend(trips)

    return departures

def get_board_lines():
    departures = get_departures()
    now = time.time()

    lines = []

    for trip in departures[:3]:
        dt_s = trip["arrivalTime"] - now
        time_until = str(datetime.timedelta(seconds=dt_s))[:-10]
        lines.append((
            trip['routeName'],
            trip['headsign'],
            time_until
        ))

    return lines




def main():
    departures = get_departures()
    now = time.time()

    for trip in departures:
        dt_s = trip["arrivalTime"] - now
        time_until = str(datetime.timedelta(seconds=dt_s))[:-10]
        print(f"{trip['routeName']} {trip['headsign']} in {time_until}")

    for trip in departures[:3]:
        dt_s = trip["arrivalTime"] - now
        time_until = str(datetime.timedelta(seconds=dt_s))[:-10]
        print([
            trip['routeName'],
            trip['headsign'],
            time_until
        ])

    print(get_board_lines())


if __name__ == "__main__":
    main()