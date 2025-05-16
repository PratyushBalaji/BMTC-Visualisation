import requests

SEARCH_ROUTE_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchRoute_v2"
ROUTE_DETAILS_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchByRouteDetails_v4"
TRIP_DETAILS_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/VehicleTripDetails_v2"
PATH_DETAILS_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/GetPathDetails"

# Prompt user for bus route
def search_route():
    while True:
        user_input = input("Enter bus route (or type 'exit'): ").strip()
        if user_input.lower() == "exit":
            return None

        headers = {"Content-Type": "application/json", "lan": "en"}
        body = {"routetext": user_input}
        resp = requests.post(SEARCH_ROUTE_URL, headers=headers, json=body).json()

        if not resp["data"]:
            print("No Records Found.\n")
            continue

        print("\nMatching routes:")
        for idx, route in enumerate(resp["data"], 1):
            print(f"{idx}. {route['routeno']}")
        print("0. Search again\n")

        try:
            selection = int(input("Select a route number: "))
            if selection == 0:
                continue
            selected = resp["data"][selection - 1]
            return selected["routeno"], selected["routeparentid"]
        except (ValueError, IndexError):
            print("Invalid selection. Try again.\n")

# Get route info and select a live vehicle
def get_vehicle_id(route_id):
    headers = {"lan": "en", "deviceType": "WEB"}
    body = {"routeid": route_id, "servicetypeid": 0}
    resp = requests.post(ROUTE_DETAILS_URL, headers=headers, json=body).json()

    up_buses = resp.get("up", {}).get("mapData", [])
    down_buses = resp.get("down", {}).get("mapData", [])
    buses = up_buses + down_buses

    if not buses:
        print("No live buses found.")
        return None

    print("\nLive Buses:")
    for idx, bus in enumerate(buses, 1):
        print(f"{idx}. {bus['vehiclenumber']} (Vehicle ID: {bus['vehicleid']})")

    try:
        selection = int(input("Select a vehicle to track: "))
        selected = buses[selection - 1]
        return selected["vehicleid"]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

# Get trip data using vehicle ID
def get_trip_stops(vehicle_id):
    body = {"vehicleId": vehicle_id}
    resp = requests.post(TRIP_DETAILS_URL, json=body).json()
    stops = resp.get("RouteDetails", [])
    if not stops:
        print("No trip data found.")
        return None

    print("\nStops in current trip:")
    for idx, stop in enumerate(stops, 1):
        name = stop.get("stationname", "Unknown")
        sid = stop.get("stationid", "?")
        sched = stop.get("sch_arrivaltime", "")
        print(f"{idx}. {name} (ID: {sid}) — Scheduled: {sched}")

    return stops

# Prompt for source/destination from stop list
def select_trip_segment(stops):
    try:
        src = int(input("Select source stop number: ")) - 1
        dst = int(input("Select destination stop number: ")) - 1
        return stops[src]["stationid"], stops[dst]["stationid"], stops[src]["tripid"]
    except (ValueError, IndexError):
        print("Invalid input.")
        return None

# Call GetPathDetails with tripId and stop IDs
def get_path_details(from_id, to_id, trip_id):
    body = {"data": [{"fromStationId": from_id, "toStationId": to_id, "tripId": trip_id}]}
    resp = requests.post(PATH_DETAILS_URL, headers={"Content-Type": "application/json", "lan": "en"}, json=body).json()
    path = resp.get("data", [])
    print("\n Path Details:")
    for stop in path:
        print(f"{stop['stationName']} at {stop['sch_arrivaltime']}")
    return path

# --- Main Flow ---
def main():
    result = search_route()
    if result is None:
        print("Goodbye!")
        return

    route_name, route_id = result
    print(f"\nRoute Selected: {route_name} (ID: {route_id})")

    vehicle_id = get_vehicle_id(route_id)
    if not vehicle_id:
        return

    trip_stops = get_trip_stops(vehicle_id)
    if not trip_stops:
        return

    segment = select_trip_segment(trip_stops)
    if not segment:
        return

    from_id, to_id, trip_id = segment
    get_path_details(from_id, to_id, trip_id)

if __name__ == "__main__":
    main()
