import datetime
import requests
import time

base = "https://tt.horner.tj"

def get_response(request):
    response = requests.get(base + request)
    response.raise_for_status()
    data = response.json()
    return data

request = "/stops/within/-72.527109,42.386394,-72.525301,42.387728"
response = requests.get(base + request)
response.raise_for_status()
data = response.json()
print(data)


request = "/stops/pvta:73/routes"
data = get_response(request)
for route in data:
    print(f"{route['name']} towards {route['headsigns']}")

request = "/schedule/pvta:38,pvta:73;pvta:B43,pvta:73;pvta:943,pvta:73;pvta:B79,pvta:73"
data = get_response(request)
for trip in data['trips']:
    dt_s = trip['arrivalTime'] - time.time()
    print(f"{trip['routeName']} {trip['headsign']} in {dt_s}s or {str(datetime.timedelta(seconds=dt_s))[:-10]}")