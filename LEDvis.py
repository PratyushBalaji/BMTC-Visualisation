import requests
import matplotlib.pyplot as plt

# --- Config ---
SEARCH_ROUTE_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchRoute_v2"
ROUTE_DETAILS_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchByRouteDetails_v4"
WIDTH = 128
HEIGHT = 128
PADDING = 2  # LED padding

# Normalize using shared bounding box + padding
def normalize_coords(stops, up_buses, down_buses, width, height, pad=2):
    combined = stops + up_buses + down_buses
    lats = [s['centerlat'] for s in combined]
    lons = [s['centerlong'] for s in combined]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    def normalize(lat, lon):
        x = int((lon - min_lon) / (max_lon - min_lon) * (width - 1 - 2 * pad)) + pad
        y = int((lat - min_lat) / (max_lat - min_lat) * (height - 1 - 2 * pad)) + pad
        return x, height - 1 - y  # Flip Y

    stop_coords = [normalize(s['centerlat'], s['centerlong']) for s in stops]
    up_coords = [normalize(s['centerlat'], s['centerlong']) for s in up_buses]
    down_coords = [normalize(s['centerlat'], s['centerlong']) for s in down_buses]
    return stop_coords, up_coords, down_coords

# Prompt user for route search
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

# Fetch route details and plot
def plot_route(route_id, route_name):
    headers = {"lan": "en", "deviceType": "WEB"}
    body = {"routeid": route_id, "servicetypeid": 0}
    resp = requests.post(ROUTE_DETAILS_URL, headers=headers, json=body).json()

    up_stops = resp.get("up", {}).get("data", [])
    up_buses = resp.get("up", {}).get("mapData", [])
    down_buses = resp.get("down", {}).get("mapData", [])

    if not up_stops:
        print("No stop data available.")
        return

    stops, up_leds, down_leds = normalize_coords(up_stops, up_buses, down_buses, WIDTH, HEIGHT, PADDING)

    # Plotting
    plt.figure(figsize=(6, 6))
    if stops:
        plt.scatter(*zip(*stops), c='blue', label='Stops')
    if up_leds:
        plt.scatter(*zip(*up_leds), c='red', label='Up Buses')
    if down_leds:
        plt.scatter(*zip(*down_leds), c='green', label='Down Buses')
    plt.title(f"Route Map for {route_name} on {WIDTH}x{HEIGHT} Grid")
    plt.xlim(0, WIDTH)
    plt.ylim(0, HEIGHT)
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.legend()
    plt.show()

# --- Main Loop ---
def main():
    while True:
        selected = search_route()
        if selected is None:
            print("Goodbye!")
            break
        route_name, route_id = selected
        print(f"\nFetching route map for: {route_name}")
        plot_route(route_id, route_name)

if __name__ == "__main__":
    main()
